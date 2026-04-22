"""Experiment spectrum ingest schema."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ar_inverse.direction import normalize_direction_prior

EXPERIMENT_SPECTRUM_SCHEMA_VERSION = "ar_inverse_experiment_spectrum_v1"

REQUIRED_EXPERIMENT_KEYS: tuple[str, ...] = (
    "experiment_schema_version",
    "experiment_id",
    "bias_mev",
    "conductance",
    "metadata",
)


def validate_experiment_spectrum(payload: dict[str, Any]) -> None:
    """Validate the experiment ingest contract."""

    missing = [key for key in REQUIRED_EXPERIMENT_KEYS if key not in payload]
    if missing:
        raise ValueError(f"Experiment spectrum is missing required key(s): {', '.join(missing)}.")
    if payload["experiment_schema_version"] != EXPERIMENT_SPECTRUM_SCHEMA_VERSION:
        raise ValueError("Unsupported experiment spectrum schema version.")

    bias = np.asarray(payload["bias_mev"], dtype=np.float64)
    conductance = np.asarray(payload["conductance"], dtype=np.float64)
    if bias.ndim != 1 or conductance.ndim != 1:
        raise ValueError("Experiment bias_mev and conductance must be 1D arrays.")
    if bias.shape != conductance.shape:
        raise ValueError("Experiment bias_mev and conductance must have the same shape.")
    if len(bias) < 2:
        raise ValueError("Experiment spectrum must contain at least two bias points.")
    if not np.all(np.isfinite(bias)) or not np.all(np.isfinite(conductance)):
        raise ValueError("Experiment spectrum contains non-finite values.")
    if not isinstance(payload["metadata"], dict):
        raise ValueError("Experiment metadata must be a mapping.")
    if "direction_prior" in payload["metadata"]:
        normalize_direction_prior(payload["metadata"]["direction_prior"])


def load_experiment_spectrum(path: Path | str) -> dict[str, Any]:
    """Load and validate an experiment spectrum JSON file."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Experiment spectrum file must contain a JSON object.")
    validate_experiment_spectrum(payload)
    return payload
