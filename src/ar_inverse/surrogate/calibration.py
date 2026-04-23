"""Calibration diagnostics and fallback policy helpers."""

from __future__ import annotations

from typing import Any

import numpy as np

from ar_inverse.direction import direction_regime_from_block


def transport_regime_label(transport_controls: dict[str, Any]) -> str:
    """Return a coarse transport-regime label for error grouping."""

    barrier_z = float(transport_controls.get("barrier_z", 0.0))
    gamma = float(transport_controls.get("gamma", 0.0))
    temperature = float(transport_controls.get("temperature_kelvin", 0.0))

    barrier_bin = "low_barrier" if barrier_z < 0.6 else "high_barrier"
    gamma_bin = "low_gamma" if gamma <= 1.0 else "high_gamma"
    temp_bin = "low_temp" if temperature <= 3.0 else "high_temp"
    return f"{barrier_bin}|{gamma_bin}|{temp_bin}"


def direction_regime_label(row: dict[str, Any]) -> str:
    """Return the direction-contract bucket for evaluation grouping."""

    direction = row.get("direction")
    return direction_regime_from_block(direction if isinstance(direction, dict) else None)


def calibration_diagnostics(
    row_records: list[dict[str, Any]],
    thresholds: dict[str, float],
) -> dict[str, float | int]:
    """Summarize held-out error calibration against simple thresholds."""

    if not row_records:
        raise ValueError("Cannot compute calibration diagnostics without row records.")

    rmse_values = np.asarray([record["metrics"]["rmse"] for record in row_records], dtype=np.float64)
    max_values = np.asarray([record["metrics"]["max_abs_error"] for record in row_records], dtype=np.float64)
    unsafe = np.asarray([not bool(record["safe_for_inverse_acceleration"]) for record in row_records], dtype=bool)
    return {
        "num_rows": int(len(row_records)),
        "mean_rmse": float(np.mean(rmse_values)),
        "max_rmse": float(np.max(rmse_values)),
        "mean_max_abs_error": float(np.mean(max_values)),
        "max_abs_error": float(np.max(max_values)),
        "rmse_threshold": float(thresholds["rmse"]),
        "max_abs_error_threshold": float(thresholds["max_abs_error"]),
        "unsafe_fraction": float(np.mean(unsafe)),
    }


def fallback_policy(
    transport_regime_report: dict[str, dict[str, Any]],
    thresholds: dict[str, float],
    direction_regime_report: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a direct-forward fallback policy from transport-regime errors."""

    unsafe_regimes = sorted(
        regime for regime, report in transport_regime_report.items() if not report["safe_for_inverse_acceleration"]
    )
    safe_regimes = sorted(
        regime for regime, report in transport_regime_report.items() if report["safe_for_inverse_acceleration"]
    )
    direction_regime_report = direction_regime_report or {}
    unsafe_direction_regimes = sorted(
        regime for regime, report in direction_regime_report.items() if not report["safe_for_inverse_acceleration"]
    )
    safe_direction_regimes = sorted(
        regime for regime, report in direction_regime_report.items() if report["safe_for_inverse_acceleration"]
    )
    if unsafe_regimes:
        summary = (
            "Surrogate acceleration is disabled for unsafe transport regimes. "
            "Inverse workflows must use direct external forward calls there."
        )
    else:
        summary = (
            "All evaluated held-out transport regimes met the configured thresholds. "
            "Direct forward rechecks are still required for final inverse candidates."
        )
    return {
        "policy_id": "task9_directional_direct_forward_fallback_v1",
        "safe_error_thresholds": {
            "rmse": float(thresholds["rmse"]),
            "max_abs_error": float(thresholds["max_abs_error"]),
        },
        "safe_transport_regimes": safe_regimes,
        "unsafe_transport_regimes": unsafe_regimes,
        "safe_direction_regimes": safe_direction_regimes,
        "unsafe_direction_regimes": unsafe_direction_regimes,
        "default_action": "direct_forward_required_for_unseen_or_unsafe_regimes",
        "summary": summary,
    }
