"""Rule-based anomaly detection for T4.

The detector consumes the T3 observation format and emits the standard Agent
output format described in ``docs/T3_AGENT_OUTPUT_SCHEMA.md``.  It deliberately
does not use ``expected_label`` so that evaluation labels cannot leak into a
runtime decision.

Usage:
    python src/detect_anomalies.py eval/cases.json
    python src/detect_anomalies.py eval/cases.json --output eval/results.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# These are intentionally simple, explainable demo thresholds.  The load
# threshold is machine-dependent and should become configurable in a later
# version; it is included here so the supplied evaluation cases are covered.
METRIC_RULES: dict[str, dict[str, Any]] = {
    "cpu_usage_percent": {
        "threshold": 80,
        "reason": "CPU 使用率超过异常阈值",
    },
    "memory_usage_percent": {
        "threshold": 95,
        "reason": "内存使用率超过异常阈值",
    },
    "disk_usage_percent": {
        "threshold": 90,
        "reason": "磁盘使用率超过异常阈值",
    },
    "load_1m": {
        "threshold": 8,
        "reason": "1 分钟系统负载超过演示阈值",
    },
    "response_time_ms": {
        "threshold": 500,
        "reason": "响应时间超过异常阈值",
    },
    "error_rate_percent": {
        "threshold": 5,
        "reason": "错误率超过异常阈值",
    },
    "db_connection_usage_percent": {
        "threshold": 80,
        "reason": "数据库连接使用率超过异常阈值",
    },
}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _metric_evidence(metrics: Any) -> tuple[list[dict[str, Any]], int, int, list[str]]:
    """Return evidence, signal count, missing count, and signal reasons."""

    if not isinstance(metrics, dict):
        return [], 0, len(METRIC_RULES), []

    evidence: list[dict[str, Any]] = []
    signal_count = 0
    missing_count = 0
    signal_reasons: list[str] = []

    for name, rule in METRIC_RULES.items():
        value = metrics.get(name)
        threshold = rule["threshold"]
        reason = rule["reason"]

        if value is None:
            missing_count += 1
            evidence.append(
                {
                    "name": name,
                    "value": None,
                    "threshold": None,
                    "operator": "missing",
                    "reason": "指标缺失，未参与异常判断",
                }
            )
            continue

        if not _is_number(value) or not math.isfinite(float(value)):
            missing_count += 1
            evidence.append(
                {
                    "name": name,
                    "value": value,
                    "threshold": None,
                    "operator": "invalid",
                    "reason": "指标不是可比较的有限数字，未参与异常判断",
                }
            )
            continue

        if value > threshold:
            signal_count += 1
            signal_reasons.append(reason)
            evidence.append(
                {
                    "name": name,
                    "value": value,
                    "threshold": threshold,
                    "operator": ">",
                    "reason": reason,
                }
            )

    return evidence, signal_count, missing_count, signal_reasons


def _log_evidence(logs: Any) -> tuple[list[dict[str, Any]], int, list[str]]:
    """Keep ERROR/WARN logs as evidence; only ERROR contributes a signal."""

    if not isinstance(logs, list):
        return [], 0, []

    evidence: list[dict[str, Any]] = []
    error_count = 0
    signal_reasons: list[str] = []
    for log in logs:
        if not isinstance(log, dict) or log.get("level") not in {"ERROR", "WARN"}:
            continue
        level = log.get("level")
        item = {
            "timestamp": log.get("timestamp"),
            "level": level,
            "source": log.get("source"),
            "message": log.get("message"),
            "reason": "检测到 ERROR 级别日志"
            if level == "ERROR"
            else "WARN 日志作为辅助证据",
        }
        evidence.append(item)
        if level == "ERROR":
            error_count += 1
            signal_reasons.append("检测到 ERROR 级别日志")
    return evidence, error_count, signal_reasons


def _severity(signal_count: int) -> str:
    if signal_count == 0:
        return "normal"
    if signal_count == 1:
        return "low"
    if signal_count <= 3:
        return "medium"
    if signal_count <= 5:
        return "high"
    return "critical"


def _summary(signal_count: int, missing_count: int, reasons: list[str]) -> str:
    if signal_count == 0:
        if missing_count:
            return "未发现明确异常，但部分指标缺失，判断置信度有限"
        return "未发现超过第一版阈值的指标或 ERROR 日志"
    unique_reasons = list(dict.fromkeys(reasons))
    detail = "；".join(unique_reasons[:3])
    if len(unique_reasons) > 3:
        detail += "等"
    return f"检测到 {signal_count} 个异常信号：{detail}"


def detect_case(case: dict[str, Any]) -> dict[str, Any]:
    """Detect one T3 case and return one standard T3 Agent output object."""

    started = time.perf_counter()
    metric_items, metric_signals, missing_count, metric_reasons = _metric_evidence(
        case.get("metrics")
    )
    log_items, log_signals, log_reasons = _log_evidence(case.get("logs"))
    signal_count = metric_signals + log_signals
    reasons = metric_reasons + log_reasons
    label = "abnormal" if signal_count else "normal"
    confidence = (
        min(0.99, 0.75 + 0.05 * signal_count)
        if signal_count
        else (0.65 if missing_count else 0.90)
    )

    service = case.get("service")
    service_name = service.get("name", "unknown-service") if isinstance(service, dict) else "unknown-service"
    latency_ms = round((time.perf_counter() - started) * 1000, 3)
    return {
        "schema_version": "1.0",
        "case_id": case.get("case_id", "unknown-case"),
        "analyzed_at": _now_iso(),
        "service": {"name": service_name},
        "result": {
            "label": label,
            "severity": _severity(signal_count),
            "confidence": round(confidence, 3),
            "summary": _summary(signal_count, missing_count, reasons),
        },
        "evidence": {
            "metrics": metric_items,
            "logs": log_items,
        },
        "root_causes": [],
        "recommendations": [],
        "safety": {
            "auto_remediation_allowed": False,
            "actions_taken": [],
        },
        "performance": {
            "latency_ms": latency_ms,
            "detector": "rule-v1",
            "model_used": False,
            "model_name": None,
        },
    }


def detect_document(document: Any) -> Any:
    """Process one case or an array, preserving the input's top-level shape."""

    if isinstance(document, list):
        return [detect_case(case) for case in document]
    if isinstance(document, dict):
        return detect_case(document)
    raise ValueError("输入必须是 JSON 对象或案例数组")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run T4 rule-based anomaly detection")
    parser.add_argument("input", type=Path, help="T3 JSON case or array of cases")
    parser.add_argument("--output", type=Path, help="optional output JSON path")
    args = parser.parse_args(argv)

    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        result = detect_document(document)
        encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf-8")
        else:
            print(encoded, end="")
    except FileNotFoundError:
        print(f"文件不存在：{args.input}")
        return 2
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"检测失败：{exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
