"""Collect a small, explicit set of local AIOps observation data."""

from __future__ import annotations

import os
import re
import socket
import json
from urllib.error import URLError
from urllib.request import urlopen
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil


LOG_FILENAME = "local_events.log"
DEMO_LOG_FILENAME = "demo_service.log"
MAX_LOG_BYTES = 128 * 1024
MAX_LOG_EVENTS = 50
LEVEL_PATTERN = re.compile(r"\b(WARN|ERROR)\b", re.IGNORECASE)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_1m() -> float | None:
    try:
        return round(float(os.getloadavg()[0]), 3)
    except (AttributeError, OSError):
        return None


def read_project_log(log_path: Path, observed_at: str, source: str = "runtime/local_events.log") -> tuple[list[dict[str, str]], str]:
    """Read WARN/ERROR lines only from the explicitly allowed project log file."""

    if not log_path.exists():
        return [], "not_found"
    if not log_path.is_file():
        return [], "not_a_file"
    try:
        with log_path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - MAX_LOG_BYTES), os.SEEK_SET)
            content = handle.read().decode("utf-8", errors="replace")
    except OSError:
        return [], "unreadable"

    events: list[dict[str, str]] = []
    for line in content.splitlines()[-500:]:
        level = LEVEL_PATTERN.search(line)
        if not level:
            continue
        events.append(
            {
                "timestamp": observed_at,
                "level": level.group(1).upper(),
                "source": source,
                "message": line.strip()[:1000],
            }
        )
    return events[-MAX_LOG_EVENTS:], "read"


def collect_local_observation(project_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a T3 observation and collection metadata without scanning user files."""

    observed_at = _now_iso()
    disk_target = Path(project_root).resolve().anchor or str(project_root)
    try:
        disk_percent: float | None = round(float(psutil.disk_usage(disk_target).percent), 1)
    except OSError:
        disk_percent = None
    try:
        memory_percent: float | None = round(float(psutil.virtual_memory().percent), 1)
    except OSError:
        memory_percent = None
    try:
        cpu_percent: float | None = round(float(psutil.cpu_percent(interval=0.1)), 1)
    except OSError:
        cpu_percent = None

    log_path = Path(project_root) / "runtime" / LOG_FILENAME
    logs, log_status = read_project_log(log_path, observed_at)
    unavailable_metrics = [
        "request_rate_per_sec",
        "response_time_ms",
        "error_rate_percent",
        "db_connection_usage_percent",
    ]
    demo_base_url = os.environ.get("DEMO_SERVICE_BASE_URL", "").strip().rstrip("/")
    demo_metrics: dict[str, Any] = {}
    demo_status = "disabled"
    if demo_base_url:
        try:
            with urlopen(f"{demo_base_url}/metrics", timeout=0.5) as response:
                demo_metrics = json.loads(response.read().decode("utf-8"))
            if isinstance(demo_metrics, dict):
                demo_status = "read"
            else:
                demo_metrics = {}
                demo_status = "invalid"
        except (URLError, TimeoutError, OSError, ValueError):
            demo_status = "unavailable"
        demo_logs, demo_log_status = read_project_log(project_root / "runtime" / DEMO_LOG_FILENAME, observed_at, "runtime/demo_service.log")
        logs.extend(demo_logs)
        unavailable_metrics = [name for name in unavailable_metrics if demo_metrics.get(name) is None]
    else:
        demo_log_status = "disabled"
    hostname = socket.gethostname() or "local-machine"
    load_1m = _load_1m()
    if load_1m is None:
        unavailable_metrics.append("load_1m")
    observation = {
        "schema_version": "1.0",
        "case_id": f"local-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "observed_at": observed_at,
        "service": {"name": "demo-service" if demo_base_url else f"local-{hostname}"},
        "metrics": {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory_percent,
            "disk_usage_percent": disk_percent,
            "load_1m": load_1m,
            "request_rate_per_sec": demo_metrics.get("request_rate_per_sec"),
            "response_time_ms": demo_metrics.get("response_time_ms"),
            "error_rate_percent": demo_metrics.get("error_rate_percent"),
            "db_connection_usage_percent": demo_metrics.get("db_connection_usage_percent"),
        },
        "logs": logs,
    }
    metadata = {
        "metric_source": "local-machine",
        "log_source": "runtime/local_events.log + runtime/demo_service.log" if demo_base_url else "runtime/local_events.log",
        "log_status": log_status if not demo_base_url else f"{log_status}; demo={demo_log_status}",
        "log_events": len(logs),
        "unavailable_metrics": unavailable_metrics,
        "demo_service": {"base_url": demo_base_url or None, "metrics_status": demo_status},
    }
    return observation, metadata
