"""Validate the T3 metric/log input format.

Usage:
    python src/validate_cases.py eval/cases.json

The validator intentionally uses only Python's standard library so it can run
before the project dependencies are installed.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


METRIC_RULES: dict[str, tuple[float | None, float | None, str]] = {
    "cpu_usage_percent": (0, 100, "0-100%"),
    "memory_usage_percent": (0, 100, "0-100%"),
    "disk_usage_percent": (0, 100, "0-100%"),
    "load_1m": (0, None, ">= 0"),
    "request_rate_per_sec": (0, None, ">= 0"),
    "response_time_ms": (0, None, ">= 0"),
    "error_rate_percent": (0, 100, "0-100%"),
    "db_connection_usage_percent": (0, 100, "0-100%"),
}
LOG_LEVELS = {"DEBUG", "INFO", "WARN", "ERROR"}
LABELS = {"normal", "abnormal"}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _check_timestamp(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} 必须是非空 ISO 8601 时间字符串")
        return
    try:
        # Python's fromisoformat accepts offsets such as +08:00. Convert Z for
        # compatibility across supported Python versions.
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field} 不是合法的 ISO 8601 时间：{value!r}")


def validate_case(case: Any, index: int | None = None, require_label: bool = False) -> list[str]:
    """Return human-readable validation errors for one case."""

    prefix = f"案例[{index}]" if index is not None else "案例"
    errors: list[str] = []
    if not isinstance(case, dict):
        return [f"{prefix} 必须是 JSON 对象"]

    required = {"schema_version", "case_id", "observed_at", "service", "metrics", "logs"}
    if require_label:
        required.add("expected_label")
    for field in sorted(required):
        if field not in case:
            errors.append(f"{prefix} 缺少必填字段：{field}")

    if "schema_version" in case and case["schema_version"] != "1.0":
        errors.append(f"{prefix}.schema_version 必须是 '1.0'")

    if "case_id" in case and (not isinstance(case["case_id"], str) or not case["case_id"].strip()):
        errors.append(f"{prefix}.case_id 必须是非空字符串")

    if "observed_at" in case:
        _check_timestamp(case["observed_at"], f"{prefix}.observed_at", errors)

    service = case.get("service")
    if not isinstance(service, dict):
        errors.append(f"{prefix}.service 必须是对象")
    elif not isinstance(service.get("name"), str) or not service["name"].strip():
        errors.append(f"{prefix}.service.name 必须是非空字符串")

    metrics = case.get("metrics")
    if not isinstance(metrics, dict):
        errors.append(f"{prefix}.metrics 必须是对象")
    else:
        for name, (minimum, maximum, description) in METRIC_RULES.items():
            if name not in metrics:
                errors.append(f"{prefix}.metrics 缺少指标：{name}")
                continue
            value = metrics[name]
            if value is None:
                continue
            if not _is_number(value) or not math.isfinite(float(value)):
                errors.append(f"{prefix}.metrics.{name} 必须是数字或 null（范围 {description}）")
                continue
            if minimum is not None and value < minimum:
                errors.append(f"{prefix}.metrics.{name} 不能小于 {minimum}")
            if maximum is not None and value > maximum:
                errors.append(f"{prefix}.metrics.{name} 不能大于 {maximum}")

    logs = case.get("logs")
    if not isinstance(logs, list):
        errors.append(f"{prefix}.logs 必须是数组")
    else:
        for log_index, log in enumerate(logs):
            log_prefix = f"{prefix}.logs[{log_index}]"
            if not isinstance(log, dict):
                errors.append(f"{log_prefix} 必须是对象")
                continue
            for field in ("timestamp", "level", "source", "message"):
                if field not in log:
                    errors.append(f"{log_prefix} 缺少字段：{field}")
            if "timestamp" in log:
                _check_timestamp(log["timestamp"], f"{log_prefix}.timestamp", errors)
            if "level" in log and log["level"] not in LOG_LEVELS:
                errors.append(f"{log_prefix}.level 必须是 DEBUG、INFO、WARN 或 ERROR")
            for field in ("source", "message"):
                if field in log and (not isinstance(log[field], str) or not log[field].strip()):
                    errors.append(f"{log_prefix}.{field} 必须是非空字符串")

    if "expected_label" in case and case["expected_label"] not in LABELS:
        errors.append(f"{prefix}.expected_label 必须是 normal 或 abnormal")
    return errors


def validate_document(document: Any, require_label: bool = False) -> list[str]:
    """Validate a single case or a JSON array of cases."""

    cases = document if isinstance(document, list) else [document]
    if not cases:
        return ["输入案例数组不能为空"]
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        errors.extend(validate_case(case, index=index, require_label=require_label))
        if isinstance(case, dict) and isinstance(case.get("case_id"), str):
            case_id = case["case_id"]
            if case_id in seen_ids:
                errors.append(f"案例[{index}].case_id 重复：{case_id!r}")
            seen_ids.add(case_id)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate AIOps metric/log JSON cases")
    parser.add_argument("input", type=Path, help="JSON file containing one case or an array of cases")
    parser.add_argument(
        "--require-label",
        action="store_true",
        help="require expected_label on every case (useful for evaluation datasets)",
    )
    args = parser.parse_args(argv)

    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"文件不存在：{args.input}")
        return 2
    except json.JSONDecodeError as exc:
        print(f"JSON 格式错误：第 {exc.lineno} 行，第 {exc.colno} 列：{exc.msg}")
        return 1
    except OSError as exc:
        print(f"读取文件失败：{exc}")
        return 2

    errors = validate_document(document, require_label=args.require_label)
    if errors:
        print(f"校验失败：发现 {len(errors)} 个问题")
        for error in errors:
            print(f"- {error}")
        return 1

    count = len(document) if isinstance(document, list) else 1
    print(f"校验通过：{count} 个案例符合 T3 1.0 格式")
    return 0


if __name__ == "__main__":
    sys.exit(main())
