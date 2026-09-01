"""T5 root-cause analysis and safe recommendations.

The module consumes T4 output, builds explainable candidate causes, optionally
asks an OpenAI-compatible model to refine them, validates the model JSON, and
falls back to deterministic safe advice when the model is unavailable.

Usage:
    python src/analyze_root_cause.py eval/results.json --output eval/t5_results.json
    python src/analyze_root_cause.py eval/results.json --use-model --output eval/t5_results.json
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Any

# Allow both ``python -m src.analyze_root_cause`` and the documented direct
# invocation ``python src/analyze_root_cause.py``.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.model_client import (
    ModelClientError,
    OpenAICompatibleClient,
    extract_json_object,
)


FORBIDDEN_PATTERNS = re.compile(
    r"(?:rm\s+-rf|drop\s+(?:database|table)|(?:shutdown|reboot)\b|systemctl\s+(?:stop|disable|restart)|format\s+[a-z]:|del\s+/[sq]|kubectl\s+delete|docker\s+rm|kill\s+-9|restart\s+(?:the\s+)?(?:production\s+)?service|stop\s+(?:the\s+)?(?:production\s+)?service|重启生产|删除数据库|删除文件|自动修复)",
    re.IGNORECASE,
)
PRIORITIES = {"P1", "P2", "P3"}


def _metric_names(output: dict[str, Any]) -> set[str]:
    metrics = output.get("evidence", {}).get("metrics", [])
    return {
        item.get("name")
        for item in metrics
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }


def _active_metric_names(output: dict[str, Any]) -> set[str]:
    metrics = output.get("evidence", {}).get("metrics", [])
    return {
        item.get("name")
        for item in metrics
        if isinstance(item, dict)
        and item.get("operator") == ">"
        and isinstance(item.get("name"), str)
    }


def _log_refs(output: dict[str, Any]) -> set[str]:
    logs = output.get("evidence", {}).get("logs", [])
    return {f"logs[{index}]" for index, _ in enumerate(logs)}


def _refs(output: dict[str, Any], *names: str, include_logs: bool = False) -> list[str]:
    available_metrics = _metric_names(output)
    refs = [f"metrics.{name}" for name in names if name in available_metrics]
    if include_logs and _log_refs(output):
        logs = output.get("evidence", {}).get("logs", [])
        for index, log in enumerate(logs):
            if isinstance(log, dict) and log.get("level") == "ERROR":
                refs.append(f"logs[{index}]")
    return list(dict.fromkeys(refs))


def _evidence_names(output: dict[str, Any]) -> set[str]:
    names = {f"metrics.{name}" for name in _metric_names(output)}
    names.update(_log_refs(output))
    return names


def build_candidate_causes(output: dict[str, Any]) -> list[dict[str, Any]]:
    """Create explainable candidate causes from T4 evidence."""

    metrics = _active_metric_names(output)
    logs = output.get("evidence", {}).get("logs", [])
    has_error_log = any(
        isinstance(log, dict) and log.get("level") == "ERROR" for log in logs
    )
    candidates: list[dict[str, Any]] = []

    def add(cause: str, confidence: float, evidence_refs: list[str]) -> None:
        if not evidence_refs or any(item["cause"] == cause for item in candidates):
            return
        candidates.append(
            {
                "cause": cause,
                "confidence": round(confidence, 2),
                "evidence_refs": evidence_refs,
            }
        )

    if "db_connection_usage_percent" in metrics and "response_time_ms" in metrics:
        add(
            "数据库连接池紧张或慢查询导致请求等待数据库连接",
            0.86,
            _refs(output, "db_connection_usage_percent", "response_time_ms", include_logs=True),
        )
    elif "db_connection_usage_percent" in metrics:
        add(
            "数据库连接池可能接近耗尽，或存在连接泄漏",
            0.80,
            _refs(output, "db_connection_usage_percent", include_logs=True),
        )

    if "cpu_usage_percent" in metrics and "load_1m" in metrics:
        add(
            "计算资源可能饱和，或服务并发压力过高",
            0.80,
            _refs(output, "cpu_usage_percent", "load_1m"),
        )
    elif "cpu_usage_percent" in metrics:
        add(
            "服务存在计算密集任务或 CPU 并发压力",
            0.74,
            _refs(output, "cpu_usage_percent"),
        )
    elif "load_1m" in metrics:
        add(
            "系统负载过高，可能存在任务排队或并发压力",
            0.70,
            _refs(output, "load_1m"),
        )

    if "memory_usage_percent" in metrics:
        add(
            "服务存在内存压力，可能与缓存过大或内存增长有关",
            0.74,
            _refs(output, "memory_usage_percent"),
        )
    if "disk_usage_percent" in metrics:
        add(
            "磁盘空间可能被日志、临时文件或业务数据持续占用",
            0.78,
            _refs(output, "disk_usage_percent"),
        )
    if "response_time_ms" in metrics and "db_connection_usage_percent" not in metrics:
        add(
            "应用线程池、外部依赖或上游服务响应变慢",
            0.68,
            _refs(output, "response_time_ms"),
        )
    if "error_rate_percent" in metrics or has_error_log:
        refs = _refs(output, "error_rate_percent", include_logs=True)
        add(
            "应用组件或上游依赖发生失败，需要结合错误日志定位",
            0.72,
            refs,
        )
    if has_error_log and not candidates:
        add(
            "日志所指向的组件可能发生运行时故障",
            0.62,
            _refs(output, include_logs=True),
        )
    return candidates[:3]


def build_fallback_recommendations(output: dict[str, Any]) -> list[dict[str, Any]]:
    """Return safe, read-only investigation advice without model access."""

    metrics = _active_metric_names(output)
    logs = output.get("evidence", {}).get("logs", [])
    has_error_log = any(
        isinstance(log, dict) and log.get("level") == "ERROR" for log in logs
    )
    recommendations: list[dict[str, Any]] = []

    def add(priority: str, action: str, rationale: str) -> None:
        if any(item["action"] == action for item in recommendations):
            return
        recommendations.append(
            {
                "priority": priority,
                "action": action,
                "rationale": rationale,
                "requires_approval": True,
            }
        )

    if "db_connection_usage_percent" in metrics:
        add(
            "P1",
            "检查数据库连接池上限、活动连接、连接泄漏和慢查询",
            "数据库连接使用率已超过检测阈值",
        )
    if "error_rate_percent" in metrics or has_error_log:
        add(
            "P1",
            "检查应用错误日志、异常堆栈和上游依赖返回状态",
            "错误率或 ERROR 日志表明请求处理存在失败",
        )
    if "disk_usage_percent" in metrics:
        add(
            "P1",
            "检查占用空间最大的日志、临时文件和数据目录，并确认保留策略",
            "磁盘使用率已超过检测阈值",
        )
    if "cpu_usage_percent" in metrics or "load_1m" in metrics:
        add(
            "P2",
            "检查 CPU 占用最高的进程、线程和请求并发情况",
            "CPU 使用率或系统负载已超过检测阈值",
        )
    if "memory_usage_percent" in metrics:
        add(
            "P2",
            "检查内存增长趋势、缓存大小和进程内存占用",
            "内存使用率已超过检测阈值",
        )
    if "response_time_ms" in metrics:
        add(
            "P2",
            "检查接口耗时分布、线程池等待和外部依赖延迟",
            "响应时间已超过检测阈值",
        )
    return recommendations[:5]


def build_prompt(output: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    """Build a constrained prompt containing only T4 evidence."""

    context = {
        "case_id": output.get("case_id"),
        "service": output.get("service"),
        "result": output.get("result"),
        "evidence": output.get("evidence"),
        "candidate_causes": candidates,
    }
    encoded = json.dumps(context, ensure_ascii=False, indent=2)
    return f"""请根据以下 T4 异常检测结果，完成 T5 根因分析。输入只包含检测证据，不包含测试答案。

要求：
1. 只返回一个合法 JSON 对象，不要使用 Markdown 代码块，不要添加解释文字。
2. 只能返回 root_causes 和 recommendations 两个字段。
3. 最多返回 3 个可能根因和 5 个建议；根因必须是“可能原因”，不能把指标异常原样改写成原因。
4. 每个根因必须包含 cause、confidence（0 到 1）和 evidence_refs；引用只能来自输入中的 metrics.<名称> 或 logs[编号]。
5. 每个建议必须包含 priority（P1/P2/P3）、action、rationale 和 requires_approval；requires_approval 必须为 true。
6. 只给出人工检查或人工确认的安全建议，不要输出删除、停机、重启生产服务、修改系统服务或任何可直接执行的危险命令。
7. 如果证据不足，明确写出“不足以确定唯一根因”，不要编造不存在的组件。

输入：
{encoded}

输出结构：
{{"root_causes": [], "recommendations": []}}"""


def validate_model_result(result: Any, output: dict[str, Any]) -> list[str]:
    """Validate model JSON before merging it into the standard output."""

    errors: list[str] = []
    if not isinstance(result, dict):
        return ["模型结果必须是 JSON 对象"]
    if not isinstance(result.get("root_causes"), list):
        errors.append("root_causes 必须是数组")
    if not isinstance(result.get("recommendations"), list):
        errors.append("recommendations 必须是数组")
    if errors:
        return errors
    if len(result["root_causes"]) > 3:
        errors.append("根因数量不能超过 3 个")
    if len(result["recommendations"]) > 5:
        errors.append("建议数量不能超过 5 个")
    available_refs = _evidence_names(output)
    for index, cause in enumerate(result["root_causes"]):
        prefix = f"root_causes[{index}]"
        if not isinstance(cause, dict) or not isinstance(cause.get("cause"), str) or not cause["cause"].strip():
            errors.append(f"{prefix}.cause 必须是非空字符串")
            continue
        confidence = cause.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not math.isfinite(float(confidence)) or not 0 <= confidence <= 1:
            errors.append(f"{prefix}.confidence 必须在 0 到 1 之间")
        evidence_refs = cause.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs or not all(ref in available_refs for ref in evidence_refs):
            errors.append(f"{prefix}.evidence_refs 必须引用输入中的证据")
        if FORBIDDEN_PATTERNS.search(cause.get("cause", "")):
            errors.append(f"{prefix}.cause 包含不安全操作")
    for index, recommendation in enumerate(result["recommendations"]):
        prefix = f"recommendations[{index}]"
        if not isinstance(recommendation, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        if recommendation.get("priority") not in PRIORITIES:
            errors.append(f"{prefix}.priority 必须是 P1、P2 或 P3")
        for field in ("action", "rationale"):
            if not isinstance(recommendation.get(field), str) or not recommendation[field].strip():
                errors.append(f"{prefix}.{field} 必须是非空字符串")
        if recommendation.get("requires_approval") is not True:
            errors.append(f"{prefix}.requires_approval 必须为 true")
        text = f"{recommendation.get('action', '')} {recommendation.get('rationale', '')}"
        if FORBIDDEN_PATTERNS.search(text):
            errors.append(f"{prefix} 包含不安全操作")
    return errors


def _fallback_output(output: dict[str, Any], attempted_model: bool) -> dict[str, Any]:
    result = copy.deepcopy(output)
    result["root_causes"] = build_candidate_causes(result)
    result["recommendations"] = build_fallback_recommendations(result)
    if attempted_model:
        result["result"]["summary"] += "；模型分析不可用，已使用规则回退"
        result["performance"]["detector"] = "rule-v1-fallback"
    return result


def analyze_case(
    t4_output: dict[str, Any],
    client: OpenAICompatibleClient | Any = None,
    use_model: bool = False,
) -> dict[str, Any]:
    """Analyze one T4 output, optionally using a model with safe fallback."""

    started = time.perf_counter()
    result = copy.deepcopy(t4_output)
    result.setdefault("root_causes", [])
    result.setdefault("recommendations", [])
    label = result.get("result", {}).get("label")
    if label != "abnormal":
        result["root_causes"] = []
        result["recommendations"] = []
    else:
        candidates = build_candidate_causes(result)
        if use_model and client is not None:
            try:
                raw, _model_latency = client.complete(build_prompt(result, candidates))
                parsed = extract_json_object(raw) if isinstance(raw, str) else raw
                errors = validate_model_result(parsed, result)
                if errors:
                    raise ModelClientError("模型输出未通过安全格式校验")
                result["root_causes"] = parsed["root_causes"]
                result["recommendations"] = parsed["recommendations"]
                result["performance"]["detector"] = "rule-v1+llm-v1"
                result["performance"]["model_used"] = True
                result["performance"]["model_name"] = getattr(client, "model", None)
            except (ModelClientError, ValueError, TypeError, KeyError):
                result = _fallback_output(result, attempted_model=True)
        else:
            result = _fallback_output(result, attempted_model=False)
    base_latency = result.get("performance", {}).get("latency_ms", 0)
    if not isinstance(base_latency, (int, float)):
        base_latency = 0
    result["performance"]["latency_ms"] = round(
        float(base_latency) + (time.perf_counter() - started) * 1000, 3
    )
    return result


def analyze_document(
    document: Any,
    client: OpenAICompatibleClient | Any = None,
    use_model: bool = False,
) -> Any:
    if isinstance(document, list):
        return [analyze_case(item, client=client, use_model=use_model) for item in document]
    if isinstance(document, dict):
        return analyze_case(document, client=client, use_model=use_model)
    raise ValueError("T5 输入必须是 T4 JSON 对象或结果数组")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run T5 root-cause analysis")
    parser.add_argument("input", type=Path, help="T4 JSON output or array")
    parser.add_argument("--output", type=Path, help="optional output JSON path")
    parser.add_argument("--use-model", action="store_true", help="call the configured model for abnormal cases")
    parser.add_argument("--case-id", help="analyze only one case from an input array")
    parser.add_argument("--timeout", type=float, default=30.0, help="model request timeout in seconds")
    args = parser.parse_args(argv)

    client = None
    if args.use_model:
        client = OpenAICompatibleClient.from_project(Path(__file__).resolve().parents[1], timeout=args.timeout)
        if client is None:
            print("未找到完整模型配置，将使用规则回退。", file=sys.stderr)

    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        if args.case_id:
            if not isinstance(document, list):
                if document.get("case_id") != args.case_id:
                    raise ValueError(f"未找到案例：{args.case_id}")
            else:
                matches = [item for item in document if isinstance(item, dict) and item.get("case_id") == args.case_id]
                if not matches:
                    raise ValueError(f"未找到案例：{args.case_id}")
                document = matches[0]
        result = analyze_document(document, client=client, use_model=args.use_model)
        encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf-8")
        else:
            print(encoded, end="")
    except FileNotFoundError:
        print(f"文件不存在：{args.input}")
        return 2
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"T5 分析失败：{exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
