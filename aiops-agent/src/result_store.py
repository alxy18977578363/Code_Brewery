"""SQLite persistence for locally submitted observations and analyses."""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class ResultStore:
    """Store JSON documents without coupling project results to FreeAiOps MySQL."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS observations (
                        observation_id TEXT PRIMARY KEY,
                        case_id TEXT NOT NULL,
                        service_name TEXT NOT NULL,
                        received_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS analyses (
                        analysis_id TEXT PRIMARY KEY,
                        observation_id TEXT NOT NULL,
                        completed_at TEXT NOT NULL,
                        model_requested INTEGER NOT NULL,
                        result_json TEXT NOT NULL,
                        freeaiops_json TEXT,
                        FOREIGN KEY (observation_id) REFERENCES observations(observation_id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_analyses_completed_at
                    ON analyses(completed_at DESC);
                    """
                )
                # Keep databases created before T10 readable and upgrade them in place.
                columns = {
                    row[1] for row in connection.execute("PRAGMA table_info(analyses)").fetchall()
                }
                if "freeaiops_json" not in columns:
                    connection.execute("ALTER TABLE analyses ADD COLUMN freeaiops_json TEXT")

    def save_observation(self, observation: dict[str, Any]) -> dict[str, str]:
        observation_id = f"obs-{uuid.uuid4().hex}"
        received_at = _now_iso()
        service = observation.get("service", {})
        service_name = service.get("name", "unknown-service") if isinstance(service, dict) else "unknown-service"
        payload_json = json.dumps(observation, ensure_ascii=False, separators=(",", ":"))
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO observations (observation_id, case_id, service_name, received_at, payload_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (observation_id, observation.get("case_id", "unknown-case"), service_name, received_at, payload_json),
                )
        return {"observation_id": observation_id, "received_at": received_at}

    def get_observation(self, observation_id: str) -> dict[str, Any] | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT payload_json FROM observations WHERE observation_id = ?", (observation_id,)
            ).fetchone()
        return json.loads(row["payload_json"]) if row else None

    def save_analysis(
        self,
        observation_id: str,
        analysis: dict[str, Any],
        model_requested: bool,
        freeaiops: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        analysis_id = f"analysis-{uuid.uuid4().hex}"
        completed_at = _now_iso()
        result_json = json.dumps(analysis, ensure_ascii=False, separators=(",", ":"))
        freeaiops_json = (
            json.dumps(freeaiops, ensure_ascii=False, separators=(",", ":"))
            if freeaiops is not None
            else None
        )
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO analyses
                        (analysis_id, observation_id, completed_at, model_requested, result_json, freeaiops_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (analysis_id, observation_id, completed_at, int(model_requested), result_json, freeaiops_json),
                )
        return {"analysis_id": analysis_id, "completed_at": completed_at}

    @staticmethod
    def _analysis_record(row: sqlite3.Row) -> dict[str, Any]:
        record = {
            "analysis_id": row["analysis_id"],
            "observation_id": row["observation_id"],
            "completed_at": row["completed_at"],
            "model_requested": bool(row["model_requested"]),
            "analysis": json.loads(row["result_json"]),
        }
        if row["observation_json"]:
            record["observation"] = json.loads(row["observation_json"])
        if row["freeaiops_json"]:
            record["freeaiops"] = json.loads(row["freeaiops_json"])
        return record

    def get_analysis(self, analysis_id: str) -> dict[str, Any] | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT a.analysis_id, a.observation_id, a.completed_at, a.model_requested,
                       a.result_json, a.freeaiops_json, o.payload_json AS observation_json
                FROM analyses AS a
                LEFT JOIN observations AS o ON o.observation_id = a.observation_id
                WHERE a.analysis_id = ?
                """,
                (analysis_id,),
            ).fetchone()
        return self._analysis_record(row) if row else None

    def latest_analysis(self) -> dict[str, Any] | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT a.analysis_id, a.observation_id, a.completed_at, a.model_requested,
                       a.result_json, a.freeaiops_json, o.payload_json AS observation_json
                FROM analyses AS a
                LEFT JOIN observations AS o ON o.observation_id = a.observation_id
                ORDER BY a.completed_at DESC LIMIT 1
                """
            ).fetchone()
        return self._analysis_record(row) if row else None

    def list_analyses(self, limit: int = 20) -> list[dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT a.analysis_id, a.observation_id, a.completed_at, a.model_requested,
                       a.result_json, a.freeaiops_json, o.payload_json AS observation_json
                FROM analyses AS a
                LEFT JOIN observations AS o ON o.observation_id = a.observation_id
                ORDER BY a.completed_at DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._analysis_record(row) for row in rows]
