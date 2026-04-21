from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ar_inverse.datasets.build import (
    DEFAULT_TASK3_SMOKE_CONFIG_PATH,
    DEFAULT_TASK3_SMOKE_DATASET_DIR,
    build_dataset_from_config,
)
from ar_inverse.datasets.schema import file_sha256, validate_dataset_manifest, validate_resumable_manifest
from ar_inverse.metadata import missing_forward_metadata_keys


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_build_dataset_from_config_writes_resumable_manifest_and_reuses_rows(tmp_path) -> None:
    output_dir = tmp_path / "dataset"
    run_metadata_path = tmp_path / "run_metadata.json"

    manifest_path, _ = build_dataset_from_config(
        DEFAULT_TASK3_SMOKE_CONFIG_PATH,
        output_dir=output_dir,
        run_metadata_path=run_metadata_path,
        force=True,
    )
    manifest = _load_json(manifest_path)
    validate_resumable_manifest(manifest)
    validate_dataset_manifest(manifest)

    assert manifest["dataset_id"] == "task3_orchestration_smoke_v1"
    assert len(manifest["plan"]) == 3
    assert len(manifest["rows"]) == 3
    assert {entry["status"] for entry in manifest["plan"]} == {"completed"}
    assert {entry["reused_existing_output"] for entry in manifest["plan"]} == {False}

    first_run_metadata = _load_json(run_metadata_path)
    assert first_run_metadata["generated_rows"] == 3
    assert first_run_metadata["reused_rows"] == 0

    build_dataset_from_config(
        DEFAULT_TASK3_SMOKE_CONFIG_PATH,
        output_dir=output_dir,
        run_metadata_path=run_metadata_path,
    )
    resumed_manifest = _load_json(manifest_path)
    resumed_run_metadata = _load_json(run_metadata_path)

    assert {entry["status"] for entry in resumed_manifest["plan"]} == {"completed"}
    assert {entry["reused_existing_output"] for entry in resumed_manifest["plan"]} == {True}
    assert resumed_run_metadata["generated_rows"] == 0
    assert resumed_run_metadata["reused_rows"] == 3


def test_repository_task3_smoke_dataset_has_complete_metadata_and_hashes() -> None:
    manifest_path = DEFAULT_TASK3_SMOKE_DATASET_DIR / "dataset.json"
    assert manifest_path.exists()

    manifest = _load_json(manifest_path)
    validate_resumable_manifest(manifest)
    validate_dataset_manifest(manifest)

    assert len(manifest["rows"]) == 3
    for row in manifest["rows"]:
        assert missing_forward_metadata_keys(row["forward_metadata"]) == ()
        output_ref = row["forward_output_ref"]
        output_path = manifest_path.parent / output_ref["path"]
        assert output_path.exists()
        assert output_ref["sha256"] == file_sha256(output_path)

        payload = _load_json(output_path)
        assert payload["request"] == row["forward_request"]
        assert payload["metadata"] == row["forward_metadata"]


def test_dataset_generation_cli_writes_manifest(tmp_path) -> None:
    output_dir = tmp_path / "cli_dataset"
    run_metadata_path = tmp_path / "cli_run_metadata.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/datasets/build_dataset.py",
            "--config",
            str(DEFAULT_TASK3_SMOKE_CONFIG_PATH),
            "--output-dir",
            str(output_dir),
            "--run-metadata",
            str(run_metadata_path),
            "--force",
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    assert str(output_dir / "dataset.json") in result.stdout
    assert str(run_metadata_path) in result.stdout
    manifest = _load_json(output_dir / "dataset.json")
    validate_resumable_manifest(manifest)
    assert _load_json(run_metadata_path)["generated_rows"] == 3
