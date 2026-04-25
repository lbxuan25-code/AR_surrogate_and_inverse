"""Dataset generation orchestration through the external forward interface."""

from __future__ import annotations

import concurrent.futures
import csv
import json
import math
import multiprocessing
import os
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
from ar_inverse.pairing.representation import (
    CANONICAL_PAIRING_CHANNEL_ORDER,
    gauge_fix_pairing_channels,
    serialize_gauge_fixed_pairing_channels,
)

DEFAULT_TASK2_SMOKE_DATASET_DIR = Path("outputs/datasets/task2_smoke_fit_layer")
DEFAULT_TASK2_SMOKE_RUN_METADATA_PATH = Path("outputs/runs/task2_smoke_dataset_run_metadata.json")
DEFAULT_TASK3_SMOKE_CONFIG_PATH = Path("configs/datasets/task3_smoke_dataset.json")
DEFAULT_TASK3_SMOKE_DATASET_DIR = Path("outputs/datasets/task3_orchestration_smoke")
DEFAULT_TASK3_SMOKE_RUN_METADATA_PATH = Path("outputs/runs/task3_dataset_generation_run_metadata.json")
DEFAULT_TASK8_DIRECTIONAL_CONFIG_PATH = Path("configs/datasets/smoke/directional_smoke_dataset.json")
DEFAULT_TASK8_DIRECTIONAL_DATASET_DIR = Path("outputs/datasets/task8_directional_smoke")
DEFAULT_TASK8_DIRECTIONAL_RUN_METADATA_PATH = Path("outputs/runs/task8_directional_dataset_run_metadata.json")


def _request_from_sample(forward: Any, sample: SmokeSampleSpec):
    transport = _transport_from_sample(forward, sample)
    return forward.FitLayerSpectrumRequest(
        pairing_controls=dict(sample.pairing_controls),
        pairing_control_mode=str(sample.pairing_control_mode),
        allow_weak_delta_zx_s=bool(sample.allow_weak_delta_zx_s),
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
    request = _request_from_sample(forward, sample)
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

    required = ("dataset_id", "sampling_policy_id")
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Dataset config is missing required key(s): {', '.join(missing)}.")
    has_samples = isinstance(config.get("samples"), list) and bool(config.get("samples"))
    has_sample_grids = isinstance(config.get("sample_grids"), list) and bool(config.get("sample_grids"))
    has_production_v1_blueprint = str(config.get("dataset_id")) == "production_surrogate_v1" and isinstance(
        config.get("row_budget"), dict
    )
    if not has_samples and not has_sample_grids and not has_production_v1_blueprint:
        raise ValueError("Dataset config must contain a non-empty samples list or sample_grids list.")
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
        group_labels={str(key): str(value) for key, value in dict(sample.get("group_labels", {})).items()},
        pairing_control_mode=str(sample.get("pairing_control_mode", "delta_from_baseline_meV")),
        allow_weak_delta_zx_s=bool(sample.get("allow_weak_delta_zx_s", False)),
        pairing_representation=dict(sample["pairing_representation"]) if isinstance(sample.get("pairing_representation"), dict) else None,
        source_provenance=dict(sample["source_provenance"]) if isinstance(sample.get("source_provenance"), dict) else None,
        bias_grid=dict(sample.get("bias_grid", {})) or {
            "bias_min_mev": -20.0,
            "bias_max_mev": 20.0,
            "num_bias": 41,
        },
    )


def materialize_dataset_samples(config: dict[str, Any]) -> list[SmokeSampleSpec]:
    """Expand explicit samples and compact sample grids into concrete sample specs."""

    allow_diagnostic_raw_angles = bool(config.get("allow_diagnostic_raw_angles", False))
    sample_entries: list[dict[str, Any]] = []
    for sample in list(config.get("samples", [])):
        if not isinstance(sample, dict):
            raise ValueError("Dataset config sample entries must be JSON objects.")
        sample_entries.append(sample)
    sample_entries.extend(_expand_sample_grids(config.get("sample_grids", [])))
    if not sample_entries and str(config.get("dataset_id")) == "production_surrogate_v1":
        sample_entries.extend(_expand_production_surrogate_v1_blueprint(config))
    if not sample_entries:
        raise ValueError("Dataset config did not materialize any samples.")
    samples = [
        sample_from_config(sample, allow_diagnostic_raw_angles=allow_diagnostic_raw_angles)
        for sample in sample_entries
    ]
    expected_num_rows = config.get("expected_num_rows")
    if expected_num_rows is not None and int(expected_num_rows) != len(samples):
        raise ValueError(
            f"Dataset config expected_num_rows={expected_num_rows} but materialized {len(samples)} samples."
        )
    row_ids = [sample.row_id for sample in samples]
    if len(set(row_ids)) != len(row_ids):
        raise ValueError("Dataset config materialized duplicate row_id values.")
    return samples


def _expand_production_surrogate_v1_blueprint(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Materialize the P1 production contract into executable local samples."""

    row_budget = dict(config.get("row_budget", {}))
    split_targets = dict(row_budget.get("split_targets", {}))
    required_splits = ("train", "validation", "test")
    missing_splits = [split for split in required_splits if split not in split_targets]
    if missing_splits:
        raise ValueError(f"production_surrogate_v1 row_budget is missing split target(s): {missing_splits}.")

    total_rows = int(row_budget.get("recommended_total_rows", 0))
    split_total = sum(int(split_targets[split]) for split in required_splits)
    if total_rows != split_total:
        raise ValueError(
            f"production_surrogate_v1 recommended_total_rows={total_rows} but split targets sum to {split_total}."
        )

    bias_grid = dict(config.get("fixed_bias_grid", {})) or {
        "bias_min_mev": -40.0,
        "bias_max_mev": 40.0,
        "num_bias": 241,
    }
    nuisance_regimes = (
        "core_sharp",
        "core_transition",
        "core_broad",
        "guard_band_sharp",
        "guard_band_transition",
        "guard_band_broad",
    )
    pairing_roles = _quota_sequence(dict(config.get("pairing_source_composition", {})), total_rows, label="pairing_source_composition")
    direction_regimes = _quota_sequence(
        dict(config.get("direction_contract", {}).get("direction_regime_targets", {})),
        total_rows,
        label="direction_regime_targets",
    )
    tb_regimes = _quota_sequence(dict(config.get("tb_regime_targets", {})), total_rows, label="tb_regime_targets")
    source_records = _load_production_v1_rmft_source_records(config)
    role_counters = {role: 0 for role in set(pairing_roles)}

    samples: list[dict[str, Any]] = []
    global_index = 0
    for split in required_splits:
        for index in range(int(split_targets[split])):
            pairing_role = pairing_roles[global_index]
            nuisance_regime = nuisance_regimes[global_index % len(nuisance_regimes)]
            direction_regime = direction_regimes[global_index]
            tb_regime = tb_regimes[global_index]
            role_index = role_counters[pairing_role]
            role_counters[pairing_role] += 1
            pairing_payload = _production_v1_pairing_payload(
                pairing_role=pairing_role,
                role_index=role_index,
                global_index=global_index,
                source_records=source_records,
            )
            samples.append(
                {
                    "row_id": f"production_v1_{split}_{index:05d}",
                    "split": split,
                    "pairing_controls": pairing_payload["pairing_controls"],
                    "pairing_control_mode": "absolute_meV",
                    "allow_weak_delta_zx_s": pairing_payload["allow_weak_delta_zx_s"],
                    "pairing_representation": pairing_payload["pairing_representation"],
                    "source_provenance": pairing_payload["source_provenance"],
                    "transport_controls": _production_v1_transport_controls(nuisance_regime, index),
                    "direction": _production_v1_direction(direction_regime, index),
                    "group_labels": {
                        "pairing_source_role": pairing_role,
                        "nuisance_regime": nuisance_regime,
                        "tb_regime": tb_regime,
                        "production_contract": "production_surrogate_v1",
                    },
                    "bias_grid": bias_grid,
                }
            )
            global_index += 1
    return samples


def _quota_sequence(quotas: dict[str, Any], total_rows: int, *, label: str) -> list[str]:
    if not quotas:
        raise ValueError(f"production_surrogate_v1 {label} must be a non-empty mapping.")
    normalized = {str(key): int(value) for key, value in quotas.items()}
    quota_total = sum(normalized.values())
    if quota_total != total_rows:
        raise ValueError(f"production_surrogate_v1 {label} sums to {quota_total}, expected {total_rows}.")
    sequence: list[str] = []
    for key, count in normalized.items():
        if count < 0:
            raise ValueError(f"production_surrogate_v1 {label} contains negative count for {key!r}.")
        sequence.extend([key] * count)
    return sequence


def _forward_repo_root_from_config(config: dict[str, Any]) -> Path:
    source_config = dict(config.get("rmft_source_projection", {}))
    if source_config.get("forward_repo_root"):
        return Path(str(source_config["forward_repo_root"]))
    if os.environ.get("LNO327_FORWARD_REPO"):
        return Path(os.environ["LNO327_FORWARD_REPO"])
    if os.environ.get("LNO327_FORWARD_SRC"):
        src_path = Path(os.environ["LNO327_FORWARD_SRC"])
        return src_path.parent if src_path.name == "src" else src_path
    return Path("/home/liubx25/Ni_Research/Projects/AR")


def _load_production_v1_rmft_source_records(config: dict[str, Any]) -> list[dict[str, Any]]:
    source_config = dict(config.get("rmft_source_projection", {}))
    relative_csv = str(source_config.get("projection_examples_csv", "outputs/source/round2_projection_examples.csv"))
    csv_path = _forward_repo_root_from_config(config) / relative_csv
    if not csv_path.exists():
        raise ValueError(
            "production_surrogate_v1 requires the forward repository round-2 projection CSV for "
            f"RMFT-source-aware sampling, but it was not found at {csv_path}."
        )

    records: list[dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            channels = {
                channel: complex(str(row[channel]).strip())
                for channel in CANONICAL_PAIRING_CHANNEL_ORDER
                if channel in row and str(row[channel]).strip()
            }
            if len(channels) != len(CANONICAL_PAIRING_CHANNEL_ORDER):
                continue
            records.append(
                {
                    "source_sample_id": str(row["sample_id"]),
                    "channels": channels,
                }
            )
    if not records:
        raise ValueError(f"No usable RMFT projection records found in {csv_path}.")
    return records


def _production_v1_pairing_payload(
    *,
    pairing_role: str,
    role_index: int,
    global_index: int,
    source_records: list[dict[str, Any]],
) -> dict[str, Any]:
    if pairing_role == "anchor":
        source_indices = [role_index % len(source_records)]
        channels = dict(source_records[source_indices[0]]["channels"])
    elif pairing_role == "neighborhood":
        source_indices = [role_index % len(source_records)]
        channels = _neighborhood_channels(dict(source_records[source_indices[0]]["channels"]), role_index)
    elif pairing_role == "bridge":
        first = (role_index * 7) % len(source_records)
        second = (first + 97 + (role_index % 29)) % len(source_records)
        source_indices = [first, second]
        channels = {
            channel: 0.5 * (
                complex(source_records[first]["channels"][channel])
                + complex(source_records[second]["channels"][channel])
            )
            for channel in CANONICAL_PAIRING_CHANNEL_ORDER
        }
    else:
        raise ValueError(f"Unsupported production pairing_source_role {pairing_role!r}.")

    gauge_fixed = gauge_fix_pairing_channels(channels)
    pairing_representation = serialize_gauge_fixed_pairing_channels(
        gauge_fixed["channels"],
        gauge_anchor_channel=gauge_fixed["gauge_anchor_channel"],
        global_phase_rotation_rad=float(gauge_fixed["global_phase_rotation_rad"]),
        weak_channel_active=bool(gauge_fixed["weak_channel_active"]),
    )
    pairing_controls = {
        channel: float(pairing_representation["channels"][channel]["re"])
        for channel in CANONICAL_PAIRING_CHANNEL_ORDER
    }
    source_sample_ids = [str(source_records[index]["source_sample_id"]) for index in source_indices]
    return {
        "pairing_controls": pairing_controls,
        "allow_weak_delta_zx_s": abs(pairing_controls.get("delta_zx_s", 0.0)) > 0.0,
        "pairing_representation": pairing_representation,
        "source_provenance": {
            "source_family": "Luo RMFT round2 projection examples",
            "source_sample_ids": source_sample_ids,
            "source_indices": source_indices,
            "pairing_source_role": pairing_role,
            "global_materialization_index": global_index,
            "forward_pairing_control_mode": "absolute_meV_real_projection_gauge",
        },
    }


def _neighborhood_channels(channels: dict[str, complex], role_index: int) -> dict[str, complex]:
    scale = 1.0 + _cycle_value(role_index, modulus=17, low=-0.035, high=0.035, offset=5)
    phase = _cycle_value(role_index, modulus=19, low=-0.025, high=0.025, offset=7)
    rotation = complex(math.cos(phase), math.sin(phase))
    return {
        channel: complex(value) * scale * rotation
        for channel, value in channels.items()
    }


def _cycle_value(index: int, *, modulus: int, low: float, high: float, offset: int = 0) -> float:
    step = ((index + offset) % modulus) / max(modulus - 1, 1)
    return low + (high - low) * step


def _production_v1_pairing_controls(pairing_role: str, index: int) -> dict[str, float]:
    if pairing_role == "anchor":
        return {
            "delta_zz_s": _cycle_value(index, modulus=17, low=0.16, high=0.30),
            "delta_perp_x": _cycle_value(index, modulus=13, low=-0.12, high=0.08, offset=3),
        }
    if pairing_role == "neighborhood":
        return {
            "delta_xx_s": _cycle_value(index, modulus=19, low=-0.16, high=-0.03, offset=5),
            "delta_zx_d": _cycle_value(index, modulus=17, low=0.04, high=0.15, offset=7),
        }
    return {
        "delta_perp_z": _cycle_value(index, modulus=23, low=0.06, high=0.18, offset=11),
        "delta_perp_x": _cycle_value(index, modulus=17, low=-0.08, high=0.14, offset=13),
        "delta_zx_d": _cycle_value(index, modulus=13, low=0.03, high=0.16, offset=2),
    }


def _production_v1_transport_controls(nuisance_regime: str, index: int) -> dict[str, float | int]:
    nuisance_windows = {
        "core_sharp": (0.22, 0.45, 0.55, 0.80, 1.4, 2.8),
        "core_transition": (0.35, 0.65, 0.82, 1.10, 2.4, 4.8),
        "core_broad": (0.45, 0.78, 1.12, 1.42, 4.5, 7.0),
        "guard_band_sharp": (0.78, 1.05, 0.60, 0.88, 2.0, 4.2),
        "guard_band_transition": (0.92, 1.22, 0.95, 1.30, 4.0, 7.5),
        "guard_band_broad": (1.08, 1.45, 1.32, 1.75, 7.0, 12.0),
    }
    z_low, z_high, gamma_low, gamma_high, temp_low, temp_high = nuisance_windows[nuisance_regime]
    return {
        "barrier_z": _cycle_value(index, modulus=29, low=z_low, high=z_high, offset=3),
        "gamma": _cycle_value(index, modulus=31, low=gamma_low, high=gamma_high, offset=7),
        "temperature_kelvin": _cycle_value(index, modulus=23, low=temp_low, high=temp_high, offset=11),
        "nk": 41,
    }


def _production_v1_direction(direction_regime: str, index: int) -> dict[str, Any]:
    if direction_regime == "inplane_100_no_spread":
        return {"direction_mode": "inplane_100"}
    if direction_regime == "inplane_110_no_spread":
        return {"direction_mode": "inplane_110"}
    mode = "inplane_100" if index % 2 == 0 else "inplane_110"
    half_width = 0.02454369260617026 if index % 4 in (0, 1) else 0.03681553890925539
    num_samples = 7 if half_width < 0.03 else 9
    return {
        "direction_mode": mode,
        "directional_spread": {
            "direction_mode": mode,
            "half_width": half_width,
            "num_samples": num_samples,
        },
    }


def _expand_sample_grids(sample_grids: Any) -> list[dict[str, Any]]:
    if sample_grids in (None, []):
        return []
    if not isinstance(sample_grids, list):
        raise ValueError("sample_grids must be a list when provided.")

    expanded: list[dict[str, Any]] = []
    for grid in sample_grids:
        if not isinstance(grid, dict):
            raise ValueError("sample_grids entries must be JSON objects.")
        required = ("row_prefix", "split", "pairing_controls_options", "transport_controls_options", "direction_options")
        missing = [key for key in required if key not in grid]
        if missing:
            raise ValueError(f"sample_grids entry is missing required key(s): {', '.join(missing)}.")

        pairing_options = grid["pairing_controls_options"]
        transport_options = grid["transport_controls_options"]
        direction_options = grid["direction_options"]
        if not isinstance(pairing_options, list) or not pairing_options:
            raise ValueError("pairing_controls_options must be a non-empty list.")
        if not isinstance(transport_options, list) or not transport_options:
            raise ValueError("transport_controls_options must be a non-empty list.")
        if not isinstance(direction_options, list) or not direction_options:
            raise ValueError("direction_options must be a non-empty list.")

        row_prefix = str(grid["row_prefix"])
        split = str(grid["split"])
        group_labels = {str(key): str(value) for key, value in dict(grid.get("group_labels", {})).items()}
        bias_grid = dict(grid.get("bias_grid", {})) or {
            "bias_min_mev": -20.0,
            "bias_max_mev": 20.0,
            "num_bias": 41,
        }

        for direction_index, direction in enumerate(direction_options):
            if direction is not None and not isinstance(direction, dict):
                raise ValueError("direction_options entries must be JSON objects or null.")
            for pairing_index, pairing_controls in enumerate(pairing_options):
                if not isinstance(pairing_controls, dict):
                    raise ValueError("pairing_controls_options entries must be JSON objects.")
                for transport_index, transport_controls in enumerate(transport_options):
                    if not isinstance(transport_controls, dict):
                        raise ValueError("transport_controls_options entries must be JSON objects.")
                    direction_label = _sample_grid_direction_label(direction, direction_index)
                    expanded.append(
                        {
                            "row_id": (
                                f"{row_prefix}_{direction_label}_p{pairing_index:02d}_t{transport_index:02d}"
                            ),
                            "split": split,
                            "pairing_controls": pairing_controls,
                            "transport_controls": transport_controls,
                            "direction": direction,
                            "group_labels": group_labels,
                            "bias_grid": bias_grid,
                        }
                    )
    return expanded


def _sample_grid_direction_label(direction: dict[str, Any] | None, direction_index: int) -> str:
    if direction is None:
        return f"legacy_d{direction_index:02d}"
    mode = direction.get("direction_mode")
    if mode is None:
        return f"raw_angle_d{direction_index:02d}"
    if direction.get("directional_spread"):
        return f"{mode}_spread_d{direction_index:02d}"
    return f"{mode}_d{direction_index:02d}"


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


def _payload_from_sample(sample: SmokeSampleSpec) -> dict[str, Any]:
    forward = import_forward_module("forward")
    result = _generate_result_from_sample(forward, sample)
    return result.to_dict()


def build_dataset_from_config(
    config_path: Path | str,
    *,
    output_dir: Path | str | None = None,
    run_metadata_path: Path | str | None = None,
    num_workers: int | None = None,
    force: bool = False,
) -> tuple[Path, Path]:
    """Generate a dataset from a config, resuming completed rows when possible."""

    import_forward_module("forward")
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
    resolved_num_workers = int(num_workers if num_workers is not None else config.get("num_workers", 1))
    if resolved_num_workers < 1:
        raise ValueError("num_workers must be at least 1.")

    output_path.mkdir(parents=True, exist_ok=True)
    spectra_dir.mkdir(parents=True, exist_ok=True)

    samples = materialize_dataset_samples(config)
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

    pending_samples: list[tuple[int, SmokeSampleSpec]] = []
    for index, sample in enumerate(samples):
        reusable_row = reusable_rows.get(sample.row_id)
        if reusable_row is not None and sample.pairing_representation is not None:
            reusable_controls = reusable_row.get("controls")
            if not isinstance(reusable_controls, dict) or reusable_controls.get("pairing_representation") != sample.pairing_representation:
                reusable_row = None
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

        pending_samples.append((index, sample))

    def record_completed_payload(index: int, sample: SmokeSampleSpec, payload: dict[str, Any]) -> None:
        nonlocal generated_count
        spectrum_path = spectra_dir / f"{sample.row_id}.json"
        spectrum_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        controls_payload: dict[str, object] = {
            "fit_layer_pairing_controls": dict(sample.pairing_controls),
            "pairing_control_mode": str(sample.pairing_control_mode),
            "allow_weak_delta_zx_s": bool(sample.allow_weak_delta_zx_s),
            "transport_controls": dict(sample.transport_controls),
            "direction": dict(sample.direction) if sample.direction is not None else None,
            "bias_grid": dict(sample.bias_grid),
        }
        if sample.group_labels:
            controls_payload["group_labels"] = dict(sample.group_labels)
        if sample.source_provenance:
            controls_payload["source_provenance"] = dict(sample.source_provenance)
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
            controls=controls_payload,
            pairing_representation=sample.pairing_representation,
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
        if generated_count == 1 or generated_count % 100 == 0 or generated_count == len(pending_samples):
            print(
                f"generated {generated_count}/{len(pending_samples)} pending rows "
                f"({generated_count + reused_count}/{len(samples)} total)",
                flush=True,
            )

    if pending_samples:
        if resolved_num_workers == 1:
            forward = import_forward_module("forward")
            for index, sample in pending_samples:
                result = _generate_result_from_sample(forward, sample)
                record_completed_payload(index, sample, result.to_dict())
        else:
            mp_context = multiprocessing.get_context("spawn")
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=resolved_num_workers,
                mp_context=mp_context,
            ) as executor:
                future_to_sample = {
                    executor.submit(_payload_from_sample, sample): (index, sample) for index, sample in pending_samples
                }
                for future in concurrent.futures.as_completed(future_to_sample):
                    index, sample = future_to_sample[future]
                    record_completed_payload(index, sample, future.result())

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
        "num_workers": resolved_num_workers,
        "allow_diagnostic_raw_angles": allow_diagnostic_raw_angles,
        "forward_metadata_family": rows[0]["forward_metadata"],
    }
    run_metadata_output_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path, run_metadata_output_path
