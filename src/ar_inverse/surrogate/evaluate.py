"""Evaluation helpers for surrogate baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ar_inverse.metadata import assert_forward_metadata_complete
from ar_inverse.surrogate.calibration import (
    calibration_diagnostics,
    direction_regime_label,
    fallback_policy,
    transport_regime_label,
)
from ar_inverse.surrogate.metrics import regression_metrics
from ar_inverse.surrogate.models import RidgeLinearSpectrumSurrogate
from ar_inverse.surrogate.train import load_dataset_arrays

DEFAULT_TASK5_CONFIG_PATH = Path("configs/surrogate/task5_evaluate_linear_surrogate.json")
DEFAULT_TASK5_REPORT_DIR = Path("outputs/runs/task5_surrogate_evaluation")
DEFAULT_TASK5_RUN_METADATA_PATH = Path("outputs/runs/task5_surrogate_evaluation_run_metadata.json")


def load_evaluation_config(path: Path | str) -> dict[str, Any]:
    """Load a surrogate evaluation config from JSON."""

    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Surrogate evaluation config must be a JSON object.")
    required = ("checkpoint", "dataset_manifest", "report_dir")
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Surrogate evaluation config is missing required key(s): {', '.join(missing)}.")
    return config


def _safe_thresholds(config: dict[str, Any]) -> dict[str, float]:
    thresholds = dict(config.get("safe_error_thresholds", {}))
    return {
        "rmse": float(thresholds.get("rmse", 0.05)),
        "max_abs_error": float(thresholds.get("max_abs_error", 0.10)),
    }


def _row_error_record(
    *,
    row_id: str,
    split: str,
    prediction: np.ndarray,
    target: np.ndarray,
    row: dict[str, Any],
    controls: dict[str, Any],
    thresholds: dict[str, float],
) -> dict[str, Any]:
    metrics = regression_metrics(prediction.reshape(1, -1), target.reshape(1, -1))
    transport_controls = dict(controls.get("transport_controls", {}))
    regime = transport_regime_label(transport_controls)
    direction_regime = direction_regime_label(row)
    unsafe_reasons: list[str] = []
    if metrics["rmse"] > thresholds["rmse"]:
        unsafe_reasons.append(f"rmse>{thresholds['rmse']}")
    if metrics["max_abs_error"] > thresholds["max_abs_error"]:
        unsafe_reasons.append(f"max_abs_error>{thresholds['max_abs_error']}")
    return {
        "row_id": row_id,
        "split": split,
        "transport_regime": regime,
        "direction_regime": direction_regime,
        "direction": row.get("direction"),
        "transport_controls": transport_controls,
        "metrics": metrics,
        "safe_for_inverse_acceleration": not unsafe_reasons,
        "unsafe_reasons": unsafe_reasons,
    }


def _group_regime_records(row_records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return _group_records_by_key(row_records, "transport_regime")


def _group_direction_records(row_records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return _group_records_by_key(row_records, "direction_regime")


def _group_records_by_key(row_records: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in row_records:
        grouped.setdefault(str(record[key]), []).append(record)

    report: dict[str, dict[str, Any]] = {}
    for regime, records in grouped.items():
        rmse_values = [float(record["metrics"]["rmse"]) for record in records]
        max_values = [float(record["metrics"]["max_abs_error"]) for record in records]
        unsafe_records = [record["row_id"] for record in records if not record["safe_for_inverse_acceleration"]]
        report[regime] = {
            "num_rows": len(records),
            "row_ids": [record["row_id"] for record in records],
            "mean_rmse": float(np.mean(rmse_values)),
            "max_rmse": float(np.max(rmse_values)),
            "max_abs_error": float(np.max(max_values)),
            "unsafe_row_ids": unsafe_records,
            "safe_for_inverse_acceleration": not unsafe_records,
        }
    return report


def _write_markdown_report(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Task 5 Surrogate Evaluation And Calibration",
        "",
        "## Summary",
        "",
        f"- Model: `{report['model']['checkpoint']}`",
        f"- Dataset: `{report['dataset']['manifest']}`",
        f"- Held-out splits: `{', '.join(report['evaluation_scope']['held_out_splits'])}`",
        f"- Safe RMSE threshold: `{report['fallback_policy']['safe_error_thresholds']['rmse']}`",
        f"- Safe max-error threshold: `{report['fallback_policy']['safe_error_thresholds']['max_abs_error']}`",
        f"- Unsafe regimes: `{len(report['fallback_policy']['unsafe_transport_regimes'])}`",
        "",
        "## Calibration Diagnostics",
        "",
    ]
    diagnostics = report["calibration_diagnostics"]
    lines.extend(
        [
            f"- Held-out rows: `{diagnostics['num_rows']}`",
            f"- Mean RMSE: `{diagnostics['mean_rmse']:.8g}`",
            f"- Max RMSE: `{diagnostics['max_rmse']:.8g}`",
            f"- Mean max absolute error: `{diagnostics['mean_max_abs_error']:.8g}`",
            f"- Unsafe fraction: `{diagnostics['unsafe_fraction']:.8g}`",
            "",
            "## Transport Regimes",
            "",
        ]
    )
    for regime, regime_report in report["transport_regime_report"].items():
        lines.extend(
            [
                f"### {regime}",
                "",
                f"- Rows: `{regime_report['num_rows']}`",
                f"- Mean RMSE: `{regime_report['mean_rmse']:.8g}`",
                f"- Max RMSE: `{regime_report['max_rmse']:.8g}`",
                f"- Max absolute error: `{regime_report['max_abs_error']:.8g}`",
                f"- Safe for inverse acceleration: `{regime_report['safe_for_inverse_acceleration']}`",
                f"- Unsafe rows: `{', '.join(regime_report['unsafe_row_ids']) or 'none'}`",
                "",
            ]
        )
    lines.extend(["## Direction Regimes", ""])
    for regime, regime_report in report["direction_regime_report"].items():
        lines.extend(
            [
                f"### {regime}",
                "",
                f"- Rows: `{regime_report['num_rows']}`",
                f"- Mean RMSE: `{regime_report['mean_rmse']:.8g}`",
                f"- Max RMSE: `{regime_report['max_rmse']:.8g}`",
                f"- Max absolute error: `{regime_report['max_abs_error']:.8g}`",
                f"- Safe for inverse acceleration: `{regime_report['safe_for_inverse_acceleration']}`",
                f"- Unsafe rows: `{', '.join(regime_report['unsafe_row_ids']) or 'none'}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Fallback Policy",
            "",
            report["fallback_policy"]["summary"],
            "",
            "For unsafe regimes, inverse workflows must call the external forward",
            "interface directly for candidate scoring or final rechecks.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def evaluate_surrogate_from_config(config_path: Path | str = DEFAULT_TASK5_CONFIG_PATH) -> tuple[Path, Path]:
    """Evaluate the trained surrogate and write Task 5 reports."""

    config_file = Path(config_path)
    config = load_evaluation_config(config_file)
    thresholds = _safe_thresholds(config)

    dataset = load_dataset_arrays(config["dataset_manifest"])
    model = RidgeLinearSpectrumSurrogate.load(config["checkpoint"])
    predictions = model.predict(dataset["features"])
    targets = dataset["targets"]
    splits = dataset["splits"]
    row_ids = dataset["row_ids"]
    manifest = dataset["manifest"]
    row_by_id = {str(row["row_id"]): row for row in manifest["rows"]}

    held_out_splits = list(config.get("held_out_splits", ["validation", "test"]))
    held_out_mask = np.isin(splits, held_out_splits)
    if not bool(np.any(held_out_mask)):
        raise ValueError("Evaluation config did not select any held-out rows.")

    row_records: list[dict[str, Any]] = []
    for index, row_id in enumerate(row_ids):
        if not bool(held_out_mask[index]):
            continue
        row = row_by_id[row_id]
        assert_forward_metadata_complete(row["forward_metadata"])
        row_records.append(
            _row_error_record(
                row_id=row_id,
                split=str(splits[index]),
                prediction=predictions[index],
                target=targets[index],
                row=row,
                controls=dict(row.get("controls", {})),
                thresholds=thresholds,
            )
        )

    regime_report = _group_regime_records(row_records)
    direction_regime_report = _group_direction_records(row_records)
    diagnostics = calibration_diagnostics(row_records, thresholds)
    policy = fallback_policy(regime_report, thresholds, direction_regime_report)
    forward_metadata_family = manifest["rows"][0]["forward_metadata"]

    report = {
        "run_kind": "task5_surrogate_evaluation_and_calibration",
        "model": {
            "checkpoint": str(config["checkpoint"]),
            "model_type": "ridge_linear_spectrum_surrogate",
        },
        "dataset": {
            "dataset_id": manifest["dataset_id"],
            "manifest": str(dataset["manifest_path"]),
            "sampling_policy_id": manifest["sampling_policy_id"],
        },
        "evaluation_scope": {
            "held_out_splits": held_out_splits,
            "num_held_out_rows": len(row_records),
        },
        "row_errors": row_records,
        "transport_regime_report": regime_report,
        "direction_regime_report": direction_regime_report,
        "calibration_diagnostics": diagnostics,
        "fallback_policy": policy,
        "forward_metadata_family": forward_metadata_family,
    }

    report_dir = Path(config["report_dir"])
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "evaluation_report.json"
    markdown_path = report_dir / "evaluation_report.md"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown_report(markdown_path, report)

    run_metadata_path = Path(config.get("run_metadata_path", DEFAULT_TASK5_RUN_METADATA_PATH))
    run_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    run_metadata = {
        "run_kind": "task5_surrogate_evaluation_and_calibration",
        "config": config_file.as_posix(),
        "report": report_path.as_posix(),
        "markdown_report": markdown_path.as_posix(),
        "checkpoint": str(config["checkpoint"]),
        "dataset_manifest": str(dataset["manifest_path"]),
        "unsafe_transport_regimes": policy["unsafe_transport_regimes"],
        "unsafe_direction_regimes": policy["unsafe_direction_regimes"],
        "forward_metadata_family": forward_metadata_family,
    }
    run_metadata_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path, markdown_path
