"""Training pipeline for the first surrogate baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ar_inverse.direction import SUPPORTED_DIRECTION_MODES, direction_regime_from_block
from ar_inverse.datasets.schema import file_sha256, validate_dataset_manifest
from ar_inverse.metadata import assert_forward_metadata_complete
from ar_inverse.surrogate.metrics import regression_metrics
from ar_inverse.surrogate.models import DEFAULT_FEATURE_SPEC, RidgeLinearSpectrumSurrogate

DEFAULT_TASK4_CONFIG_PATH = Path("configs/surrogate/task4_linear_surrogate.json")
DEFAULT_TASK4_CHECKPOINT_DIR = Path("outputs/checkpoints/task4_linear_surrogate")
DEFAULT_TASK4_RUN_METADATA_PATH = Path("outputs/runs/task4_linear_surrogate_run_metadata.json")


def load_training_config(path: Path | str) -> dict[str, Any]:
    """Load a surrogate training config from JSON."""

    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Surrogate training config must be a JSON object.")
    required = ("dataset_manifest", "checkpoint_dir")
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Surrogate training config is missing required key(s): {', '.join(missing)}.")
    return config


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _row_output_payload(dataset_dir: Path, row: dict[str, Any]) -> dict[str, Any]:
    output_ref = row["forward_output_ref"]
    output_path = dataset_dir / str(output_ref["path"])
    if not output_path.exists():
        raise ValueError(f"Forward output artifact does not exist: {output_path}.")
    if str(output_ref["sha256"]) != file_sha256(output_path):
        raise ValueError(f"Forward output artifact hash mismatch: {output_path}.")
    payload = _load_json(output_path)
    if payload["request"] != row["forward_request"]:
        raise ValueError(f"Forward output request does not match row request for {row['row_id']}.")
    if payload["metadata"] != row["forward_metadata"]:
        raise ValueError(f"Forward output metadata does not match row metadata for {row['row_id']}.")
    return payload


def _feature_from_row(row: dict[str, Any]) -> np.ndarray:
    controls = row.get("controls")
    if not isinstance(controls, dict):
        raise ValueError(f"Dataset row {row['row_id']} is missing controls.")

    pairing_controls = dict(controls.get("fit_layer_pairing_controls", {}))
    transport_controls = dict(controls.get("transport_controls", {}))
    direction_features = _direction_feature_values(row, transport_controls)
    values: list[float] = []
    for name in DEFAULT_FEATURE_SPEC.names:
        if name in pairing_controls:
            values.append(float(pairing_controls[name]))
        elif name in direction_features:
            values.append(float(direction_features[name]))
        elif name in transport_controls:
            values.append(float(transport_controls[name]))
        else:
            values.append(0.0)
    return np.asarray(values, dtype=np.float64)


def _direction_feature_values(row: dict[str, Any], transport_controls: dict[str, Any]) -> dict[str, float]:
    direction = row.get("direction")
    if isinstance(direction, dict):
        spread = direction.get("directional_spread")
        spread_payload = spread if isinstance(spread, dict) else {}
        mode = direction.get("direction_mode")
        interface_angle = direction.get("interface_angle")
        regime = direction_regime_from_block(direction)
        return {
            "direction_inplane_100": 1.0 if mode == "inplane_100" else 0.0,
            "direction_inplane_110": 1.0 if mode == "inplane_110" else 0.0,
            "direction_named_mode": 1.0 if mode in SUPPORTED_DIRECTION_MODES else 0.0,
            "direction_diagnostic_raw_angle": 1.0 if regime == "diagnostic_raw_angle" else 0.0,
            "direction_has_spread": 1.0 if spread_payload else 0.0,
            "direction_spread_half_width": float(spread_payload.get("half_width", 0.0)),
            "direction_spread_num_samples": float(spread_payload.get("num_samples", 0.0)),
            "direction_raw_interface_angle": 0.0 if interface_angle is None else float(interface_angle),
        }

    # Legacy angle-only rows remain loadable but are explicitly diagnostic.
    interface_angle = transport_controls.get("interface_angle", 0.0)
    return {
        "direction_inplane_100": 0.0,
        "direction_inplane_110": 0.0,
        "direction_named_mode": 0.0,
        "direction_diagnostic_raw_angle": 1.0,
        "direction_has_spread": 0.0,
        "direction_spread_half_width": 0.0,
        "direction_spread_num_samples": 0.0,
        "direction_raw_interface_angle": float(interface_angle),
    }


def load_dataset_arrays(manifest_path: Path | str) -> dict[str, Any]:
    """Load feature/target arrays split by dataset row labels."""

    manifest_file = Path(manifest_path)
    dataset_dir = manifest_file.parent
    manifest = _load_json(manifest_file)
    validate_dataset_manifest(manifest)

    rows = list(manifest["rows"])
    features: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    splits: list[str] = []
    row_ids: list[str] = []
    forward_metadata_by_row: dict[str, dict[str, object]] = {}
    bias_mev: list[float] | None = None

    for row in rows:
        metadata = row["forward_metadata"]
        assert_forward_metadata_complete(metadata)
        payload = _row_output_payload(dataset_dir, row)
        if bias_mev is None:
            bias_mev = list(payload["bias_mev"])
        elif list(payload["bias_mev"]) != bias_mev:
            raise ValueError("All rows in the baseline training dataset must share the same bias grid.")

        features.append(_feature_from_row(row))
        targets.append(np.asarray(payload["conductance"], dtype=np.float64))
        splits.append(str(row["split"]))
        row_ids.append(str(row["row_id"]))
        forward_metadata_by_row[str(row["row_id"])] = metadata

    return {
        "manifest": manifest,
        "manifest_path": manifest_file,
        "features": np.vstack(features),
        "targets": np.vstack(targets),
        "splits": np.asarray(splits, dtype=str),
        "row_ids": row_ids,
        "bias_mev": bias_mev or [],
        "forward_metadata_by_row": forward_metadata_by_row,
    }


def _split_metrics(
    model: RidgeLinearSpectrumSurrogate,
    features: np.ndarray,
    targets: np.ndarray,
    splits: np.ndarray,
) -> dict[str, dict[str, float | int]]:
    metrics: dict[str, dict[str, float | int]] = {}
    for split in ("train", "validation", "test"):
        mask = splits == split
        if not bool(np.any(mask)):
            continue
        prediction = model.predict(features[mask])
        split_metrics = regression_metrics(prediction, targets[mask])
        split_metrics["num_rows"] = int(np.sum(mask))
        metrics[split] = split_metrics
    return metrics


def _write_model_card(
    path: Path,
    *,
    config: dict[str, Any],
    dataset: dict[str, Any],
    metrics: dict[str, Any],
    checkpoint_path: Path,
) -> None:
    manifest = dataset["manifest"]
    first_row = manifest["rows"][0]
    forward_metadata = first_row["forward_metadata"]
    direction_support = _direction_support_summary(manifest["rows"])
    lines = [
        "# Task 4 Linear Surrogate Baseline",
        "",
        "## Purpose",
        "",
        "First lightweight baseline mapping fit-layer and transport controls to AR conductance spectra.",
        "This is a smoke-scale model, not a calibrated inverse-search surrogate.",
        "",
        "## Model",
        "",
        "- Type: ridge-linear spectrum surrogate",
        f"- Ridge alpha: `{config.get('ridge_alpha', 1.0e-6)}`",
        f"- Checkpoint: `{checkpoint_path.as_posix()}`",
        f"- Feature order: `{', '.join(DEFAULT_FEATURE_SPEC.names)}`",
        "",
        "## Dataset",
        "",
        f"- Dataset id: `{manifest['dataset_id']}`",
        f"- Manifest: `{dataset['manifest_path'].as_posix()}`",
        f"- Sampling policy id: `{manifest['sampling_policy_id']}`",
        f"- Rows: `{len(manifest['rows'])}`",
        f"- Splits: `{', '.join(sorted({str(row['split']) for row in manifest['rows']}))}`",
        f"- Direction regimes: `{direction_support['direction_regime_counts']}`",
        "",
        "## Direction Support",
        "",
        "- Supported named modes: `inplane_100`, `inplane_110`.",
        "- `c_axis` is unsupported and is not a valid inverse target.",
        "- Generic raw angles are diagnostic-only and are not primary truth-grade training data.",
        "- Directional spread is represented only as narrow named-mode-centered spread.",
        f"- Dataset direction support summary: `{direction_support}`",
        "",
        "## Forward Metadata Family",
        "",
        f"- forward_interface_version: `{forward_metadata['forward_interface_version']}`",
        f"- output_schema_version: `{forward_metadata['output_schema_version']}`",
        f"- pairing_convention_id: `{forward_metadata['pairing_convention_id']}`",
        f"- formal_baseline_record: `{forward_metadata['formal_baseline_record']}`",
        f"- formal_baseline_selection_rule: `{forward_metadata['formal_baseline_selection_rule']}`",
        f"- git_commit: `{forward_metadata['git_commit']}`",
        f"- git_dirty: `{forward_metadata['git_dirty']}`",
        "",
        "## Metrics",
        "",
    ]
    for split, split_metrics in metrics["splits"].items():
        lines.extend(
            [
                f"### {split}",
                "",
                f"- Rows: `{split_metrics['num_rows']}`",
                f"- MAE: `{split_metrics['mae']:.8g}`",
                f"- RMSE: `{split_metrics['rmse']:.8g}`",
                f"- Max absolute error: `{split_metrics['max_abs_error']:.8g}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Limitations",
            "",
            "This baseline is trained on the tiny Task 3 smoke dataset and is intended only",
            "to verify training, checkpointing, metrics, and dataset metadata plumbing.",
            "Calibration and unsafe-regime analysis belong to Task 5.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def train_surrogate_from_config(
    config_path: Path | str = DEFAULT_TASK4_CONFIG_PATH,
) -> tuple[Path, Path, Path]:
    """Train the Task 4 baseline and write checkpoint, metrics, and model card."""

    config_file = Path(config_path)
    config = load_training_config(config_file)
    dataset = load_dataset_arrays(config["dataset_manifest"])

    features = dataset["features"]
    targets = dataset["targets"]
    splits = dataset["splits"]
    train_mask = splits == "train"
    if not bool(np.any(train_mask)):
        raise ValueError("Training dataset must contain at least one train row.")

    ridge_alpha = float(config.get("ridge_alpha", 1.0e-6))
    model = RidgeLinearSpectrumSurrogate.fit(
        features[train_mask],
        targets[train_mask],
        ridge_alpha=ridge_alpha,
    )

    checkpoint_dir = Path(config["checkpoint_dir"])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / "model.npz"
    metrics_path = checkpoint_dir / "metrics.json"
    model_card_path = checkpoint_dir / "model_card.md"

    model.save(checkpoint_path)
    metrics = {
        "run_kind": "task4_linear_surrogate_training",
        "model_type": "ridge_linear_spectrum_surrogate",
        "ridge_alpha": ridge_alpha,
        "dataset_manifest": str(dataset["manifest_path"]),
        "dataset_id": dataset["manifest"]["dataset_id"],
        "feature_spec": DEFAULT_FEATURE_SPEC.to_dict(),
        "bias_mev": dataset["bias_mev"],
        "direction_support": _direction_support_summary(dataset["manifest"]["rows"]),
        "splits": _split_metrics(model, features, targets, splits),
        "held_out_splits": ["validation", "test"],
        "checkpoint": checkpoint_path.as_posix(),
    }
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_model_card(
        model_card_path,
        config=config,
        dataset=dataset,
        metrics=metrics,
        checkpoint_path=checkpoint_path,
    )

    run_metadata_path = Path(config.get("run_metadata_path", DEFAULT_TASK4_RUN_METADATA_PATH))
    run_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    run_metadata = {
        "run_kind": "task4_linear_surrogate_training",
        "config": config_file.as_posix(),
        "checkpoint": checkpoint_path.as_posix(),
        "metrics": metrics_path.as_posix(),
        "model_card": model_card_path.as_posix(),
        "dataset_manifest": str(dataset["manifest_path"]),
        "dataset_id": dataset["manifest"]["dataset_id"],
        "forward_metadata_family": dataset["manifest"]["rows"][0]["forward_metadata"],
        "direction_support": _direction_support_summary(dataset["manifest"]["rows"]),
        "held_out_splits": ["validation", "test"],
    }
    run_metadata_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return checkpoint_path, metrics_path, model_card_path


def _direction_support_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    modes: set[str] = set()
    for row in rows:
        direction = row.get("direction")
        regime = direction_regime_from_block(direction if isinstance(direction, dict) else None)
        counts[regime] = counts.get(regime, 0) + 1
        if isinstance(direction, dict) and direction.get("direction_mode") is not None:
            modes.add(str(direction["direction_mode"]))
    return {
        "direction_regime_counts": counts,
        "direction_modes": sorted(modes),
        "legacy_angle_only_rows": counts.get("legacy_or_unknown_direction", 0),
        "diagnostic_raw_angle_rows": counts.get("diagnostic_raw_angle", 0),
    }
