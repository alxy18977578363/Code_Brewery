from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.local_collector import collect_local_observation, read_project_log


class LocalCollectorTests(unittest.TestCase):
    def test_collects_allowed_metrics_and_explicit_log_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / "runtime"
            runtime.mkdir()
            (runtime / "local_events.log").write_text(
                "INFO ignored\nWARN cache growing\nERROR database timeout\n", encoding="utf-8"
            )
            with patch("src.local_collector.psutil.cpu_percent", return_value=41.2), patch(
                "src.local_collector.psutil.virtual_memory", return_value=SimpleNamespace(percent=52.3)
            ), patch(
                "src.local_collector.psutil.disk_usage", return_value=SimpleNamespace(percent=67.8)
            ), patch("src.local_collector._load_1m", return_value=None):
                observation, metadata = collect_local_observation(root)

        self.assertEqual(observation["metrics"]["cpu_usage_percent"], 41.2)
        self.assertEqual(observation["metrics"]["memory_usage_percent"], 52.3)
        self.assertEqual(observation["metrics"]["disk_usage_percent"], 67.8)
        self.assertIsNone(observation["metrics"]["request_rate_per_sec"])
        self.assertEqual([item["level"] for item in observation["logs"]], ["WARN", "ERROR"])
        self.assertEqual(metadata["log_source"], "runtime/local_events.log")
        self.assertEqual(metadata["log_status"], "read")

    def test_missing_explicit_log_file_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            logs, status = read_project_log(Path(directory) / "missing.log", "2026-08-30T10:00:00+00:00")
        self.assertEqual(logs, [])
        self.assertEqual(status, "not_found")
