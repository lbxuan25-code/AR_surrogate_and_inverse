"""Shared surrogate metric helpers."""

from __future__ import annotations

import numpy as np


def regression_metrics(prediction: np.ndarray, target: np.ndarray) -> dict[str, float]:
    """Return simple spectrum regression metrics."""

    pred = np.asarray(prediction, dtype=np.float64)
    truth = np.asarray(target, dtype=np.float64)
    if pred.shape != truth.shape:
        raise ValueError(f"Prediction shape {pred.shape} does not match target shape {truth.shape}.")
    error = pred - truth
    return {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "max_abs_error": float(np.max(np.abs(error))),
    }
