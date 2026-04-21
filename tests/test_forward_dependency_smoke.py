from __future__ import annotations

import importlib

import numpy as np

from ar_inverse.forward_client import generate_fit_layer_smoke_payload
from ar_inverse.metadata import REQUIRED_FORWARD_METADATA_KEYS, missing_forward_metadata_keys


def test_forward_package_is_importable() -> None:
    forward = importlib.import_module("forward")

    assert hasattr(forward, "FitLayerSpectrumRequest")
    assert hasattr(forward, "generate_spectrum_from_fit_layer")


def test_fit_layer_forward_smoke_generates_finite_spectrum_and_metadata() -> None:
    payload = generate_fit_layer_smoke_payload()
    metadata = payload["metadata"]

    assert payload["request_kind"] == "fit_layer"
    assert payload["schema_version"] == metadata["output_schema_version"]
    assert missing_forward_metadata_keys(metadata) == ()
    assert set(REQUIRED_FORWARD_METADATA_KEYS).issubset(metadata)
    assert metadata["forward_interface_version"]
    assert metadata["pairing_convention_id"]
    assert metadata["formal_baseline_record"]
    assert metadata["formal_baseline_selection_rule"]
    assert metadata["projection_config"]
    assert metadata["git_commit"]
    assert "git_dirty" in metadata

    bias = np.asarray(payload["bias_mev"], dtype=float)
    conductance = np.asarray(payload["conductance"], dtype=float)

    assert len(bias) == 41
    assert len(conductance) == 41
    assert np.all(np.isfinite(conductance))
    assert payload["transport_summary"]["num_channels"] > 0
