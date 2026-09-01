from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.analyze_root_cause import (
    analyze_case,
    analyze_document,
    build_candidate_causes,
    build_prompt,
    validate_model_result,
)
from src.detect_anomalies import detect_document


ROOT = Path(__file__).resolve().parents[1]


class FakeClient:
    model = "fake-model"

    def __init__(self, content: str) -> None:
        self.content = content
        self.calls = 0

    def complete(self, prompt: str) -> tuple[str, float]:
        self.calls += 1
        return self.content, 1.0


class RootCauseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cases = json.loads((ROOT / "eval" / "cases.json").read_text(encoding="utf-8"))
        cls.t4_outputs = detect_document(cases)

    def test_rule_fallback_explains_abnormal_case_without_model(self) -> None:
        output = analyze_case(self.t4_outputs[10])
        self.assertTrue(output["root_causes"])
        self.assertTrue(output["recommendations"])
        self.assertFalse(output["performance"]["model_used"])
        self.assertTrue(all(item["requires_approval"] for item in output["recommendations"]))

    def test_normal_case_does_not_call_model(self) -> None:
        client = FakeClient("this must not be called")
        output = analyze_case(self.t4_outputs[1], client=client, use_model=True)
        self.assertEqual(client.calls, 0)
        self.assertEqual(output["root_causes"], [])
        self.assertEqual(output["recommendations"], [])

    def test_valid_model_result_is_merged(self) -> None:
        client = FakeClient(
            json.dumps(
                {
                    "root_causes": [
                        {
                            "cause": "计算资源压力较高",
                            "confidence": 0.8,
                            "evidence_refs": ["metrics.cpu_usage_percent"],
                        }
                    ],
                    "recommendations": [
                        {
                            "priority": "P2",
                            "action": "检查 CPU 占用最高的进程和请求并发",
                            "rationale": "CPU 指标超过阈值",
                            "requires_approval": True,
                        }
                    ],
                },
                ensure_ascii=False,
            )
        )
        output = analyze_case(self.t4_outputs[4], client=client, use_model=True)
        self.assertEqual(client.calls, 1)
        self.assertTrue(output["performance"]["model_used"])
        self.assertEqual(output["performance"]["detector"], "rule-v1+llm-v1")
        self.assertEqual(output["performance"]["model_name"], "fake-model")
        self.assertEqual(output["root_causes"][0]["evidence_refs"], ["metrics.cpu_usage_percent"])

    def test_invalid_model_result_uses_safe_fallback(self) -> None:
        client = FakeClient('{"root_causes": [{"cause": "bad"}], "recommendations": []}')
        output = analyze_case(self.t4_outputs[4], client=client, use_model=True)
        self.assertTrue(output["root_causes"])
        self.assertEqual(output["performance"]["detector"], "rule-v1-fallback")
        self.assertFalse(output["performance"]["model_used"])
        self.assertIn("规则回退", output["result"]["summary"])

    def test_prompt_does_not_contain_evaluation_label(self) -> None:
        output = self.t4_outputs[0]
        prompt = build_prompt(output, build_candidate_causes(output))
        self.assertNotIn("expected_label", prompt)
        self.assertIn("candidate_causes", prompt)

    def test_unsafe_model_recommendation_is_rejected(self) -> None:
        result = {
            "root_causes": [],
            "recommendations": [
                {
                    "priority": "P1",
                    "action": "执行 rm -rf 清理目录",
                    "rationale": "释放空间",
                    "requires_approval": True,
                }
            ],
        }
        errors = validate_model_result(result, self.t4_outputs[6])
        self.assertTrue(any("不安全操作" in error for error in errors))

    def test_all_twenty_outputs_can_be_analyzed_offline(self) -> None:
        outputs = analyze_document(self.t4_outputs)
        self.assertEqual(len(outputs), 20)
        for output in outputs:
            self.assertIn(output["result"]["label"], {"normal", "abnormal"})
            if output["result"]["label"] == "normal":
                self.assertEqual(output["root_causes"], [])
            else:
                self.assertTrue(output["root_causes"])


if __name__ == "__main__":
    unittest.main()
