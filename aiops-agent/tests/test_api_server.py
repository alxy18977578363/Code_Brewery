from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from src.api_server import create_app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ApiServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        app = create_app(Path(self.temp_dir.name) / "api.db")
        app.state.freeaiops = MagicMock()
        app.state.freeaiops.check_health.return_value = {
            "status": "offline",
            "base_url": "http://127.0.0.1:8080",
            "health_url": "http://127.0.0.1:8080/health",
            "checked_at": "2026-08-30T00:00:00+00:00",
            "http_status": None,
            "latency_ms": 0,
            "message": "test offline",
        }
        self.client = TestClient(app)
        cases = json.loads((PROJECT_ROOT / "eval" / "cases.json").read_text(encoding="utf-8"))
        self.normal_case = next(case for case in cases if case["expected_label"] == "normal")
        self.abnormal_case = next(case for case in cases if case["expected_label"] == "abnormal")

    def tearDown(self) -> None:
        self.client.close()
        self.temp_dir.cleanup()

    def _submit(self, case: dict) -> str:
        response = self.client.post("/api/observations", json=case)
        self.assertEqual(response.status_code, 201)
        return response.json()["observation_id"]

    def test_health(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_freeaiops_status_is_exposed(self) -> None:
        response = self.client.get("/api/freeaiops/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "offline")

    def test_ai_ask_requires_model_configuration(self) -> None:
        with patch("src.api_server.OpenAICompatibleClient.from_project", return_value=None):
            response = self.client.post("/api/ai/ask", json={"question": "如何理解当前内存指标？"})
        self.assertEqual(response.status_code, 503)

    def test_ai_ask_returns_answer_without_exposing_secret(self) -> None:
        client = MagicMock()
        client.model = "test-model"
        client.answer.return_value = ("建议先观察内存趋势，并人工确认高占用进程。", 12.3)
        with patch("src.api_server.OpenAICompatibleClient.from_project", return_value=client):
            response = self.client.post("/api/ai/ask", json={"question": "如何排查内存压力？"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("建议先观察", response.json()["answer"])
        self.assertNotIn("api_key", response.text.lower())

    def test_ai_ask_can_use_selected_analysis_context(self) -> None:
        client = MagicMock()
        client.model = "test-model"
        client.answer.return_value = ("已根据所选记录回答。", 8.1)
        observation_id = self._submit(self.abnormal_case)
        analysis_response = self.client.post("/api/analyze", json={"observation_id": observation_id})
        analysis_id = analysis_response.json()["analysis_id"]
        with patch("src.api_server.OpenAICompatibleClient.from_project", return_value=client):
            response = self.client.post(
                "/api/ai/ask",
                json={"question": "解释这条记录", "analysis_id": analysis_id, "include_latest": True},
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["context_used"])
        context = client.answer.call_args.kwargs["context"]
        self.assertEqual(context["analysis"]["case_id"], self.abnormal_case["case_id"])

    def test_dashboard_is_served_by_the_api_process(self) -> None:
        home = self.client.get("/", follow_redirects=False)
        self.assertEqual(home.status_code, 307)
        self.assertEqual(home.headers["location"], "/web/")
        dashboard = self.client.get("/web/")
        self.assertEqual(dashboard.status_code, 200)
        self.assertIn("实时监控", dashboard.text)
        self.assertIn("历史分析", dashboard.text)
        self.assertIn("系统状态", dashboard.text)
        cases = self.client.get("/eval/cases.json")
        self.assertEqual(cases.status_code, 200)

    def test_invalid_observation_returns_422(self) -> None:
        response = self.client.post("/api/observations", json={"case_id": "invalid"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("errors", response.json()["detail"])

    def test_normal_analysis_is_saved_without_evaluation_label(self) -> None:
        observation_id = self._submit(self.normal_case)
        response = self.client.post("/api/analyze", json={"observation_id": observation_id})
        self.assertEqual(response.status_code, 201)
        payload = response.json()

        self.assertEqual(payload["analysis"]["result"]["label"], "normal")
        self.assertFalse(payload["analysis"]["performance"]["model_used"])
        self.assertEqual(payload["analysis"]["root_causes"], [])
        self.assertFalse(payload["analysis"]["safety"]["auto_remediation_allowed"])
        self.assertNotIn("expected_label", json.dumps(payload, ensure_ascii=False))

    def test_abnormal_analysis_has_safe_recommendations_and_history(self) -> None:
        observation_id = self._submit(self.abnormal_case)
        created = self.client.post("/api/analyze", json={"observation_id": observation_id})
        self.assertEqual(created.status_code, 201)
        payload = created.json()
        analysis = payload["analysis"]

        self.assertEqual(analysis["result"]["label"], "abnormal")
        self.assertTrue(analysis["root_causes"])
        self.assertTrue(analysis["recommendations"])
        self.assertTrue(all(item["requires_approval"] for item in analysis["recommendations"]))

        latest = self.client.get("/api/results/latest")
        self.assertEqual(latest.status_code, 200)
        self.assertEqual(latest.json()["analysis_id"], payload["analysis_id"])
        self.assertEqual(latest.json()["freeaiops"]["status"], "offline")
        self.assertEqual(latest.json()["observation"]["service"]["name"], "demo-service")
        history = self.client.get("/api/results?limit=20")
        self.assertEqual(history.status_code, 200)
        self.assertEqual(len(history.json()["items"]), 1)

    def test_quick_analysis_submits_and_analyzes_in_one_request(self) -> None:
        response = self.client.post(
            "/api/analyze-now",
            json={"observation": self.abnormal_case, "use_model": False},
        )
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertTrue(payload["observation_id"].startswith("obs-"))
        self.assertTrue(payload["analysis_id"].startswith("analysis-"))
        self.assertEqual(payload["analysis"]["result"]["label"], "abnormal")
        self.assertEqual(payload["freeaiops"]["status"], "offline")
        self.assertNotIn("expected_label", json.dumps(payload, ensure_ascii=False))

    def test_fault_detection_returns_structured_report(self) -> None:
        response = self.client.post(
            "/api/fault-detection",
            json={"observation": self.abnormal_case},
        )
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["report"]["report_type"], "fault_detection")
        self.assertEqual(payload["report"]["detection"]["label"], "abnormal")
        self.assertTrue(payload["report"]["evidence"]["metrics"])
        self.assertFalse(payload["report"]["safety"]["auto_remediation_allowed"])
        self.assertNotIn("expected_label", json.dumps(payload, ensure_ascii=False))

    def test_collect_now_uses_server_side_local_collection(self) -> None:
        collection = {
            "metric_source": "local-machine",
            "log_source": "runtime/local_events.log",
            "log_status": "not_found",
            "log_events": 0,
            "unavailable_metrics": [],
        }
        with patch("src.api_server.collect_local_observation", return_value=(self.normal_case, collection)):
            response = self.client.post("/api/collect-now", json={"use_model": False})
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["collection"], collection)
        self.assertEqual(payload["observation"]["case_id"], self.normal_case["case_id"])
        self.assertEqual(payload["analysis"]["result"]["label"], "normal")

    def test_unknown_observation_and_analysis_return_404(self) -> None:
        missing_observation = self.client.post("/api/analyze", json={"observation_id": "obs-missing"})
        self.assertEqual(missing_observation.status_code, 404)
        missing_analysis = self.client.get("/api/results/analysis-missing")
        self.assertEqual(missing_analysis.status_code, 404)
