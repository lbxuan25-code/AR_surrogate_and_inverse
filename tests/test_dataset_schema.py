from __future__ import annotations

import json
from pathlib import Path

import pytest

from ar_inverse.datasets.build import DEFAULT_TASK2_SMOKE_DATASET_DIR, build_task2_smoke_dataset
from ar_inverse.datasets.sampling import SMOKE_SAMPLING_POLICY_ID
from ar_inverse.datasets.schema import (
    DATASET_ROW_SCHEMA_VERSION,
    SPLIT_LABELS,
    file_sha256,
    validate_dataset_manifest,
    validate_dataset_row,
)
from ar_inverse.metadata import REQUIRED_FORWARD_METADATA_KEYS, missing_forward_metadata_keys


def _load_manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task2_smoke_dataset_builder_writes_valid_manifest(tmp_path) -> None:
    manifest_path, run_metadata_path = build_task2_smoke_dataset(
        tmp_path / "task2_smoke_fit_layer",
        tmp_path / "task2_smoke_dataset_run_metadata.json",
    )

    manifest = _load_manifest(manifest_path)
    validate_dataset_manifest(manifest)

    rows = manifest["rows"]
    assert len(rows) == 3
    assert {row["split"] for row in rows} == set(SPLIT_LABELS)
    assert {row["sampling_policy_id"] for row in rows} == {SMOKE_SAMPLING_POLICY_ID}

    for row in rows:
        assert row["dataset_row_schema_version"] == DATASET_ROW_SCHEMA_VERSION
        assert set(REQUIRED_FORWARD_METADATA_KEYS).issubset(row["forward_metadata"])
        assert missing_forward_metadata_keys(row["forward_metadata"]) == ()

        output_ref = row["forward_output_ref"]
        output_path = manifest_path.parent / output_ref["path"]
        assert output_path.exists()
        assert output_ref["sha256"] == file_sha256(output_path)

        forward_payload = json.loads(output_path.read_text(encoding="utf-8"))
        assert forward_payload["request"] == row["forward_request"]
        assert forward_payload["metadata"] == row["forward_metadata"]

    run_metadata = json.loads(run_metadata_path.read_text(encoding="utf-8"))
    assert run_metadata["run_kind"] == "task2_deterministic_smoke_dataset"
    assert run_metadata["num_rows"] == 3
    assert run_metadata["sampling_policy_id"] == SMOKE_SAMPLING_POLICY_ID


def test_repository_task2_smoke_dataset_exists_and_is_valid() -> None:
    manifest_path = DEFAULT_TASK2_SMOKE_DATASET_DIR / "dataset.json"
    assert manifest_path.exists()

    manifest = _load_manifest(manifest_path)
    validate_dataset_manifest(manifest)

    rows = manifest["rows"]
    assert len(rows) == 3
    for row in rows:
        output_ref = row["forward_output_ref"]
        output_path = manifest_path.parent / output_ref["path"]
        assert output_path.exists()
        assert output_ref["sha256"] == file_sha256(output_path)
        assert missing_forward_metadata_keys(row["forward_metadata"]) == ()


def test_dataset_row_validation_rejects_missing_required_fields() -> None:
    with pytest.raises(ValueError, match="missing required key"):
        validate_dataset_row({"row_id": "incomplete"})
