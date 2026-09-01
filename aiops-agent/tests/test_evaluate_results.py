from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from src.detect_anomalies import detect_document
from src.evaluate_results import EvaluationError, evaluate
from src.analyze_root_cause import analyze_document


ROOT = Path(__file__).resolve().parents[1]


class EvaluateResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads((ROOT / "eval" / "cases.json").read_text(encoding="utf-8"))
        cls.t4 = detect_document(cls.cases)
        cls.t5 = analyze_document(cls.t4)

    def test_twenty_cases_are_evaluated_with_full_accuracy(self) -> None:
        report = evaluate(self.cases, self.t4, self.t5)
        self.assertEqual(report["total_cases"], 20)
        self.assertEqual(report["correct_cases"], 20)
        self.assertEqual(report["incorrect_cases"], 0)
        self.assertEqual(report["accuracy"], 1.0)
        self.assertEqual(report["accuracy_percent"], 100.0)
        self.assertEqual(len(report["case_results"]), 20)

    def test_latency_statistics_are_calculated(self) -> None:
        report = evaluate(self.cases[:2], self.t4[:2], self.t5[:2])
        self.assertGreaterEqual(report["t4_latency_ms"]["average"], 0)
        self.assertGreaterEqual(report["t5_latency_ms"]["average"], 0)
        self.assertLessEqual(report["t4_latency_ms"]["minimum"], report["t4_latency_ms"]["maximum"])
        self.assertIn("median", report["t5_latency_ms"])

    def test_wrong_label_is_counted(self) -> None:
        t4 = copy.deepcopy(self.t4[:2])
        t4[0]["result"]["label"] = "normal"
        report = evaluate(self.cases[:2], t4)
        self.assertEqual(report["correct_cases"], 1)
        self.assertEqual(report["incorrect_cases"], 1)
        self.assertEqual(report["accuracy_percent"], 50.0)
        self.assertFalse(report["case_results"][0]["correct"])

    def test_case_id_matching_does_not_depend_on_order(self) -> None:
        report = evaluate(self.cases[:2], list(reversed(self.t4[:2])))
        self.assertEqual(report["accuracy_percent"], 100.0)
        self.assertEqual([item["case_id"] for item in report["case_results"]], ["case-001", "case-002"])

    def test_missing_case_is_rejected(self) -> None:
        with self.assertRaises(EvaluationError):
            evaluate(self.cases[:2], self.t4[:1])

    def test_invalid_latency_is_rejected(self) -> None:
        t4 = copy.deepcopy(self.t4[:1])
        t4[0]["performance"]["latency_ms"] = "fast"
        with self.assertRaises(EvaluationError):
            evaluate(self.cases[:1], t4)

    def test_t4_only_mode_has_no_t5_stats(self) -> None:
        report = evaluate(self.cases[:1], self.t4[:1])
        self.assertIsNone(report["t5_latency_ms"])
        self.assertIsNone(report["model_usage"])
        self.assertNotIn("t5_latency_ms", report["case_results"][0])


if __name__ == "__main__":
    unittest.main()
