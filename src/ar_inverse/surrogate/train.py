"""Training pipeline for direction-aware surrogate checkpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ar_inverse.direction import SUPPORTED_DIRECTION_MODES, direction_regime_from_block
from ar_inverse.datasets.schema import file_sha256, validate_dataset_manifest
from ar_inverse.metadata import assert_forward_metadata_complete
from ar_inverse.surrogate.metrics import regression_metrics
from ar_inverse.surrogate.models import (
    DEFAULT_FEATURE_SPEC,
    NEURAL_MLP_MODEL_TYPE,
    NEURAL_RESIDUAL_MLP_MODEL_TYPE,
    RIDGE_MODEL_TYPE,
    NeuralMLPSpectrumSurrogate,
    RidgeLinearSpectrumSurrogate,
    checkpoint_filename_for_model_type,
    normalize_model_type,
)

DEFAULT_DIRECTIONAL_SURROGATE_CONFIG_PATH = Path("configs/surrogate/task9_directional_surrogate_smoke.json")
DEFAULT_DIRECTIONAL_SURROGATE_CHECKPOINT_DIR = Path("outputs/checkpoints/task9_directional_surrogate_smoke")
DEFAULT_DIRECTIONAL_SURROGATE_RUN_METADATA_PATH = Path(
    "outputs/runs/task9_directional_surrogate_smoke_run_metadata.json"
)

# Deprecated compatibility aliases for historical Task 4 callers.
DEFAULT_TASK4_CONFIG_PATH = DEFAULT_DIRECTIONAL_SURROGATE_CONFIG_PATH
DEFAULT_TASK4_CHECKPOINT_DIR = DEFAULT_DIRECTIONAL_SURROGATE_CHECKPOINT_DIR
DEFAULT_TASK4_RUN_METADATA_PATH = DEFAULT_DIRECTIONAL_SURROGATE_RUN_METADATA_PATH


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
    model: RidgeLinearSpectrumSurrogate | NeuralMLPSpectrumSurrogate,
    features: np.ndarray,
    targets: np.ndarray,
    splits: np.ndarray,
    *,
    device: str | None = None,
) -> dict[str, dict[str, float | int]]:
    metrics: dict[str, dict[str, float | int]] = {}
    for split in ("train", "validation", "test"):
        mask = splits == split
        if not bool(np.any(mask)):
            continue
        prediction = model.predict(features[mask], device=device)
        split_metrics = regression_metrics(prediction, targets[mask])
        split_metrics["num_rows"] = int(np.sum(mask))
        metrics[split] = split_metrics
    return metrics


def _split_metrics_from_predictions(
    predictions: np.ndarray,
    targets: np.ndarray,
    splits: np.ndarray,
) -> dict[str, dict[str, float | int]]:
    metrics: dict[str, dict[str, float | int]] = {}
    for split in ("train", "validation", "test"):
        mask = splits == split
        if not bool(np.any(mask)):
            continue
        split_metrics = regression_metrics(predictions[mask], targets[mask])
        split_metrics["num_rows"] = int(np.sum(mask))
        metrics[split] = split_metrics
    return metrics


def _ensemble_seeds_from_config(config: dict[str, Any]) -> list[int]:
    ensemble = config.get("ensemble")
    if not isinstance(ensemble, dict) or not bool(ensemble.get("enabled", False)):
        return [int(config.get("random_seed", 0))]

    seeds = ensemble.get("seeds")
    if not isinstance(seeds, list) or len(seeds) < 2:
        raise ValueError("ensemble.seeds must be a list with at least two entries when ensemble is enabled.")
    normalized = [int(seed) for seed in seeds]
    if len(set(normalized)) != len(normalized):
        raise ValueError("ensemble.seeds must be unique.")
    return normalized


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
    title = str(config.get("model_card_title", "Task 9 Directional Surrogate Smoke Checkpoint"))
    purpose_lines = _model_card_lines(
        config.get("model_card_purpose_lines"),
        default_lines=(
            "Smoke-scale direction-aware checkpoint mapping fit-layer, direction, and transport controls to AR conductance spectra.",
            "This is the Task 9 smoke-loop artifact, not the Task 10 non-smoke pilot or a server-scale training run.",
        ),
    )
    limitation_lines = _model_card_lines(
        config.get("model_card_limitations_lines"),
        default_lines=(
            "This checkpoint is trained on the tiny Task 8 directional smoke dataset and is intended only",
            "to verify direction-aware feature intake, checkpointing, metrics, and dataset metadata plumbing.",
            "The non-smoke pilot and server-scale training expansions belong to later tasks.",
        ),
    )
    lines = [
        f"# {title}",
        "",
        "## Purpose",
        "",
        *purpose_lines,
        "",
        "## Model",
        "",
        *_model_card_model_lines(config, metrics, checkpoint_path),
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
            *limitation_lines,
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _model_card_lines(lines: Any, *, default_lines: tuple[str, ...]) -> list[str]:
    if lines is None:
        return list(default_lines)
    if not isinstance(lines, list) or not lines or not all(isinstance(line, str) and line for line in lines):
        raise ValueError("Model card line overrides must be a non-empty list of strings.")
    return list(lines)


def _model_card_model_lines(config: dict[str, Any], metrics: dict[str, Any], checkpoint_path: Path) -> list[str]:
    model_type = normalize_model_type(metrics["model_type"])
    lines = [
        f"- Type: `{model_type}`",
        f"- Checkpoint: `{checkpoint_path.as_posix()}`",
        f"- Feature order: `{', '.join(DEFAULT_FEATURE_SPEC.names)}`",
    ]
    if model_type == RIDGE_MODEL_TYPE:
        lines.insert(1, f"- Ridge alpha: `{config.get('ridge_alpha', 1.0e-6)}`")
        return lines

    training = dict(metrics.get("training", {}))
    if model_type == NEURAL_MLP_MODEL_TYPE:
        lines.extend(
            [
                f"- Hidden layer widths: `{training.get('hidden_layer_widths', [])}`",
                f"- Depth: `{training.get('depth', 0)}`",
            ]
        )
    elif model_type == NEURAL_RESIDUAL_MLP_MODEL_TYPE:
        lines.extend(
            [
                f"- Residual hidden width: `{training.get('residual_hidden_width', training.get('hidden_width', 0))}`",
                f"- Residual blocks: `{training.get('residual_num_blocks', training.get('num_blocks', 0))}`",
                f"- Normalization: `{training.get('normalization', config.get('normalization', 'none'))}`",
            ]
        )
    lines.extend(
        [
            f"- Activation: `{training.get('activation', config.get('activation', 'relu'))}`",
            f"- Optimizer: `{training.get('optimizer', config.get('optimizer', 'adam'))}`",
            f"- Learning rate: `{training.get('learning_rate', config.get('learning_rate', 1.0e-3))}`",
            f"- Weight decay: `{training.get('weight_decay', config.get('weight_decay', 0.0))}`",
            f"- Batch size: `{training.get('batch_size', config.get('batch_size', 32))}`",
            f"- Epoch limit: `{training.get('epoch_limit', config.get('max_epochs', 100))}`",
            f"- Best epoch: `{training.get('best_epoch', training.get('epochs_completed', 0))}`",
            f"- Early-stopping patience: `{training.get('early_stopping_patience', config.get('early_stopping_patience', 10))}`",
            f"- Random seed: `{training.get('random_seed', config.get('random_seed', 0))}`",
            f"- Requested device: `{training.get('requested_device', config.get('device', 'auto'))}`",
            f"- Resolved device: `{training.get('resolved_device', 'cpu')}`",
        ]
    )
    loss_contract = dict(training.get("loss_contract", {}))
    if loss_contract:
        lines.extend(
            [
                f"- Loss kind: `{loss_contract.get('kind', 'plain_mse')}`",
                f"- Reconstruction weight: `{loss_contract.get('reconstruction_weight', 1.0)}`",
                f"- Shape weight: `{loss_contract.get('shape_weight', 0.0)}`",
                f"- Bias weighting: `{loss_contract.get('bias_weighting', {})}`",
            ]
        )
    ensemble = dict(metrics.get("ensemble", {}))
    if ensemble:
        lines.extend(
            [
                f"- Ensemble enabled: `{ensemble.get('enabled', False)}`",
                f"- Ensemble seeds: `{ensemble.get('seeds', [])}`",
                f"- Ensemble aggregation: `{ensemble.get('aggregation', 'mean')}`",
                f"- Ensemble disagreement summary: `{ensemble.get('disagreement_summary', 'per_point_std')}`",
            ]
        )
    return lines


def train_surrogate_from_config(
    config_path: Path | str = DEFAULT_DIRECTIONAL_SURROGATE_CONFIG_PATH,
) -> tuple[Path, Path, Path]:
    """Train a direction-aware surrogate checkpoint and write metrics/model card."""

    config_file = Path(config_path)
    config = load_training_config(config_file)
    dataset = load_dataset_arrays(config["dataset_manifest"])

    features = dataset["features"]
    targets = dataset["targets"]
    splits = dataset["splits"]
    train_mask = splits == "train"
    if not bool(np.any(train_mask)):
        raise ValueError("Training dataset must contain at least one train row.")

    held_out_splits = list(config.get("held_out_splits", ["validation", "test"]))
    model_type = normalize_model_type(config.get("model_type"))
    prediction_device: str | None = None
    ensemble_seeds = _ensemble_seeds_from_config(config)

    if model_type == RIDGE_MODEL_TYPE:
        if len(ensemble_seeds) != 1:
            raise ValueError("Ridge surrogate training does not support ensemble.seeds.")
        ridge_alpha = float(config.get("ridge_alpha", 1.0e-6))
        model = RidgeLinearSpectrumSurrogate.fit(
            features[train_mask],
            targets[train_mask],
            ridge_alpha=ridge_alpha,
        )
        training_summary = {
            "ridge_alpha": ridge_alpha,
        }
        split_metrics = _split_metrics(model, features, targets, splits, device=prediction_device)
    else:
        validation_mask = splits == "validation"
        validation_features = features[validation_mask] if bool(np.any(validation_mask)) else None
        validation_targets = targets[validation_mask] if bool(np.any(validation_mask)) else None
        shared_fit_kwargs = {
            "validation_features": validation_features,
            "validation_targets": validation_targets,
            "model_type": model_type,
            "hidden_layer_widths": _hidden_layer_widths_from_config(config),
            "residual_hidden_width": int(config.get("residual_hidden_width", config.get("hidden_width", 256))),
            "residual_num_blocks": int(config.get("residual_num_blocks", config.get("depth", 4))),
            "activation_name": str(config.get("activation", "relu")),
            "normalization_name": str(config.get("normalization", "none")),
            "optimizer_name": str(config.get("optimizer", "adam")),
            "learning_rate": float(config.get("learning_rate", 1.0e-3)),
            "weight_decay": float(config.get("weight_decay", 0.0)),
            "batch_size": int(config.get("batch_size", 32)),
            "max_epochs": int(config.get("max_epochs", 100)),
            "early_stopping_patience": int(config.get("early_stopping_patience", 10)),
            "device": str(config.get("device", "auto")),
            "loss_config": dict(config.get("loss", {})) if config.get("loss") is not None else None,
            "bias_mev": list(dataset["bias_mev"]),
        }
        prediction_device = "cpu"
        ensemble_config = dict(config.get("ensemble", {}))
        if len(ensemble_seeds) == 1:
            model, training_summary = NeuralMLPSpectrumSurrogate.fit(
                features[train_mask],
                targets[train_mask],
                random_seed=int(ensemble_seeds[0]),
                **shared_fit_kwargs,
            )
            split_metrics = _split_metrics(model, features, targets, splits, device=prediction_device)
        else:
            member_dir = Path(config["checkpoint_dir"]) / "members"
            member_dir.mkdir(parents=True, exist_ok=True)
            member_models: list[NeuralMLPSpectrumSurrogate] = []
            member_records: list[dict[str, Any]] = []
            member_predictions: list[np.ndarray] = []
            member_checkpoints: list[str] = []
            for seed in ensemble_seeds:
                member_model, member_training_summary = NeuralMLPSpectrumSurrogate.fit(
                    features[train_mask],
                    targets[train_mask],
                    random_seed=int(seed),
                    **shared_fit_kwargs,
                )
                member_checkpoint_path = member_dir / f"model_seed_{seed}.pt"
                member_model.save(member_checkpoint_path)
                member_models.append(member_model)
                member_checkpoints.append(member_checkpoint_path.as_posix())
                member_prediction = member_model.predict(features, device=prediction_device)
                member_predictions.append(member_prediction)
                member_records.append(
                    {
                        "seed": int(seed),
                        "checkpoint": member_checkpoint_path.as_posix(),
                        "splits": _split_metrics_from_predictions(member_prediction, targets, splits),
                        "training": member_training_summary,
                    }
                )

            ensemble_prediction = np.mean(np.stack(member_predictions, axis=0), axis=0)
            split_metrics = _split_metrics_from_predictions(ensemble_prediction, targets, splits)
            checkpoint_path = Path(config["checkpoint_dir"]) / "ensemble_manifest.json"
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            ensemble_manifest = {
                "ensemble_schema_version": "ar_inverse_surrogate_ensemble_v1",
                "model_type": model_type,
                "dataset_manifest": str(dataset["manifest_path"]),
                "dataset_id": dataset["manifest"]["dataset_id"],
                "aggregation": str(ensemble_config.get("aggregation", "mean")),
                "disagreement_summary": str(ensemble_config.get("disagreement_summary", "per_point_std")),
                "seeds": list(int(seed) for seed in ensemble_seeds),
                "member_checkpoints": member_checkpoints,
                "loss_contract": member_records[0]["training"]["loss_contract"],
            }
            checkpoint_path.write_text(json.dumps(ensemble_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            model = member_models[0]
            training_summary = dict(member_records[0]["training"])
            training_summary.update(
                {
                    "ensemble_enabled": True,
                    "ensemble_member_count": len(ensemble_seeds),
                    "ensemble_seeds": list(int(seed) for seed in ensemble_seeds),
                    "ensemble_aggregation": str(ensemble_config.get("aggregation", "mean")),
                    "ensemble_disagreement_summary": str(
                        ensemble_config.get("disagreement_summary", "per_point_std")
                    ),
                }
            )

    checkpoint_dir = Path(config["checkpoint_dir"])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = locals().get("checkpoint_path", checkpoint_dir / checkpoint_filename_for_model_type(model_type))
    metrics_path = checkpoint_dir / "metrics.json"
    model_card_path = checkpoint_dir / "model_card.md"

    if model_type == RIDGE_MODEL_TYPE or len(ensemble_seeds) == 1:
        model.save(checkpoint_path)
    run_kind = str(config.get("run_kind", "task9_directional_surrogate_smoke_training"))
    metrics = {
        "run_kind": run_kind,
        "model_type": model_type,
        "dataset_manifest": str(dataset["manifest_path"]),
        "dataset_id": dataset["manifest"]["dataset_id"],
        "feature_spec": DEFAULT_FEATURE_SPEC.to_dict(),
        "bias_mev": dataset["bias_mev"],
        "direction_support": _direction_support_summary(dataset["manifest"]["rows"]),
        "splits": split_metrics,
        "held_out_splits": held_out_splits,
        "checkpoint": checkpoint_path.as_posix(),
    }
    if model_type == RIDGE_MODEL_TYPE:
        metrics["ridge_alpha"] = float(training_summary["ridge_alpha"])
    else:
        metrics["training"] = training_summary
        if len(ensemble_seeds) > 1:
            ensemble = dict(config.get("ensemble", {}))
            metrics["ensemble"] = {
                "enabled": True,
                "member_count": len(ensemble_seeds),
                "seeds": list(int(seed) for seed in ensemble_seeds),
                "aggregation": str(ensemble.get("aggregation", "mean")),
                "disagreement_summary": str(ensemble.get("disagreement_summary", "per_point_std")),
                "member_checkpoints": member_checkpoints,
            }
            metrics["members"] = member_records
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_model_card(
        model_card_path,
        config=config,
        dataset=dataset,
        metrics=metrics,
        checkpoint_path=checkpoint_path,
    )

    run_metadata_path = Path(config.get("run_metadata_path", DEFAULT_DIRECTIONAL_SURROGATE_RUN_METADATA_PATH))
    run_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    run_metadata = {
        "run_kind": run_kind,
        "config": config_file.as_posix(),
        "checkpoint": checkpoint_path.as_posix(),
        "metrics": metrics_path.as_posix(),
        "model_card": model_card_path.as_posix(),
        "dataset_manifest": str(dataset["manifest_path"]),
        "dataset_id": dataset["manifest"]["dataset_id"],
        "model_type": model_type,
        "forward_metadata_family": dataset["manifest"]["rows"][0]["forward_metadata"],
        "direction_support": _direction_support_summary(dataset["manifest"]["rows"]),
        "held_out_splits": held_out_splits,
    }
    if model_type == RIDGE_MODEL_TYPE:
        run_metadata["ridge_alpha"] = float(training_summary["ridge_alpha"])
    else:
        run_metadata.update(
            {
                "optimizer": training_summary["optimizer"],
                "learning_rate": training_summary["learning_rate"],
                "batch_size": training_summary["batch_size"],
                "epoch_limit": training_summary["epoch_limit"],
                "epochs_completed": training_summary["epochs_completed"],
                "best_epoch": training_summary["best_epoch"],
                "early_stopping_patience": training_summary["early_stopping_patience"],
                "random_seed": training_summary["random_seed"],
                "requested_device": training_summary["requested_device"],
                "resolved_device": training_summary["resolved_device"],
                "depth": training_summary["depth"],
                "activation": training_summary["activation"],
                "weight_decay": training_summary["weight_decay"],
                "loss_contract": training_summary["loss_contract"],
            }
        )
        if "hidden_layer_widths" in training_summary:
            run_metadata["hidden_layer_widths"] = training_summary["hidden_layer_widths"]
        if "residual_hidden_width" in training_summary:
            run_metadata["residual_hidden_width"] = training_summary["residual_hidden_width"]
            run_metadata["residual_num_blocks"] = training_summary["residual_num_blocks"]
            run_metadata["normalization"] = training_summary["normalization"]
        if len(ensemble_seeds) > 1:
            ensemble = dict(config.get("ensemble", {}))
            run_metadata["ensemble"] = {
                "enabled": True,
                "member_count": len(ensemble_seeds),
                "seeds": list(int(seed) for seed in ensemble_seeds),
                "aggregation": str(ensemble.get("aggregation", "mean")),
                "disagreement_summary": str(ensemble.get("disagreement_summary", "per_point_std")),
                "member_checkpoints": member_checkpoints,
                "checkpoint_manifest": checkpoint_path.as_posix(),
            }
    run_metadata_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return checkpoint_path, metrics_path, model_card_path


def _hidden_layer_widths_from_config(config: dict[str, Any]) -> tuple[int, ...]:
    widths = config.get("hidden_layer_widths")
    if widths is not None:
        if not isinstance(widths, list) or not widths:
            raise ValueError("hidden_layer_widths must be a non-empty list when provided.")
        return tuple(int(width) for width in widths)
    depth = int(config.get("depth", 2))
    hidden_width = int(config.get("hidden_width", 128))
    if depth < 1:
        raise ValueError("depth must be at least 1.")
    if hidden_width < 1:
        raise ValueError("hidden_width must be at least 1.")
    return tuple(hidden_width for _ in range(depth))


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
