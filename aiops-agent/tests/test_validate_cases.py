from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from src.validate_cases import validate_case, validate_document


ROOT = Path(__file__).resolve().parents[1]


class ValidateCasesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads((ROOT / "eval" / "cases.json").read_text(encoding="utf-8"))

    def test_current_examples_are_valid(self) -> None:
        self.assertEqual(validate_document(self.cases, require_label=True), [])

    def test_runtime_case_may_omit_expected_label(self) -> None:
        case = copy.deepcopy(self.cases[0])
        del case["expected_label"]
        self.assertEqual(validate_case(case), [])

    def test_missing_metric_is_rejected(self) -> None:
        case = copy.deepcopy(self.cases[0])
        del case["metrics"]["cpu_usage_percent"]
        errors = validate_case(case)
        self.assertTrue(any("缺少指标：cpu_usage_percent" in error for error in errors))

    def test_metric_range_and_type_are_rejected(self) -> None:
        case = copy.deepcopy(self.cases[0])
        case["metrics"]["cpu_usage_percent"] = 101
        case["metrics"]["response_time_ms"] = "850ms"
        errors = validate_case(case)
        self.assertTrue(any("cpu_usage_percent 不能大于 100" in error for error in errors))
        self.assertTrue(any("response_time_ms 必须是数字或 null" in error for error in errors))

    def test_bad_log_and_timestamp_are_rejected(self) -> None:
        case = copy.deepcopy(self.cases[0])
        case["observed_at"] = "not-a-time"
        case["logs"][0]["level"] = "FATAL"
        errors = validate_case(case)
        self.assertTrue(any("observed_at 不是合法的 ISO 8601" in error for error in errors))
        self.assertTrue(any("level 必须是 DEBUG、INFO、WARN 或 ERROR" in error for error in errors))

    def test_duplicate_case_ids_are_rejected(self) -> None:
        errors = validate_document([self.cases[0], copy.deepcopy(self.cases[0])])
        self.assertTrue(any("case_id 重复" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
