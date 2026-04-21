from __future__ import annotations

import numpy as np
import pytest
import sys

from ar_inverse.forward_dependency import ForwardDependencyError, configure_forward_import_path, import_forward_module
from ar_inverse.forward_client import generate_fit_layer_smoke_payload
from ar_inverse.metadata import REQUIRED_FORWARD_METADATA_KEYS, missing_forward_metadata_keys


def test_forward_package_is_importable() -> None:
    forward = import_forward_module("forward")

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


def test_forward_source_env_path_is_explicit_and_portable(monkeypatch, tmp_path) -> None:
    fake_src = tmp_path / "forward_source"
    fake_package = fake_src / "forward"
    fake_package.mkdir(parents=True)
    (fake_package / "__init__.py").write_text("", encoding="utf-8")

    monkeypatch.setenv("LNO327_FORWARD_SRC", str(fake_src))
    monkeypatch.setattr(sys, "path", list(sys.path))

    assert configure_forward_import_path() == fake_src.resolve()


def test_missing_forward_dependency_error_is_actionable(monkeypatch) -> None:
    import ar_inverse.forward_dependency as dependency

    def missing_forward(_: str):
        raise ModuleNotFoundError("No module named 'forward'", name="forward")

    monkeypatch.delenv("LNO327_FORWARD_SRC", raising=False)
    monkeypatch.delenv("LNO327_FORWARD_REPO", raising=False)
    monkeypatch.setattr(dependency.importlib, "import_module", missing_forward)

    with pytest.raises(ForwardDependencyError) as exc_info:
        dependency.import_forward_module("forward")

    message = str(exc_info.value)
    assert "Missing external forward interface package `forward`" in message
    assert "python -m pip install -e /path/to/forward-repo" in message
    assert "LNO327_FORWARD_SRC" in message
    assert "LNO327_FORWARD_REPO" in message
    assert "will not copy or reimplement forward physics code" in message
