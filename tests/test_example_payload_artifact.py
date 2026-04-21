from __future__ import annotations

import json

import numpy as np

from ar_inverse.forward_client import (
    DEFAULT_SMOKE_PAYLOAD_PATH,
    DEFAULT_SMOKE_RUN_METADATA_PATH,
    write_smoke_payload,
)
from ar_inverse.metadata import missing_forward_metadata_keys


def test_write_smoke_payload_records_forward_metadata(tmp_path) -> None:
    output_path = write_smoke_payload(tmp_path / "fit_layer_forward_smoke_payload.json")

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    metadata = payload["metadata"]

    assert output_path.exists()
    assert payload["request_kind"] == "fit_layer"
    assert missing_forward_metadata_keys(metadata) == ()
    assert np.all(np.isfinite(np.asarray(payload["conductance"], dtype=float)))


def test_repository_example_payload_exists_and_records_metadata() -> None:
    assert DEFAULT_SMOKE_PAYLOAD_PATH.exists()

    payload = json.loads(DEFAULT_SMOKE_PAYLOAD_PATH.read_text(encoding="utf-8"))

    assert payload["request_kind"] == "fit_layer"
    assert missing_forward_metadata_keys(payload["metadata"]) == ()


def test_repository_run_metadata_exists_and_records_forward_metadata() -> None:
    assert DEFAULT_SMOKE_RUN_METADATA_PATH.exists()

    run_metadata = json.loads(DEFAULT_SMOKE_RUN_METADATA_PATH.read_text(encoding="utf-8"))

    assert run_metadata["run_kind"] == "task1_forward_dependency_smoke"
    assert run_metadata["payload_path"] == str(DEFAULT_SMOKE_PAYLOAD_PATH)
    assert missing_forward_metadata_keys(run_metadata["forward_metadata"]) == ()
