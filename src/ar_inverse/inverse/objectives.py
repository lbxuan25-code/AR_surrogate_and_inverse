"""Inverse-search objective helpers."""

from __future__ import annotations

import numpy as np


def spectrum_objective(candidate_conductance: list[float], target_conductance: list[float]) -> dict[str, float]:
    """Return spectrum mismatch metrics for inverse ranking."""

    candidate = np.asarray(candidate_conductance, dtype=np.float64)
    target = np.asarray(target_conductance, dtype=np.float64)
    if candidate.shape != target.shape:
        raise ValueError(f"Candidate spectrum shape {candidate.shape} does not match target shape {target.shape}.")
    error = candidate - target
    return {
        "score": float(np.sqrt(np.mean(error**2))),
        "score_kind": "spectrum_rmse",
        "mae": float(np.mean(np.abs(error))),
        "max_abs_error": float(np.max(np.abs(error))),
    }
