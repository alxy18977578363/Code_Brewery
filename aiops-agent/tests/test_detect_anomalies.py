from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from src.detect_anomalies import detect_case, detect_document


ROOT = Path(__file__).resolve().parents[1]


class DetectAnomaliesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads((ROOT / "eval" / "cases.json").read_text(encoding="utf-8"))

    def test_all_evaluation_labels_match_rule_detector(self) -> None:
        outputs = detect_document(self.cases)
        self.assertEqual(len(outputs), 20)
        for case, output in zip(self.cases, outputs):
            self.assertEqual(output["result"]["label"], case["expected_label"], case["case_id"])

    def test_cpu_threshold_and_evidence(self) -> None:
        case = copy.deepcopy(self.cases[1])
        case["metrics"]["cpu_usage_percent"] = 80.1
        output = detect_case(case)
        self.assertEqual(output["result"]["label"], "abnormal")
        self.assertEqual(output["result"]["severity"], "low")
        self.assertTrue(any(item["name"] == "cpu_usage_percent" for item in output["evidence"]["metrics"]))

    def test_boundary_value_is_not_abnormal(self) -> None:
        case = copy.deepcopy(self.cases[1])
        case["metrics"]["cpu_usage_percent"] = 80
        output = detect_case(case)
        self.assertEqual(output["result"]["label"], "normal")

    def test_memory_threshold_allows_sustained_90_percent_usage(self) -> None:
        case = copy.deepcopy(self.cases[1])
        case["metrics"]["memory_usage_percent"] = 90
        output = detect_case(case)
        self.assertEqual(output["result"]["label"], "normal")
        self.assertFalse(any(item["name"] == "memory_usage_percent" for item in output["evidence"]["metrics"]))

    def test_memory_above_95_percent_is_abnormal(self) -> None:
        case = copy.deepcopy(self.cases[1])
        case["metrics"]["memory_usage_percent"] = 95.1
        output = detect_case(case)
        self.assertEqual(output["result"]["label"], "abnormal")
        self.assertTrue(any(item["name"] == "memory_usage_percent" for item in output["evidence"]["metrics"]))

    def test_error_log_is_signal_but_warn_is_supporting_evidence(self) -> None:
        normal_case = copy.deepcopy(self.cases[1])
        normal_case["logs"] = [
            {
                "timestamp": normal_case["observed_at"],
                "level": "WARN",
                "source": "application",
                "message": "slow background task",
            }
        ]
        normal_output = detect_case(normal_case)
        self.assertEqual(normal_output["result"]["label"], "normal")
        self.assertEqual(len(normal_output["evidence"]["logs"]), 1)

        error_case = copy.deepcopy(normal_case)
        error_case["logs"][0]["level"] = "ERROR"
        error_output = detect_case(error_case)
        self.assertEqual(error_output["result"]["label"], "abnormal")

    def test_null_metric_is_skipped_and_confidence_is_lower(self) -> None:
        case = copy.deepcopy(self.cases[1])
        case["metrics"]["memory_usage_percent"] = None
        output = detect_case(case)
        self.assertEqual(output["result"]["label"], "normal")
        self.assertEqual(output["result"]["confidence"], 0.65)
        missing = [item for item in output["evidence"]["metrics"] if item["operator"] == "missing"]
        self.assertEqual(len(missing), 1)

    def test_output_has_required_safety_and_performance_fields(self) -> None:
        output = detect_case(self.cases[0])
        self.assertEqual(output["schema_version"], "1.0")
        self.assertFalse(output["safety"]["auto_remediation_allowed"])
        self.assertEqual(output["safety"]["actions_taken"], [])
        self.assertFalse(output["performance"]["model_used"])
        self.assertGreaterEqual(output["performance"]["latency_ms"], 0)
        self.assertEqual(output["root_causes"], [])
        self.assertEqual(output["recommendations"], [])

    def test_expected_label_is_not_copied_to_output(self) -> None:
        output = detect_case(self.cases[0])
        self.assertNotIn("expected_label", output)


if __name__ == "__main__":
    unittest.main()
