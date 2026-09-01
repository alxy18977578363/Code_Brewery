"""FreeAiOps adapter used by the local AIOps pipeline.

The checked-in FreeAiOps version exposes a generic ``app`` CRUD endpoint but
does not yet expose a first-class event API.  We therefore use a namespaced
``aiops-event:`` application record as a compatibility envelope.  This keeps
the FreeAiOps source untouched while still allowing the Agent to publish and
read structured observations/events through FreeAiOps' own MySQL-backed API.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class FreeAiOpsAdapter:
    """Health, event publish and event read operations for FreeAiOps."""

    def __init__(self, base_url: str | None = None, timeout: float = 0.5) -> None:
        configured = base_url or os.environ.get("FREEAIOPS_BASE_URL", "http://127.0.0.1:8080")
        self.base_url = configured.rstrip("/")
        self.timeout = timeout
        self.events_path = os.environ.get("FREEAIOPS_EVENTS_PATH", "/api/v1/app")
        # The current FreeAiOps response mapper returns a compact description
        # instead of the original JSON body.  Keep the just-published envelope
        # in memory so the same Agent process can read it back losslessly.
        self._published_payloads: dict[str, dict[str, Any]] = {}

    @property
    def health_url(self) -> str:
        return f"{self.base_url}/health"

    @property
    def events_url(self) -> str:
        return f"{self.base_url}/{self.events_path.strip('/') }"

    def check_health(self) -> dict[str, Any]:
        """Return status data; network failures are represented, not raised."""

        checked_at = _now_iso()
        request = Request(self.health_url, method="GET", headers={"Accept": "application/json"})
        started = time.perf_counter()
        try:
            with urlopen(request, timeout=self.timeout) as response:
                status_code = int(response.status)
                response.read(4096)
            latency_ms = round((time.perf_counter() - started) * 1000, 3)
            if 200 <= status_code < 300:
                return {
                    "status": "online",
                    "base_url": self.base_url,
                    "health_url": self.health_url,
                    "checked_at": checked_at,
                    "http_status": status_code,
                    "latency_ms": latency_ms,
                    "message": "FreeAiOps 健康检查通过",
                }
            return {
                "status": "degraded",
                "base_url": self.base_url,
                "health_url": self.health_url,
                "checked_at": checked_at,
                "http_status": status_code,
                "latency_ms": latency_ms,
                "message": f"FreeAiOps 返回 HTTP {status_code}",
            }
        except HTTPError as exc:
            # HTTP response means the service is reachable, even when it reports an error.
            return self._failure(
                checked_at,
                f"FreeAiOps 返回 HTTP {exc.code}",
                exc.code,
                started,
                status="degraded",
            )
        except (URLError, TimeoutError, OSError) as exc:
            reason = getattr(exc, "reason", None) or exc
            return self._failure(checked_at, f"FreeAiOps 不可达：{reason}", None, started)

    def publish_event(
        self,
        observation: dict[str, Any],
        detection: dict[str, Any],
        observation_id: str,
    ) -> dict[str, Any]:
        """Publish an abnormal observation as a FreeAiOps event envelope.

        FreeAiOps' generic app endpoint accepts ``name/description/level/type``.
        The complete observation and T4 detection are kept as JSON in
        ``description`` so the Agent can retrieve the exact event later.
        """

        event_id = f"evt-{observation_id.removeprefix('obs-')}"
        result = detection.get("result", {}) if isinstance(detection, dict) else {}
        label = str(result.get("label", "abnormal"))
        severity = str(result.get("severity", "high")).lower()
        level = {"critical": "S1", "high": "S2", "medium": "S3", "low": "S4"}.get(severity, "S3")
        payload = {
            "event_schema": "aiops-event-1.0",
            "event_id": event_id,
            "event_type": "anomaly",
            "label": label,
            "observation_id": observation_id,
            "observed_at": observation.get("observed_at"),
            "service": observation.get("service"),
            "observation": observation,
            "detection": detection,
        }
        self._published_payloads[event_id] = payload
        body = {
            "name": f"aiops-event:{event_id}",
            "description": json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            "level": level,
            "type": "container",
        }
        request = Request(
            self.events_url,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urlopen(request, timeout=max(self.timeout, 1.5)) as response:
                raw = response.read(4096).decode("utf-8", errors="replace")
                status_code = int(response.status)
            if not 200 <= status_code < 300:
                return {"status": "failed", "event_id": event_id, "http_status": status_code}
            return {
                "status": "published",
                "event_id": event_id,
                "http_status": status_code,
                "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                "endpoint": self.events_url,
                "response": self._safe_json(raw),
                "payload": payload,
            }
        except HTTPError as exc:
            return {"status": "failed", "event_id": event_id, "http_status": exc.code, "message": f"HTTP {exc.code}"}
        except (URLError, TimeoutError, OSError) as exc:
            reason = getattr(exc, "reason", None) or exc
            return {"status": "failed", "event_id": event_id, "http_status": None, "message": str(reason)}

    def list_events(self, limit: int = 20) -> dict[str, Any]:
        """Read namespaced AIOps events from FreeAiOps."""

        limit = max(1, min(int(limit), 100))
        request = Request(f"{self.events_url}?size={limit}&current=1", headers={"Accept": "application/json"}, method="GET")
        started = time.perf_counter()
        try:
            with urlopen(request, timeout=max(self.timeout, 1.5)) as response:
                raw = response.read(256 * 1024).decode("utf-8", errors="replace")
                status_code = int(response.status)
            data = self._safe_json(raw)
            events = []
            results = data.get("data", {}).get("results", []) if isinstance(data, dict) else []
            for item in results if isinstance(results, list) else []:
                if not isinstance(item, dict) or not str(item.get("name", "")).startswith("aiops-event:"):
                    continue
                encoded = item.get("description", "")
                try:
                    payload = json.loads(encoded) if isinstance(encoded, str) else {}
                except json.JSONDecodeError:
                    payload = {}
                event_name = str(item.get("name", ""))
                event_id = event_name.removeprefix("aiops-event:")
                if not isinstance(payload, dict) or payload.get("event_schema") != "aiops-event-1.0":
                    payload = self._published_payloads.get(event_id, {
                        "event_schema": "aiops-event-1.0",
                        "event_id": event_id,
                        "event_type": "anomaly",
                        "label": "abnormal",
                    })
                events.append({"event": payload, "freeaiops_record": item})
            return {
                "status": "retrieved",
                "http_status": status_code,
                "count": len(events),
                "events": events,
                "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                "endpoint": self.events_url,
            }
        except HTTPError as exc:
            return {"status": "failed", "http_status": exc.code, "count": 0, "events": [], "message": f"HTTP {exc.code}"}
        except (URLError, TimeoutError, OSError, ValueError) as exc:
            reason = getattr(exc, "reason", None) or exc
            return {"status": "failed", "http_status": None, "count": 0, "events": [], "message": str(reason)}

    def retrieve_event(self, event_id: str, limit: int = 100) -> dict[str, Any] | None:
        """Return one event envelope by its namespaced event id."""

        result = self.list_events(limit=limit)
        for item in result.get("events", []):
            event = item.get("event", {})
            if event.get("event_id") == event_id:
                return item
        return None

    @staticmethod
    def _safe_json(raw: str) -> Any:
        try:
            return json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            return raw[:1000]

    def _failure(
        self,
        checked_at: str,
        message: str,
        status_code: int | None,
        started: float,
        status: str = "offline",
    ) -> dict[str, Any]:
        return {
            "status": status,
            "base_url": self.base_url,
            "health_url": self.health_url,
            "checked_at": checked_at,
            "http_status": status_code,
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
            "message": message,
        }
