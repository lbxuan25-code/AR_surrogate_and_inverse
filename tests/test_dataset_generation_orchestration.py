from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ar_inverse.datasets.build import (
    DEFAULT_TASK3_SMOKE_CONFIG_PATH,
    DEFAULT_TASK3_SMOKE_DATASET_DIR,
    DEFAULT_TASK8_DIRECTIONAL_CONFIG_PATH,
    DEFAULT_TASK8_DIRECTIONAL_DATASET_DIR,
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
    assert first_run_metadata["run_kind"] == "legacy_task3_dataset_generation_orchestration"
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


def test_task8_directional_smoke_dataset_has_direction_blocks() -> None:
    manifest_path = DEFAULT_TASK8_DIRECTIONAL_DATASET_DIR / "dataset.json"
    run_metadata_path = Path("outputs/runs/task8_directional_dataset_run_metadata.json")
    assert manifest_path.exists()
    assert run_metadata_path.exists()

    manifest = _load_json(manifest_path)
    run_metadata = _load_json(run_metadata_path)
    validate_resumable_manifest(manifest)
    validate_dataset_manifest(manifest)

    assert run_metadata["run_kind"] == "task8_directional_dataset_generation"
    assert run_metadata["dataset_manifest"] == str(manifest_path)
    regimes = {row["direction"]["direction_regime"] for row in manifest["rows"]}
    assert regimes == {
        "inplane_100_no_spread",
        "inplane_110_no_spread",
        "named_mode_narrow_spread",
    }
    assert all(row["dataset_row_schema_version"] == "ar_inverse_dataset_row_v2" for row in manifest["rows"])
    for row in manifest["rows"]:
        assert row["direction"]["forward_direction_provenance"]["request_transport"]
        if row["direction"]["direction_regime"] == "named_mode_narrow_spread":
            assert row["direction"]["directional_spread"]["half_width"] > 0
            assert row["direction"]["directional_spread"]["num_samples"] == 3


def test_directional_dataset_config_rejects_unsupported_modes(tmp_path) -> None:
    config = _load_json(DEFAULT_TASK8_DIRECTIONAL_CONFIG_PATH)
    config["output_dir"] = str(tmp_path / "bad_dataset")
    config["run_metadata_path"] = str(tmp_path / "bad_run_metadata.json")
    config["samples"][0]["direction"] = {"direction_mode": "c_axis"}
    config_path = tmp_path / "unsupported_direction.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported direction_mode"):
        build_dataset_from_config(config_path, force=True)


def test_directional_dataset_config_rejects_too_wide_spread(tmp_path) -> None:
    config = _load_json(DEFAULT_TASK8_DIRECTIONAL_CONFIG_PATH)
    config["output_dir"] = str(tmp_path / "bad_spread_dataset")
    config["run_metadata_path"] = str(tmp_path / "bad_spread_run_metadata.json")
    config["samples"][2]["direction"]["directional_spread"]["half_width"] = 0.2
    config_path = tmp_path / "wide_spread.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="pi/32"):
        build_dataset_from_config(config_path, force=True)


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
