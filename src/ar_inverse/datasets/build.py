"""Dataset generation orchestration through the external forward interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ar_inverse.direction import (
    SUPPORTED_DIRECTION_MODES,
    direction_block_from_forward_payload,
    validate_direction_config,
)
from ar_inverse.datasets.sampling import (
    DIRECTIONAL_SMOKE_SAMPLING_POLICY_ID,
    SMOKE_SAMPLING_POLICY_ID,
    SmokeSampleSpec,
    deterministic_directional_smoke_samples,
    deterministic_smoke_samples,
    directional_smoke_sampling_policy,
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
DEFAULT_TASK8_DIRECTIONAL_CONFIG_PATH = Path("configs/datasets/task8_directional_smoke_dataset.json")
DEFAULT_TASK8_DIRECTIONAL_DATASET_DIR = Path("outputs/datasets/task8_directional_smoke")
DEFAULT_TASK8_DIRECTIONAL_RUN_METADATA_PATH = Path("outputs/runs/task8_directional_dataset_run_metadata.json")


def _request_from_sample(sample: SmokeSampleSpec):
    forward = import_forward_module("forward")
    transport = _transport_from_sample(forward, sample)
    return forward.FitLayerSpectrumRequest(
        pairing_controls=dict(sample.pairing_controls),
        pairing_control_mode="delta_from_baseline_meV",
        allow_weak_delta_zx_s=False,
        transport=transport,
        bias_grid=forward.BiasGrid(**sample.bias_grid),
        request_label=sample.row_id,
    )


def _transport_from_sample(forward: Any, sample: SmokeSampleSpec):
    direction = sample.direction
    controls = dict(sample.transport_controls)
    if not direction:
        return forward.TransportControls(**controls)

    mode = direction.get("direction_mode")
    if mode in SUPPORTED_DIRECTION_MODES:
        controls.pop("interface_angle", None)
        controls.pop("direction_mode", None)
        return forward.transport_with_direction_mode(str(mode), **controls)

    if mode is None:
        controls["interface_angle"] = float(direction["interface_angle"])
        controls.pop("direction_mode", None)
        return forward.TransportControls(**controls)

    raise ValueError(f"Unsupported direction_mode {mode!r}.")


def _generate_result_from_sample(forward: Any, sample: SmokeSampleSpec):
    request = _request_from_sample(sample)
    spread = (sample.direction or {}).get("directional_spread")
    if spread:
        directional_spread = forward.DirectionalSpread(
            direction_mode=str(spread.get("direction_mode") or sample.direction["direction_mode"]),
            half_width=float(spread["half_width"]),
            num_samples=int(spread["num_samples"]),
        )
        return forward.generate_spread_spectrum_from_fit_layer(request, directional_spread)
    return forward.generate_spectrum_from_fit_layer(request)


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
        result = _generate_result_from_sample(forward, sample)
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


def task8_directional_dataset_config() -> dict[str, Any]:
    """Return the canonical Task 8 directional smoke dataset config."""

    return {
        "dataset_id": "task8_directional_smoke_v1",
        "description": "Direction-aware smoke dataset covering supported named modes and narrow spread.",
        "output_dir": DEFAULT_TASK8_DIRECTIONAL_DATASET_DIR.as_posix(),
        "run_metadata_path": DEFAULT_TASK8_DIRECTIONAL_RUN_METADATA_PATH.as_posix(),
        "sampling_policy_id": DIRECTIONAL_SMOKE_SAMPLING_POLICY_ID,
        "allow_diagnostic_raw_angles": False,
        "sampling_policy": directional_smoke_sampling_policy(),
        "samples": [sample.to_dict() for sample in deterministic_directional_smoke_samples()],
    }


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


def sample_from_config(
    sample: dict[str, Any],
    *,
    allow_diagnostic_raw_angles: bool = False,
) -> SmokeSampleSpec:
    """Convert a config sample mapping into the local sample spec."""

    required = ("row_id", "split", "pairing_controls", "transport_controls")
    missing = [key for key in required if key not in sample]
    if missing:
        raise ValueError(f"Dataset sample config is missing key(s): {', '.join(missing)}.")
    direction = dict(sample["direction"]) if "direction" in sample and sample["direction"] is not None else None
    validate_direction_config(direction, allow_diagnostic_raw_angles=allow_diagnostic_raw_angles)
    return SmokeSampleSpec(
        row_id=str(sample["row_id"]),
        split=str(sample["split"]),
        pairing_controls={str(key): float(value) for key, value in dict(sample["pairing_controls"]).items()},
        transport_controls=dict(sample["transport_controls"]),
        direction=direction,
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
    run_metadata_path: Path | str | None = None,
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
    allow_diagnostic_raw_angles = bool(config.get("allow_diagnostic_raw_angles", False))
    output_path = Path(output_dir or config.get("output_dir") or DEFAULT_TASK3_SMOKE_DATASET_DIR)
    spectra_dir = output_path / "forward_outputs"
    manifest_path = output_path / "dataset.json"

    output_path.mkdir(parents=True, exist_ok=True)
    spectra_dir.mkdir(parents=True, exist_ok=True)

    samples = [
        sample_from_config(sample, allow_diagnostic_raw_angles=allow_diagnostic_raw_angles)
        for sample in config["samples"]
    ]
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

        result = _generate_result_from_sample(forward, sample)
        payload = result.to_dict()
        spectrum_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        row = make_dataset_row(
            row_id=sample.row_id,
            sampling_policy_id=sampling_policy_id,
            split=sample.split,
            forward_request=payload["request"],
            forward_output_ref_payload=forward_output_ref(spectrum_path, base_dir=output_path),
            forward_metadata=payload["metadata"],
            direction=(
                direction_block_from_forward_payload(payload, configured_direction=sample.direction)
                if sample.direction is not None
                else None
            ),
            controls={
                "fit_layer_pairing_controls": dict(sample.pairing_controls),
                "transport_controls": dict(sample.transport_controls),
                "direction": dict(sample.direction) if sample.direction is not None else None,
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

    run_metadata_output_path = Path(run_metadata_path or config.get("run_metadata_path") or DEFAULT_TASK3_SMOKE_RUN_METADATA_PATH)
    run_metadata_output_path.parent.mkdir(parents=True, exist_ok=True)
    default_run_kind = (
        "task8_directional_dataset_generation"
        if any(sample.direction for sample in samples)
        else "legacy_task3_dataset_generation_orchestration"
    )
    run_kind = str(config.get("run_kind", default_run_kind))
    run_metadata = {
        "run_kind": run_kind,
        "dataset_manifest": manifest_path.as_posix(),
        "dataset_id": dataset_id,
        "source_config": config_file.as_posix(),
        "sampling_policy_id": sampling_policy_id,
        "num_rows": len(rows),
        "generated_rows": generated_count,
        "reused_rows": reused_count,
        "force": bool(force),
        "allow_diagnostic_raw_angles": allow_diagnostic_raw_angles,
        "forward_metadata_family": rows[0]["forward_metadata"],
    }
    run_metadata_output_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path, run_metadata_output_path
