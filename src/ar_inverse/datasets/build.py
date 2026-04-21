"""Dataset generation orchestration through the external forward interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ar_inverse.datasets.sampling import (
    SMOKE_SAMPLING_POLICY_ID,
    SmokeSampleSpec,
    deterministic_smoke_samples,
    smoke_sampling_policy,
)
from ar_inverse.datasets.schema import (
    DATASET_MANIFEST_SCHEMA_VERSION,
    RESUMABLE_MANIFEST_SCHEMA_VERSION,
    file_sha256,
    forward_output_ref,
    make_dataset_row,
    validate_dataset_manifest,
    validate_dataset_row,
    validate_resumable_manifest,
)
from ar_inverse.forward_dependency import import_forward_module

DEFAULT_TASK2_SMOKE_DATASET_DIR = Path("outputs/datasets/task2_smoke_fit_layer")
DEFAULT_TASK2_SMOKE_RUN_METADATA_PATH = Path("outputs/runs/task2_smoke_dataset_run_metadata.json")
DEFAULT_TASK3_SMOKE_CONFIG_PATH = Path("configs/datasets/task3_smoke_dataset.json")
DEFAULT_TASK3_SMOKE_DATASET_DIR = Path("outputs/datasets/task3_orchestration_smoke")
DEFAULT_TASK3_SMOKE_RUN_METADATA_PATH = Path("outputs/runs/task3_dataset_generation_run_metadata.json")


def _request_from_sample(sample: SmokeSampleSpec):
    forward = import_forward_module("forward")
    return forward.FitLayerSpectrumRequest(
        pairing_controls=dict(sample.pairing_controls),
        pairing_control_mode="delta_from_baseline_meV",
        allow_weak_delta_zx_s=False,
        transport=forward.TransportControls(**sample.transport_controls),
        bias_grid=forward.BiasGrid(**sample.bias_grid),
        request_label=sample.row_id,
    )


def build_task2_smoke_dataset(
    dataset_dir: Path | str = DEFAULT_TASK2_SMOKE_DATASET_DIR,
    run_metadata_path: Path | str = DEFAULT_TASK2_SMOKE_RUN_METADATA_PATH,
) -> tuple[Path, Path]:
    """Generate the tiny deterministic Task 2 smoke dataset."""

    forward = import_forward_module("forward")
    output_dir = Path(dataset_dir)
    spectra_dir = output_dir / "forward_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    spectra_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    for sample in deterministic_smoke_samples():
        request = _request_from_sample(sample)
        result = forward.generate_spectrum_from_fit_layer(request)
        payload = result.to_dict()

        spectrum_path = spectra_dir / f"{sample.row_id}.json"
        spectrum_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        row = make_dataset_row(
            row_id=sample.row_id,
            sampling_policy_id=SMOKE_SAMPLING_POLICY_ID,
            split=sample.split,
            forward_request=payload["request"],
            forward_output_ref_payload=forward_output_ref(spectrum_path, base_dir=output_dir),
            forward_metadata=payload["metadata"],
            controls={
                "fit_layer_pairing_controls": dict(sample.pairing_controls),
                "transport_controls": dict(sample.transport_controls),
                "bias_grid": dict(sample.bias_grid),
            },
        )
        rows.append(row)

    manifest = {
        "dataset_manifest_schema_version": DATASET_MANIFEST_SCHEMA_VERSION,
        "dataset_id": "task2_smoke_fit_layer_v1",
        "description": "Small deterministic smoke dataset for Task 2 schema validation.",
        "sampling_policy": smoke_sampling_policy(),
        "sampling_policy_id": SMOKE_SAMPLING_POLICY_ID,
        "rows": rows,
    }
    validate_dataset_manifest(manifest)

    manifest_path = output_dir / "dataset.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    run_metadata_output_path = Path(run_metadata_path)
    run_metadata_output_path.parent.mkdir(parents=True, exist_ok=True)
    run_metadata = {
        "run_kind": "task2_deterministic_smoke_dataset",
        "dataset_manifest": manifest_path.as_posix(),
        "dataset_id": manifest["dataset_id"],
        "sampling_policy_id": SMOKE_SAMPLING_POLICY_ID,
        "num_rows": len(rows),
        "splits": sorted({str(row["split"]) for row in rows}),
        "forward_metadata_family": rows[0]["forward_metadata"],
    }
    run_metadata_output_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path, run_metadata_output_path


def load_dataset_config(path: Path | str) -> dict[str, Any]:
    """Load a dataset generation config from JSON."""

    config_path = Path(path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Dataset config must be a JSON object.")

    required = ("dataset_id", "sampling_policy_id", "samples")
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Dataset config is missing required key(s): {', '.join(missing)}.")
    if not isinstance(config["samples"], list) or not config["samples"]:
        raise ValueError("Dataset config must contain a non-empty samples list.")
    return config


def sample_from_config(sample: dict[str, Any]) -> SmokeSampleSpec:
    """Convert a config sample mapping into the local sample spec."""

    required = ("row_id", "split", "pairing_controls", "transport_controls")
    missing = [key for key in required if key not in sample]
    if missing:
        raise ValueError(f"Dataset sample config is missing key(s): {', '.join(missing)}.")
    return SmokeSampleSpec(
        row_id=str(sample["row_id"]),
        split=str(sample["split"]),
        pairing_controls={str(key): float(value) for key, value in dict(sample["pairing_controls"]).items()},
        transport_controls=dict(sample["transport_controls"]),
        bias_grid=dict(sample.get("bias_grid", {})) or {
            "bias_min_mev": -20.0,
            "bias_max_mev": 20.0,
            "num_bias": 41,
        },
    )


def _plan_entry(
    *,
    sample: SmokeSampleSpec,
    sampling_policy_id: str,
    status: str,
    output_path: str,
    reused_existing_output: bool,
) -> dict[str, object]:
    return {
        "row_id": sample.row_id,
        "split": sample.split,
        "sampling_policy_id": sampling_policy_id,
        "status": status,
        "forward_output_path": output_path,
        "reused_existing_output": reused_existing_output,
    }


def _write_resumable_manifest(
    *,
    manifest_path: Path,
    dataset_id: str,
    description: str,
    sampling_policy_id: str,
    sampling_policy: dict[str, object],
    config_path: Path,
    plan: list[dict[str, object]],
    rows: list[dict[str, object]],
) -> None:
    manifest = {
        "dataset_manifest_schema_version": DATASET_MANIFEST_SCHEMA_VERSION,
        "resumable_manifest_schema_version": RESUMABLE_MANIFEST_SCHEMA_VERSION,
        "dataset_id": dataset_id,
        "description": description,
        "sampling_policy": sampling_policy,
        "sampling_policy_id": sampling_policy_id,
        "source_config": config_path.as_posix(),
        "plan": plan,
        "rows": rows,
    }
    validate_resumable_manifest(manifest)
    if rows:
        validate_dataset_manifest(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_reusable_rows(manifest_path: Path, output_dir: Path) -> dict[str, dict[str, object]]:
    if not manifest_path.exists():
        return {}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        return {}

    reusable: dict[str, dict[str, object]] = {}
    for row in manifest.get("rows", []):
        if not isinstance(row, dict):
            continue
        try:
            validate_dataset_row(row)
            output_ref = row["forward_output_ref"]
            output_path = output_dir / str(output_ref["path"])
            if output_path.exists() and str(output_ref["sha256"]) == file_sha256(output_path):
                reusable[str(row["row_id"])] = row
        except (KeyError, TypeError, ValueError):
            continue
    return reusable


def build_dataset_from_config(
    config_path: Path | str,
    *,
    output_dir: Path | str | None = None,
    run_metadata_path: Path | str = DEFAULT_TASK3_SMOKE_RUN_METADATA_PATH,
    force: bool = False,
) -> tuple[Path, Path]:
    """Generate a dataset from a config, resuming completed rows when possible."""

    forward = import_forward_module("forward")
    config_file = Path(config_path)
    config = load_dataset_config(config_file)
    dataset_id = str(config["dataset_id"])
    description = str(config.get("description", "Forward-generated dataset."))
    sampling_policy_id = str(config["sampling_policy_id"])
    sampling_policy = dict(config.get("sampling_policy", {"sampling_policy_id": sampling_policy_id}))
    output_path = Path(output_dir or config.get("output_dir") or DEFAULT_TASK3_SMOKE_DATASET_DIR)
    spectra_dir = output_path / "forward_outputs"
    manifest_path = output_path / "dataset.json"

    output_path.mkdir(parents=True, exist_ok=True)
    spectra_dir.mkdir(parents=True, exist_ok=True)

    samples = [sample_from_config(sample) for sample in config["samples"]]
    reusable_rows = {} if force else _load_reusable_rows(manifest_path, output_path)

    rows: list[dict[str, object]] = []
    plan: list[dict[str, object]] = [
        _plan_entry(
            sample=sample,
            sampling_policy_id=sampling_policy_id,
            status="pending",
            output_path=(Path("forward_outputs") / f"{sample.row_id}.json").as_posix(),
            reused_existing_output=False,
        )
        for sample in samples
    ]
    generated_count = 0
    reused_count = 0

    for index, sample in enumerate(samples):
        spectrum_path = spectra_dir / f"{sample.row_id}.json"
        reusable_row = reusable_rows.get(sample.row_id)
        if reusable_row is not None:
            rows.append(reusable_row)
            plan[index] = _plan_entry(
                sample=sample,
                sampling_policy_id=sampling_policy_id,
                status="completed",
                output_path=(Path("forward_outputs") / f"{sample.row_id}.json").as_posix(),
                reused_existing_output=True,
            )
            reused_count += 1
            _write_resumable_manifest(
                manifest_path=manifest_path,
                dataset_id=dataset_id,
                description=description,
                sampling_policy_id=sampling_policy_id,
                sampling_policy=sampling_policy,
                config_path=config_file,
                plan=plan,
                rows=rows,
            )
            continue

        request = _request_from_sample(sample)
        result = forward.generate_spectrum_from_fit_layer(request)
        payload = result.to_dict()
        spectrum_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        row = make_dataset_row(
            row_id=sample.row_id,
            sampling_policy_id=sampling_policy_id,
            split=sample.split,
            forward_request=payload["request"],
            forward_output_ref_payload=forward_output_ref(spectrum_path, base_dir=output_path),
            forward_metadata=payload["metadata"],
            controls={
                "fit_layer_pairing_controls": dict(sample.pairing_controls),
                "transport_controls": dict(sample.transport_controls),
                "bias_grid": dict(sample.bias_grid),
            },
        )
        rows.append(row)
        plan[index] = _plan_entry(
            sample=sample,
            sampling_policy_id=sampling_policy_id,
            status="completed",
            output_path=(Path("forward_outputs") / f"{sample.row_id}.json").as_posix(),
            reused_existing_output=False,
        )
        generated_count += 1
        _write_resumable_manifest(
            manifest_path=manifest_path,
            dataset_id=dataset_id,
            description=description,
            sampling_policy_id=sampling_policy_id,
            sampling_policy=sampling_policy,
            config_path=config_file,
            plan=plan,
            rows=rows,
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_resumable_manifest(manifest)
    validate_dataset_manifest(manifest)

    run_metadata_output_path = Path(run_metadata_path)
    run_metadata_output_path.parent.mkdir(parents=True, exist_ok=True)
    run_metadata = {
        "run_kind": "task3_dataset_generation_orchestration",
        "dataset_manifest": manifest_path.as_posix(),
        "dataset_id": dataset_id,
        "source_config": config_file.as_posix(),
        "sampling_policy_id": sampling_policy_id,
        "num_rows": len(rows),
        "generated_rows": generated_count,
        "reused_rows": reused_count,
        "force": bool(force),
        "forward_metadata_family": rows[0]["forward_metadata"],
    }
    run_metadata_output_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path, run_metadata_output_path
