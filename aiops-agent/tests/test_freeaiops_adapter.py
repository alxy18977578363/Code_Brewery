from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from src.freeaiops_adapter import FreeAiOpsAdapter


class FakeResponse:
    status = 200

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return b'"ok..."'


class FreeAiOpsAdapterTests(unittest.TestCase):
    def test_http_200_is_online(self) -> None:
        with patch("src.freeaiops_adapter.urlopen", return_value=FakeResponse()):
            status = FreeAiOpsAdapter("http://freeaiops.test", timeout=0.1).check_health()
        self.assertEqual(status["status"], "online")
        self.assertEqual(status["http_status"], 200)
        self.assertEqual(status["health_url"], "http://freeaiops.test/health")

    def test_network_error_is_offline_without_raising(self) -> None:
        with patch("src.freeaiops_adapter.urlopen", side_effect=URLError("connection refused")):
            status = FreeAiOpsAdapter("http://freeaiops.test", timeout=0.1).check_health()
        self.assertEqual(status["status"], "offline")
        self.assertIsNone(status["http_status"])
        self.assertIn("不可达", status["message"])

    def test_http_error_is_degraded_because_service_responded(self) -> None:
        error = HTTPError("http://freeaiops.test/health", 503, "busy", {}, None)
        with patch("src.freeaiops_adapter.urlopen", side_effect=error):
            status = FreeAiOpsAdapter("http://freeaiops.test", timeout=0.1).check_health()
        self.assertEqual(status["status"], "degraded")
        self.assertEqual(status["http_status"], 503)
