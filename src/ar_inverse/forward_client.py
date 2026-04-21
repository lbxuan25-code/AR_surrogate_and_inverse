"""Thin client for the external stable `forward` interface."""

from __future__ import annotations

import json
from pathlib import Path

from forward import BiasGrid, FitLayerSpectrumRequest, TransportControls, generate_spectrum_from_fit_layer
from forward.schema import FORWARD_OUTPUT_SCHEMA_VERSION

from ar_inverse.metadata import assert_forward_metadata_complete

DEFAULT_SMOKE_PAYLOAD_PATH = Path("outputs/datasets/fit_layer_forward_smoke_payload.json")
DEFAULT_SMOKE_RUN_METADATA_PATH = Path("outputs/runs/task1_forward_smoke_run_metadata.json")


def build_smoke_fit_layer_request() -> FitLayerSpectrumRequest:
    """Build a small deterministic fit-layer request for dependency smoke tests."""

    return FitLayerSpectrumRequest(
        pairing_controls={"delta_zz_s": 0.25, "delta_perp_x": -0.1},
        transport=TransportControls(interface_angle=0.0, barrier_z=0.5, gamma=1.0, temperature_kelvin=3.0, nk=11),
        bias_grid=BiasGrid(bias_min_mev=-20.0, bias_max_mev=20.0, num_bias=41),
        request_label="ar_inverse_task1_fit_layer_smoke",
    )


def generate_fit_layer_smoke_payload() -> dict[str, object]:
    """Generate one fit-layer spectrum and validate required forward metadata."""

    request = build_smoke_fit_layer_request()
    result = generate_spectrum_from_fit_layer(request)
    payload = result.to_dict()

    if payload["schema_version"] != FORWARD_OUTPUT_SCHEMA_VERSION:
        raise ValueError(
            f"Unexpected forward output schema: {payload['schema_version']!r}; "
            f"expected {FORWARD_OUTPUT_SCHEMA_VERSION!r}."
        )
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("Forward payload does not contain a metadata mapping.")
    assert_forward_metadata_complete(metadata)
    return payload


def write_smoke_payload(path: Path | str = DEFAULT_SMOKE_PAYLOAD_PATH) -> Path:
    """Write the Task 1 forward smoke payload and return its path."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = generate_fit_layer_smoke_payload()
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_task1_smoke_artifacts(
    payload_path: Path | str = DEFAULT_SMOKE_PAYLOAD_PATH,
    run_metadata_path: Path | str = DEFAULT_SMOKE_RUN_METADATA_PATH,
) -> tuple[Path, Path]:
    """Write the Task 1 payload plus local run metadata."""

    payload_output_path = Path(payload_path)
    run_metadata_output_path = Path(run_metadata_path)
    payload_output_path.parent.mkdir(parents=True, exist_ok=True)
    run_metadata_output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = generate_fit_layer_smoke_payload()
    payload_output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    run_metadata = {
        "run_kind": "task1_forward_dependency_smoke",
        "payload_path": str(payload_output_path),
        "request_kind": payload["request_kind"],
        "output_schema_version": payload["schema_version"],
        "num_bias": len(payload["bias_mev"]),
        "num_conductance": len(payload["conductance"]),
        "forward_metadata": payload["metadata"],
    }
    run_metadata_output_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload_output_path, run_metadata_output_path
