"""Evaluate T4/T5 results against the T3 labelled cases.

The evaluator compares only ``result.label`` with the offline
``expected_label``.  It also summarizes latency and model usage, while keeping
the per-case details so the course report can cite the evidence.

Usage:
    python src/evaluate_results.py
    python src/evaluate_results.py --cases eval/cases.json \
        --t4-results eval/results.json --t5-results eval/t5_results.json \
        --output eval/metrics.json
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EvaluationError(ValueError):
    """Raised when evaluation inputs cannot be matched or measured."""


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise EvaluationError(f"文件不存在：{path}") from None
    except json.JSONDecodeError as exc:
        raise EvaluationError(f"JSON 格式错误（{path}）：第 {exc.lineno} 行，第 {exc.colno} 列") from None
    except OSError as exc:
        raise EvaluationError(f"读取文件失败（{path}）：{exc}") from None


def _as_case_list(document: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(document, list):
        raise EvaluationError(f"{label} 必须是 JSON 数组")
    if not document:
        raise EvaluationError(f"{label} 不能为空")
    if not all(isinstance(item, dict) for item in document):
        raise EvaluationError(f"{label} 中每项必须是 JSON 对象")
    return document


def _index_by_case_id(items: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        case_id = item.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise EvaluationError(f"{label} 存在缺失或无效 case_id")
        if case_id in indexed:
            raise EvaluationError(f"{label} 存在重复 case_id：{case_id}")
        indexed[case_id] = item
    return indexed


def _latency(item: dict[str, Any], label: str, case_id: str) -> float:
    try:
        value = item["performance"]["latency_ms"]
    except (KeyError, TypeError):
        raise EvaluationError(f"{label} 的 {case_id} 缺少 performance.latency_ms") from None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EvaluationError(f"{label} 的 {case_id} latency_ms 必须是数字")
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise EvaluationError(f"{label} 的 {case_id} latency_ms 必须是非负有限数字")
    return value


def _stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"average": 0.0, "minimum": 0.0, "maximum": 0.0, "median": 0.0}
    return {
        "average": round(statistics.fmean(values), 3),
        "minimum": round(min(values), 3),
        "maximum": round(max(values), 3),
        "median": round(statistics.median(values), 3),
    }


def evaluate(
    cases_document: Any,
    t4_document: Any,
    t5_document: Any | None = None,
) -> dict[str, Any]:
    """Build a machine-readable evaluation report."""

    cases = _as_case_list(cases_document, "测试案例")
    t4_results = _as_case_list(t4_document, "T4 结果")
    case_map = _index_by_case_id(cases, "测试案例")
    t4_map = _index_by_case_id(t4_results, "T4 结果")

    missing_t4 = sorted(set(case_map) - set(t4_map))
    extra_t4 = sorted(set(t4_map) - set(case_map))
    if missing_t4 or extra_t4:
        details = []
        if missing_t4:
            details.append("T4 缺少：" + ", ".join(missing_t4))
        if extra_t4:
            details.append("T4 多出：" + ", ".join(extra_t4))
        raise EvaluationError("案例与 T4 结果无法一一匹配；" + "；".join(details))

    t5_map: dict[str, dict[str, Any]] | None = None
    if t5_document is not None:
        t5_results = _as_case_list(t5_document, "T5 结果")
        t5_map = _index_by_case_id(t5_results, "T5 结果")
        missing_t5 = sorted(set(case_map) - set(t5_map))
        extra_t5 = sorted(set(t5_map) - set(case_map))
        if missing_t5 or extra_t5:
            details = []
            if missing_t5:
                details.append("T5 缺少：" + ", ".join(missing_t5))
            if extra_t5:
                details.append("T5 多出：" + ", ".join(extra_t5))
            raise EvaluationError("案例与 T5 结果无法一一匹配；" + "；".join(details))

    case_results: list[dict[str, Any]] = []
    t4_latencies: list[float] = []
    t5_latencies: list[float] = []
    correct_count = 0
    model_calls = 0
    fallback_cases = 0
    normal_without_model = 0
    for case_id, case in case_map.items():
        t4 = t4_map[case_id]
        expected = case.get("expected_label")
        actual = t4.get("result", {}).get("label") if isinstance(t4.get("result"), dict) else None
        if expected not in {"normal", "abnormal"}:
            raise EvaluationError(f"案例 {case_id} 的 expected_label 无效")
        if actual not in {"normal", "abnormal"}:
            raise EvaluationError(f"T4 的 {case_id} 缺少有效 result.label")
        t4_latency = _latency(t4, "T4 结果", case_id)
        t4_latencies.append(t4_latency)
        correct = expected == actual
        correct_count += int(correct)

        detail: dict[str, Any] = {
            "case_id": case_id,
            "expected_label": expected,
            "actual_label": actual,
            "correct": correct,
            "t4_latency_ms": t4_latency,
        }
        if t5_map is not None:
            t5 = t5_map[case_id]
            t5_latency = _latency(t5, "T5 结果", case_id)
            t5_latencies.append(t5_latency)
            performance = t5.get("performance")
            if not isinstance(performance, dict):
                raise EvaluationError(f"T5 的 {case_id} 缺少 performance 对象")
            model_used = performance.get("model_used") is True
            detector = performance.get("detector")
            model_calls += int(model_used)
            fallback_cases += int(isinstance(detector, str) and "fallback" in detector)
            normal_without_model += int(actual == "normal" and not model_used)
            detail.update(
                {
                    "t5_latency_ms": t5_latency,
                    "model_used": model_used,
                    "detector": detector,
                }
            )
        case_results.append(detail)

    total = len(cases)
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "total_cases": total,
        "correct_cases": correct_count,
        "incorrect_cases": total - correct_count,
        "accuracy": round(correct_count / total, 4),
        "accuracy_percent": round(correct_count / total * 100, 2),
        "t4_latency_ms": _stats(t4_latencies),
        "case_results": case_results,
    }
    if t5_map is not None:
        report["t5_latency_ms"] = _stats(t5_latencies)
        report["model_usage"] = {
            "model_calls": model_calls,
            "fallback_cases": fallback_cases,
            "normal_cases_without_model": normal_without_model,
            "rule_cases": total - model_calls,
        }
    else:
        report["t5_latency_ms"] = None
        report["model_usage"] = None
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate T4/T5 AIOps results")
    parser.add_argument("--cases", type=Path, default=Path("eval/cases.json"))
    parser.add_argument("--t4-results", type=Path, default=Path("eval/results.json"))
    parser.add_argument("--t5-results", type=Path, default=Path("eval/t5_results.json"))
    parser.add_argument("--output", type=Path, default=Path("eval/metrics.json"))
    parser.add_argument("--without-t5", action="store_true", help="only evaluate T4 results")
    args = parser.parse_args(argv)

    try:
        cases = _read_json(args.cases)
        t4_results = _read_json(args.t4_results)
        t5_results = None if args.without_t5 else _read_json(args.t5_results)
        report = evaluate(cases, t4_results, t5_results)
        encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
        print(f"评估完成：{report['total_cases']} 个案例")
        print(f"准确率：{report['accuracy_percent']}%（{report['correct_cases']}/{report['total_cases']}）")
        t4_stats = report["t4_latency_ms"]
        print(f"T4 平均响应时间：{t4_stats['average']} ms")
        if report["t5_latency_ms"] is not None:
            print(f"T5 平均响应时间：{report['t5_latency_ms']['average']} ms")
            print(f"模型调用次数：{report['model_usage']['model_calls']}")
        print(f"结果文件：{args.output}")
    except (EvaluationError, OSError, TypeError, ValueError) as exc:
        print(f"评估失败：{exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
