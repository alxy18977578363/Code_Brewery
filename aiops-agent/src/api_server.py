"""Local HTTP API for submitting and analyzing AIOps observations."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.analysis_service import (
    ObservationValidationError,
    analyze_observation,
    validate_and_sanitize_observation,
)
from src.detect_anomalies import detect_case
from src.local_collector import collect_local_observation
from src.freeaiops_adapter import FreeAiOpsAdapter
from src.model_client import ModelClientError, OpenAICompatibleClient
from src.result_store import ResultStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "runtime" / "aiops.db"


class AnalyzeRequest(BaseModel):
    observation_id: str = Field(min_length=1, max_length=128)
    use_model: bool = False


class QuickAnalyzeRequest(BaseModel):
    observation: dict[str, Any]
    use_model: bool = False


class CollectNowRequest(BaseModel):
    use_model: bool = False


class AiAskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    include_latest: bool = True
    analysis_id: str | None = Field(default=None, min_length=1, max_length=128)


class FaultDetectionRequest(BaseModel):
    observation: dict[str, Any]


class DiagnosticReportRequest(BaseModel):
    analysis_ids: list[str] = Field(min_length=1, max_length=50)


def _run_analysis_pipeline(
    app: FastAPI,
    observation: dict[str, Any],
    observation_id: str,
    use_model: bool,
    project_root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the FreeAiOps-aware observation -> event -> analysis pipeline.

    Normal observations remain local.  When T4 detects an abnormal signal and
    FreeAiOps is online, the complete observation (metrics and logs) is pushed
    into FreeAiOps' MySQL-backed compatibility event envelope, read back, and
    only then passed to T5/LLM.  This avoids flooding FreeAiOps during the
    one-second monitoring mode with healthy samples.
    """

    adapter = app.state.freeaiops
    health = adapter.check_health()
    freeaiops: dict[str, Any] = dict(health)
    event: dict[str, Any] = {"status": "skipped", "reason": "当前观测未检测到异常"}
    analysis_input = observation
    used_freeaiops_event = False
    try:
        precheck = detect_case(observation)
    except Exception:
        precheck = None
    if isinstance(precheck, dict) and precheck.get("result", {}).get("label") == "abnormal":
        evidence = precheck.get("evidence", {})
        event_key = json.dumps({
            "service": observation.get("service"),
            "metrics": sorted(item.get("name") for item in evidence.get("metrics", []) if item.get("operator") == ">"),
            "logs": sorted(item.get("message") for item in evidence.get("logs", [])),
        }, ensure_ascii=False, sort_keys=True)
        if app.state.last_event_key == event_key:
            event = {
                "status": "deduplicated",
                "event_id": app.state.last_event_id,
                "reason": "同一异常指纹已上报，等待状态变化",
            }
        elif health.get("status") == "online" and callable(getattr(adapter, "publish_event", None)):
            event = adapter.publish_event(observation, precheck, observation_id)
            if event.get("status") == "published":
                app.state.last_event_key = event_key
                app.state.last_event_id = event.get("event_id")
            if event.get("status") == "published" and callable(getattr(adapter, "retrieve_event", None)):
                retrieved = adapter.retrieve_event(event.get("event_id", ""))
                if retrieved and isinstance(retrieved.get("event"), dict):
                    analysis_input = retrieved["event"].get("observation") or observation
                    used_freeaiops_event = True
                    event["retrieval_status"] = "retrieved"
                    event["retrieved_event"] = retrieved.get("event")
                else:
                    event["retrieval_status"] = "not_found"
        else:
            event = {
                "status": "skipped",
                "reason": "FreeAiOps 离线，异常事件暂不推送",
                "health_status": health.get("status"),
            }
    else:
        app.state.last_event_key = None
        app.state.last_event_id = None
    analysis = analyze_observation(analysis_input, use_model=use_model, project_root=project_root)
    freeaiops["event"] = event
    freeaiops["pipeline"] = {
        "observation_pushed": event.get("status") == "published",
        "event_retrieved": event.get("retrieval_status") == "retrieved",
        "analysis_source": "freeaiops-event" if used_freeaiops_event else "agent-observation",
    }
    return analysis, freeaiops


def create_app(database_path: Path | None = None) -> FastAPI:
    """Create an app instance; an alternate database path makes tests isolated."""

    app = FastAPI(title="AIOps Analysis API", version="1.0.0")
    app.state.store = ResultStore(database_path or DEFAULT_DATABASE_PATH)
    app.state.freeaiops = FreeAiOpsAdapter()
    app.state.last_event_key = None
    app.state.last_event_id = None
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "aiops-analysis-api", "storage": "sqlite"}

    @app.post("/api/observations", status_code=201)
    def create_observation(observation: dict[str, Any] = Body(...)) -> dict[str, str]:
        try:
            clean_observation = validate_and_sanitize_observation(observation)
        except ObservationValidationError as exc:
            raise HTTPException(status_code=422, detail={"errors": exc.errors}) from exc
        metadata = app.state.store.save_observation(clean_observation)
        return {**metadata, "case_id": clean_observation["case_id"]}

    @app.post("/api/analyze", status_code=201)
    def create_analysis(request: AnalyzeRequest) -> dict[str, Any]:
        observation = app.state.store.get_observation(request.observation_id)
        if observation is None:
            raise HTTPException(status_code=404, detail="observation_id 不存在")
        analysis, freeaiops = _run_analysis_pipeline(
            app, observation, request.observation_id, request.use_model, PROJECT_ROOT
        )
        metadata = app.state.store.save_analysis(
            request.observation_id, analysis, request.use_model, freeaiops=freeaiops
        )
        return {
            **metadata,
            "observation_id": request.observation_id,
            "freeaiops": freeaiops,
            "analysis": analysis,
        }

    @app.post("/api/analyze-now", status_code=201)
    def analyze_now(request: QuickAnalyzeRequest) -> dict[str, Any]:
        """Submit and analyze one observation in a single user-facing operation."""

        try:
            observation = validate_and_sanitize_observation(request.observation)
        except ObservationValidationError as exc:
            raise HTTPException(status_code=422, detail={"errors": exc.errors}) from exc
        observation_metadata = app.state.store.save_observation(observation)
        analysis, freeaiops = _run_analysis_pipeline(
            app, observation, observation_metadata["observation_id"], request.use_model, PROJECT_ROOT
        )
        analysis_metadata = app.state.store.save_analysis(
            observation_metadata["observation_id"], analysis, request.use_model, freeaiops=freeaiops
        )
        return {
            **analysis_metadata,
            **observation_metadata,
            "freeaiops": freeaiops,
            "analysis": analysis,
        }

    @app.post("/api/fault-detection", status_code=201)
    def fault_detection(request: FaultDetectionRequest) -> dict[str, Any]:
        """Receive one observation and return a compact current-state detection."""

        try:
            observation = validate_and_sanitize_observation(request.observation)
        except ObservationValidationError as exc:
            raise HTTPException(status_code=422, detail={"errors": exc.errors}) from exc
        observation_metadata = app.state.store.save_observation(observation)
        analysis, freeaiops = _run_analysis_pipeline(
            app, observation, observation_metadata["observation_id"], False, PROJECT_ROOT
        )
        analysis_metadata = app.state.store.save_analysis(
            observation_metadata["observation_id"], analysis, False, freeaiops=freeaiops
        )
        report = {
            "report_type": "fault_detection",
            "report_version": "1.0",
            "generated_at": analysis_metadata["completed_at"],
            "observation_id": observation_metadata["observation_id"],
            "analysis_id": analysis_metadata["analysis_id"],
            "service": observation.get("service"),
            "detection": analysis["result"],
            "evidence": analysis["evidence"],
            "root_causes": analysis["root_causes"],
            "recommendations": analysis["recommendations"],
            "safety": analysis["safety"],
            "performance": analysis["performance"],
            "freeaiops": freeaiops,
        }
        return {
            **analysis_metadata,
            **observation_metadata,
            "observation": observation,
            "analysis": analysis,
            "report": report,
        }

    @app.post("/api/diagnostic-report", status_code=200)
    def diagnostic_report(request: DiagnosticReportRequest) -> dict[str, Any]:
        """Summarize a user-selected window of historical analyses."""

        records = []
        missing = []
        for analysis_id in request.analysis_ids:
            record = app.state.store.get_analysis(analysis_id)
            if record is None:
                missing.append(analysis_id)
            else:
                records.append(record)
        if missing:
            raise HTTPException(status_code=404, detail={"missing_analysis_ids": missing})
        records.sort(key=lambda item: item.get("completed_at", ""))
        abnormal_records = [item for item in records if item.get("analysis", {}).get("result", {}).get("label") == "abnormal"]
        metric_stats: dict[str, dict[str, Any]] = {}
        for record in records:
            metrics = record.get("observation", {}).get("metrics", {})
            evidence = record.get("analysis", {}).get("evidence", {}).get("metrics", [])
            thresholds = {item.get("name"): item.get("threshold") for item in evidence if item.get("name")}
            for name, value in metrics.items():
                if not isinstance(value, (int, float)):
                    continue
                item = metric_stats.setdefault(name, {"name": name, "values": [], "threshold": thresholds.get(name), "abnormal_count": 0})
                item["values"].append(value)
                threshold = item.get("threshold")
                if threshold is not None and value > threshold:
                    item["abnormal_count"] += 1
        metric_summary = []
        for item in metric_stats.values():
            values = item["values"]
            threshold = item.get("threshold")
            metric_summary.append({
                "name": item["name"],
                "average": round(sum(values) / len(values), 2),
                "maximum": max(values),
                "minimum": min(values),
                "threshold": threshold,
                "abnormal_count": item["abnormal_count"],
                "samples": len(values),
            })
        metric_summary.sort(key=lambda item: (item["abnormal_count"], item["maximum"]), reverse=True)
        causes = []
        recommendations = []
        logs = []
        for record in abnormal_records:
            analysis = record.get("analysis", {})
            causes.extend(analysis.get("root_causes", []))
            recommendations.extend(analysis.get("recommendations", []))
            logs.extend(record.get("observation", {}).get("logs", []))
        unique_causes = []
        for item in causes:
            text = item.get("cause") if isinstance(item, dict) else str(item)
            if text and text not in unique_causes:
                unique_causes.append(text)
        unique_recommendations = []
        for item in recommendations:
            text = item.get("action") if isinstance(item, dict) else str(item)
            if text and text not in unique_recommendations:
                unique_recommendations.append(text)
        report = {
            "report_type": "historical_diagnostic",
            "report_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "source_analysis_ids": request.analysis_ids,
            "period": {"start": records[0]["completed_at"], "end": records[-1]["completed_at"]},
            "summary": {"sample_count": len(records), "abnormal_count": len(abnormal_records), "abnormal_rate_percent": round(len(abnormal_records) / len(records) * 100, 1)},
            "metrics": metric_summary,
            "logs": logs[-20:],
            "root_causes": unique_causes[:8],
            "recommendations": unique_recommendations[:8],
            "safety": {"auto_remediation_allowed": False, "actions_taken": []},
        }
        return {"report": report, "items": records}

    @app.get("/api/freeaiops/status")
    def freeaiops_status() -> dict[str, Any]:
        return app.state.freeaiops.check_health()

    @app.get("/api/freeaiops/events")
    def freeaiops_events(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
        """Expose the events currently managed by FreeAiOps to the dashboard."""

        reader = getattr(app.state.freeaiops, "list_events", None)
        if not callable(reader):
            return {"status": "unsupported", "count": 0, "events": []}
        return reader(limit=limit)

    @app.post("/api/ai/ask")
    def ai_ask(request: AiAskRequest) -> dict[str, Any]:
        """Answer a user question through the server-side model configuration."""

        client = OpenAICompatibleClient.from_project(PROJECT_ROOT, timeout=30.0)
        if client is None:
            raise HTTPException(status_code=503, detail="尚未配置可用的模型接口，请检查项目 .env")
        context: dict[str, Any] | None = None
        if request.include_latest:
            latest = (
                app.state.store.get_analysis(request.analysis_id)
                if request.analysis_id
                else app.state.store.latest_analysis()
            )
            if request.analysis_id and latest is None:
                raise HTTPException(status_code=404, detail="analysis_id 不存在")
            if latest:
                context = {
                    "observation": latest.get("observation"),
                    "analysis": latest.get("analysis"),
                    "freeaiops": latest.get("freeaiops"),
                }
        try:
            answer, latency_ms = client.answer(request.question.strip(), context=context)
        except ModelClientError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {
            "answer": answer,
            "model_name": client.model,
            "latency_ms": latency_ms,
            "context_used": context is not None,
            "safety": {"auto_remediation_allowed": False, "actions_taken": []},
        }

    @app.get("/api/local-observation")
    def local_observation() -> dict[str, Any]:
        observation, collection = collect_local_observation(PROJECT_ROOT)
        return {"observation": observation, "collection": collection}

    @app.post("/api/collect-now", status_code=201)
    def collect_now(request: CollectNowRequest) -> dict[str, Any]:
        """Collect approved local data and analyze it without browser file access."""

        observation, collection = collect_local_observation(PROJECT_ROOT)
        observation_metadata = app.state.store.save_observation(observation)
        analysis, freeaiops = _run_analysis_pipeline(
            app, observation, observation_metadata["observation_id"], request.use_model, PROJECT_ROOT
        )
        analysis_metadata = app.state.store.save_analysis(
            observation_metadata["observation_id"], analysis, request.use_model, freeaiops=freeaiops
        )
        return {
            **analysis_metadata,
            **observation_metadata,
            "observation": observation,
            "collection": collection,
            "freeaiops": freeaiops,
            "analysis": analysis,
        }

    @app.get("/api/results/latest")
    def latest_result() -> dict[str, Any]:
        result = app.state.store.latest_analysis()
        if result is None:
            raise HTTPException(status_code=404, detail="暂无分析结果")
        return result

    @app.get("/api/results/{analysis_id}")
    def get_result(analysis_id: str) -> dict[str, Any]:
        result = app.state.store.get_analysis(analysis_id)
        if result is None:
            raise HTTPException(status_code=404, detail="analysis_id 不存在")
        return result

    @app.get("/api/results")
    def list_results(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
        return {"items": app.state.store.list_analyses(limit)}

    @app.get("/", include_in_schema=False)
    def home() -> RedirectResponse:
        return RedirectResponse(url="/web/")

    # Serve the user-facing dashboard and its read-only evaluation data from
    # this same local process, so normal use needs only one terminal window.
    app.mount("/web", StaticFiles(directory=PROJECT_ROOT / "web", html=True), name="web")
    app.mount("/eval", StaticFiles(directory=PROJECT_ROOT / "eval"), name="eval")

    return app


app = create_app()
