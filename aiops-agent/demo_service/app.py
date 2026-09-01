"""Small observable demo service used as the AIOps monitoring target."""

from __future__ import annotations

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


STARTED = time.time()
STATE = {"requests": 0, "errors": 0, "latency_total_ms": 0.0}
LOCK = threading.Lock()
LOG_PATH = Path(os.environ.get("DEMO_LOG_PATH", "/runtime/demo_service.log"))


def write_log(level: str, message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {level} demo-service {message}\n")


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        started = time.perf_counter()
        with LOCK:
            STATE["requests"] += 1
        if self.path == "/health":
            self._json(200, {"status": "ok", "service": "demo-service", "uptime_seconds": round(time.time() - STARTED, 1)})
        elif self.path == "/metrics":
            with LOCK:
                requests = STATE["requests"]
                errors = STATE["errors"]
                latency_total = STATE["latency_total_ms"]
            self._json(200, {
                "request_rate_per_sec": round(requests / max(1.0, time.time() - STARTED), 2),
                "response_time_ms": round(latency_total / max(1, requests), 2),
                "error_rate_percent": round(errors / max(1, requests) * 100, 2),
                "db_connection_usage_percent": 12.0,
            })
        elif self.path == "/error":
            with LOCK:
                STATE["errors"] += 1
            write_log("ERROR", "simulated demo failure")
            self._json(500, {"status": "error"})
        else:
            self._json(404, {"status": "not_found"})
        elapsed = (time.perf_counter() - started) * 1000
        with LOCK:
            STATE["latency_total_ms"] += elapsed

    def log_message(self, *_args) -> None:
        return


if __name__ == "__main__":
    write_log("INFO", "demo service started")
    server = ThreadingHTTPServer(("0.0.0.0", 9000), Handler)
    server.serve_forever()
