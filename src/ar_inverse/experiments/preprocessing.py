"""Experiment preprocessing metadata and operations."""

from __future__ import annotations

from typing import Any

import numpy as np

PREPROCESSING_SCHEMA_VERSION = "ar_inverse_experiment_preprocessing_v1"


def default_preprocessing_config() -> dict[str, Any]:
    """Return the default explicit no-surprises preprocessing config."""

    return {
        "preprocessing_schema_version": PREPROCESSING_SCHEMA_VERSION,
        "operations": [
            {
                "operation": "identity",
                "description": "No smoothing, background subtraction, or normalization applied.",
            }
        ],
    }


def validate_preprocessing_config(config: dict[str, Any]) -> None:
    """Validate preprocessing metadata."""

    if config.get("preprocessing_schema_version") != PREPROCESSING_SCHEMA_VERSION:
        raise ValueError("Unsupported or missing preprocessing_schema_version.")
    operations = config.get("operations")
    if not isinstance(operations, list) or not operations:
        raise ValueError("Preprocessing config must include a non-empty operations list.")
    for operation in operations:
        if not isinstance(operation, dict) or "operation" not in operation:
            raise ValueError("Every preprocessing operation must be a mapping with an operation name.")


def apply_preprocessing(
    experiment: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> tuple[dict[str, list[float]], dict[str, Any]]:
    """Apply the configured preprocessing and return processed arrays plus metadata."""

    preprocessing = config or default_preprocessing_config()
    validate_preprocessing_config(preprocessing)

    bias = np.asarray(experiment["bias_mev"], dtype=np.float64)
    conductance = np.asarray(experiment["conductance"], dtype=np.float64)
    applied: list[dict[str, Any]] = []
    processed = conductance.copy()

    for operation in preprocessing["operations"]:
        name = operation["operation"]
        if name == "identity":
            applied.append(dict(operation))
        elif name == "scale_to_mean":
            target_mean = float(operation.get("target_mean", 1.0))
            current_mean = float(np.mean(processed))
            if current_mean == 0.0:
                raise ValueError("Cannot scale conductance with zero mean.")
            processed = processed * (target_mean / current_mean)
            applied.append({**operation, "input_mean": current_mean})
        else:
            raise ValueError(f"Unsupported preprocessing operation: {name!r}.")

    metadata = {
        "preprocessing_schema_version": PREPROCESSING_SCHEMA_VERSION,
        "operations": applied,
        "separated_from_physical_inference": True,
    }
    return {
        "bias_mev": [float(value) for value in bias],
        "conductance": [float(value) for value in processed],
    }, metadata
