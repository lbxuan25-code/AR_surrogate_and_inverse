"""Candidate-family contract for inverse outputs."""

from __future__ import annotations

from typing import Any

from ar_inverse.metadata import assert_forward_metadata_complete

CANDIDATE_FAMILY_SCHEMA_VERSION = "ar_inverse_candidate_family_v1"

REQUIRED_CANDIDATE_FAMILY_KEYS: tuple[str, ...] = (
    "candidate_family_schema_version",
    "candidate_family_id",
    "interpretation",
    "pairing_controls",
    "transport_nuisance_controls",
    "uncertainty_ranges",
    "objective",
    "forward_recheck",
)


def control_ranges(center: dict[str, float], half_width: dict[str, float] | float) -> dict[str, dict[str, float]]:
    """Build min/max ranges around a center control vector."""

    ranges: dict[str, dict[str, float]] = {}
    for key, value in center.items():
        width = float(half_width[key]) if isinstance(half_width, dict) and key in half_width else float(half_width)
        ranges[key] = {
            "min": float(value) - width,
            "max": float(value) + width,
        }
    return ranges


def make_candidate_family(
    *,
    candidate_family_id: str,
    pairing_center: dict[str, float],
    pairing_ranges: dict[str, dict[str, float]],
    transport_center: dict[str, float | int],
    transport_ranges: dict[str, dict[str, float]],
    objective: dict[str, float | str],
    forward_recheck: dict[str, Any],
    surrogate_usage: dict[str, Any],
) -> dict[str, Any]:
    """Create and validate a candidate-family output."""

    family = {
        "candidate_family_schema_version": CANDIDATE_FAMILY_SCHEMA_VERSION,
        "candidate_family_id": candidate_family_id,
        "interpretation": "the AR data are compatible with these feature families",
        "pairing_controls": {
            "control_mode": "delta_from_baseline_meV",
            "center": pairing_center,
            "ranges": pairing_ranges,
        },
        "transport_nuisance_controls": {
            "center": transport_center,
            "ranges": transport_ranges,
        },
        "uncertainty_ranges": {
            "pairing_controls": pairing_ranges,
            "transport_nuisance_controls": transport_ranges,
        },
        "objective": objective,
        "surrogate_usage": surrogate_usage,
        "forward_recheck": forward_recheck,
    }
    validate_candidate_family(family)
    return family


def validate_candidate_family(candidate: dict[str, Any]) -> None:
    """Validate the Task 6 candidate-family contract."""

    missing = [key for key in REQUIRED_CANDIDATE_FAMILY_KEYS if key not in candidate]
    if missing:
        raise ValueError(f"Candidate family is missing required key(s): {', '.join(missing)}.")
    if candidate["candidate_family_schema_version"] != CANDIDATE_FAMILY_SCHEMA_VERSION:
        raise ValueError("Unsupported candidate-family schema version.")

    for key in ("pairing_controls", "transport_nuisance_controls"):
        payload = candidate[key]
        if not isinstance(payload, dict) or "center" not in payload or "ranges" not in payload:
            raise ValueError(f"Candidate family {key} must include center and ranges.")

    objective = candidate["objective"]
    if not isinstance(objective, dict) or "score" not in objective or "score_kind" not in objective:
        raise ValueError("Candidate family objective must include score and score_kind.")

    forward_recheck = candidate["forward_recheck"]
    if not isinstance(forward_recheck, dict):
        raise ValueError("Candidate family forward_recheck must be a mapping.")
    if "metadata" not in forward_recheck:
        raise ValueError("Candidate family forward_recheck must include metadata.")
    assert_forward_metadata_complete(forward_recheck["metadata"])


def validate_inverse_report(report: dict[str, Any]) -> None:
    """Validate the smoke inverse report candidate-family list."""

    if report.get("run_kind") != "task6_inverse_search_prototype":
        raise ValueError("Unexpected inverse report run_kind.")
    candidates = report.get("candidate_families")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Inverse report must include non-empty candidate_families.")
    for candidate in candidates:
        validate_candidate_family(candidate)
