"""Reusable runtime pipeline built from the existing T3, T4, and T5 modules."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from src.analyze_root_cause import analyze_case
from src.detect_anomalies import detect_case
from src.model_client import OpenAICompatibleClient
from src.validate_cases import validate_case


class ObservationValidationError(ValueError):
    """Raised when a runtime observation does not comply with the T3 schema."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def validate_and_sanitize_observation(observation: Any) -> dict[str, Any]:
    """Validate one runtime input and remove evaluation-only fields before use."""

    errors = validate_case(observation, require_label=False)
    if errors:
        raise ObservationValidationError(errors)
    sanitized = copy.deepcopy(observation)
    sanitized.pop("expected_label", None)
    return sanitized


def analyze_observation(
    observation: dict[str, Any], use_model: bool = False, project_root: Path | None = None
) -> dict[str, Any]:
    """Run T4 and T5, using a configured model only when explicitly requested."""

    clean_observation = validate_and_sanitize_observation(observation)
    t4_output = detect_case(clean_observation)
    client = None
    if use_model:
        root = project_root or Path(__file__).resolve().parents[1]
        client = OpenAICompatibleClient.from_project(root)
    result = analyze_case(t4_output, client=client, use_model=use_model)

    # Runtime requests must never unlock remediation, regardless of later code changes.
    result["safety"] = {"auto_remediation_allowed": False, "actions_taken": []}
    return result
