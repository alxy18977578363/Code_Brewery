from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.result_store import ResultStore


class ResultStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = ResultStore(Path(self.temp_dir.name) / "aiops.db")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_observation_and_analysis_round_trip(self) -> None:
        observation = {"case_id": "runtime-001", "service": {"name": "demo-service"}}
        saved_observation = self.store.save_observation(observation)
        self.assertEqual(self.store.get_observation(saved_observation["observation_id"]), observation)

        analysis = {"case_id": "runtime-001", "result": {"label": "normal"}}
        saved_analysis = self.store.save_analysis(saved_observation["observation_id"], analysis, False)
        loaded = self.store.get_analysis(saved_analysis["analysis_id"])

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["analysis"], analysis)
        self.assertFalse(loaded["model_requested"])
        self.assertNotIn("freeaiops", loaded)
        self.assertEqual(self.store.latest_analysis()["analysis_id"], saved_analysis["analysis_id"])

    def test_freeaiops_status_is_persisted_with_analysis(self) -> None:
        observation = {"case_id": "runtime-002", "service": {"name": "demo-service"}}
        saved_observation = self.store.save_observation(observation)
        status = {"status": "online", "http_status": 200, "checked_at": "2026-08-30T00:00:00+00:00"}
        saved_analysis = self.store.save_analysis(
            saved_observation["observation_id"], {"result": {"label": "normal"}}, False, freeaiops=status
        )
        loaded = self.store.get_analysis(saved_analysis["analysis_id"])
        self.assertEqual(loaded["freeaiops"], status)

    def test_missing_records_return_none(self) -> None:
        self.assertIsNone(self.store.get_observation("obs-missing"))
        self.assertIsNone(self.store.get_analysis("analysis-missing"))
        self.assertIsNone(self.store.latest_analysis())
