"""Experiment-fitting report workflow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ar_inverse.direction import normalize_direction_prior
from ar_inverse.experiments.ingest import load_experiment_spectrum
from ar_inverse.experiments.preprocessing import apply_preprocessing, default_preprocessing_config
from ar_inverse.inverse.objectives import spectrum_objective

DEFAULT_TASK7_CONFIG_PATH = Path("configs/experiments/task7_synthetic_experiment.json")
DEFAULT_TASK7_OUTPUT_DIR = Path("outputs/experiments/task7_synthetic_fit")
DEFAULT_TASK7_RUN_METADATA_PATH = Path("outputs/runs/task7_experiment_fit_run_metadata.json")


def load_experiment_fit_config(path: Path | str) -> dict[str, Any]:
    """Load an experiment-fit report config."""

    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Experiment fit config must be a JSON object.")
    required = ("experiment_spectrum", "inverse_report", "output_dir")
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Experiment fit config is missing required key(s): {', '.join(missing)}.")
    return config


def _load_json(path: Path | str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _candidate_recheck_payload(inverse_report_path: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    output_ref = candidate["forward_recheck"]["output_ref"]
    payload_path = inverse_report_path.parent / output_ref["path"]
    if not payload_path.exists():
        raise ValueError(f"Candidate forward recheck payload does not exist: {payload_path}.")
    return _load_json(payload_path)


def _fit_candidate_records(
    *,
    inverse_report_path: Path,
    inverse_report: dict[str, Any],
    processed_experiment: dict[str, list[float]],
) -> list[dict[str, Any]]:
    experiment_bias = np.asarray(processed_experiment["bias_mev"], dtype=np.float64)
    experiment_conductance = list(processed_experiment["conductance"])
    records: list[dict[str, Any]] = []

    for candidate in inverse_report["candidate_families"]:
        payload = _candidate_recheck_payload(inverse_report_path, candidate)
        candidate_bias = np.asarray(payload["bias_mev"], dtype=np.float64)
        if candidate_bias.shape != experiment_bias.shape or not np.allclose(candidate_bias, experiment_bias):
            raise ValueError("Experiment and candidate forward recheck bias grids do not match.")
        metrics = spectrum_objective(payload["conductance"], experiment_conductance)
        records.append(
            {
                "candidate_family_id": candidate["candidate_family_id"],
                "compatibility_statement": "the AR data are compatible with these feature families",
                "experiment_fit_objective": metrics,
                "pairing_controls": candidate["pairing_controls"],
                "transport_nuisance_controls": candidate["transport_nuisance_controls"],
                "direction": candidate.get("direction"),
                "direction_prior": candidate.get("direction_prior"),
                "uncertainty_ranges": candidate["uncertainty_ranges"],
                "forward_recheck_metadata": candidate["forward_recheck"]["metadata"],
            }
        )

    records.sort(key=lambda record: float(record["experiment_fit_objective"]["score"]))
    return records


def build_experiment_fit_report(config_path: Path | str = DEFAULT_TASK7_CONFIG_PATH) -> tuple[Path, Path]:
    """Build the Task 7 experiment-fitting smoke report."""

    config_file = Path(config_path)
    config = load_experiment_fit_config(config_file)
    experiment = load_experiment_spectrum(config["experiment_spectrum"])
    direction_prior = normalize_direction_prior(
        config.get("direction_prior") or experiment.get("metadata", {}).get("direction_prior")
    )
    preprocessing_config = dict(config.get("preprocessing", default_preprocessing_config()))
    processed_experiment, preprocessing_metadata = apply_preprocessing(experiment, preprocessing_config)

    inverse_report_path = Path(config["inverse_report"])
    inverse_report = _load_json(inverse_report_path)
    candidate_records = _fit_candidate_records(
        inverse_report_path=inverse_report_path,
        inverse_report=inverse_report,
        processed_experiment=processed_experiment,
    )

    report = {
        "run_kind": "task7_experiment_fitting_report",
        "report_schema_version": "ar_inverse_experiment_fit_report_v1",
        "experiment": {
            "experiment_id": experiment["experiment_id"],
            "source": str(config["experiment_spectrum"]),
            "metadata": experiment["metadata"],
            "direction_prior": direction_prior,
        },
        "preprocessing": preprocessing_metadata,
        "experimental_preprocessing": {
            "bias_mev": processed_experiment["bias_mev"],
            "num_points": len(processed_experiment["bias_mev"]),
        },
        "transport_nuisance_controls": {
            "description": "Transport controls are nuisance parameters and are reported separately from pairing controls.",
            "candidate_values": {
                record["candidate_family_id"]: record["transport_nuisance_controls"] for record in candidate_records
            },
        },
        "directional_priors_and_regimes": {
            "description": "Direction priors and candidate direction regimes are reported separately from pairing controls and transport nuisance controls.",
            "experiment_direction_prior": direction_prior,
            "candidate_values": {
                record["candidate_family_id"]: {
                    "direction": record.get("direction"),
                    "direction_prior": record.get("direction_prior"),
                }
                for record in candidate_records
            },
        },
        "order_parameter_feature_claims": {
            "statement": "the AR data are compatible with these feature families",
            "not_unique_microscopic_truth": True,
            "candidate_values": {
                record["candidate_family_id"]: record["pairing_controls"] for record in candidate_records
            },
        },
        "surrogate_uncertainty": {
            "source": str(config.get("surrogate_evaluation_report", "")),
            "usage": "No surrogate-only claim is made; candidate scores use direct-forward recheck payloads.",
        },
        "final_forward_recheck_results": candidate_records,
    }
    _validate_no_unique_truth_claim(report)

    output_dir = Path(config.get("output_dir", DEFAULT_TASK7_OUTPUT_DIR))
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "experiment_fit_report.json"
    markdown_path = output_dir / "experiment_fit_report.md"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown_report(markdown_path, report)

    run_metadata_path = Path(config.get("run_metadata_path", DEFAULT_TASK7_RUN_METADATA_PATH))
    run_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    run_metadata = {
        "run_kind": "task7_experiment_fitting_report",
        "config": config_file.as_posix(),
        "report": report_path.as_posix(),
        "markdown_report": markdown_path.as_posix(),
        "experiment_id": experiment["experiment_id"],
        "candidate_family_count": len(candidate_records),
        "best_candidate_family_id": candidate_records[0]["candidate_family_id"],
        "claim_policy": "candidate_families_not_unique_microscopic_truth",
        "direction_prior": direction_prior,
    }
    run_metadata_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path, markdown_path


def _write_markdown_report(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Task 7 Synthetic Experiment Fit Report",
        "",
        "The AR data are compatible with these feature families. This report does not",
        "claim a unique microscopic RMFT point.",
        "",
        "## Experiment",
        "",
        f"- Experiment id: `{report['experiment']['experiment_id']}`",
        f"- Source: `{report['experiment']['source']}`",
        "",
        "## Experimental Preprocessing",
        "",
    ]
    for operation in report["preprocessing"]["operations"]:
        lines.append(f"- `{operation['operation']}`: {operation.get('description', 'recorded operation')}")
    lines.extend(
        [
            "",
            "## Transport Nuisance Controls",
            "",
            report["transport_nuisance_controls"]["description"],
            "",
            "## Direction Priors And Regimes",
            "",
            report["directional_priors_and_regimes"]["description"],
            "",
            f"- Experiment direction prior: `{report['directional_priors_and_regimes']['experiment_direction_prior']['kind']}`",
            "",
            "## Candidate Feature Families",
            "",
        ]
    )
    for record in report["final_forward_recheck_results"]:
        lines.extend(
            [
                f"### {record['candidate_family_id']}",
                "",
                f"- Fit score: `{record['experiment_fit_objective']['score']:.8g}`",
                f"- Pairing controls: `{record['pairing_controls']['center']}`",
                f"- Transport nuisance controls: `{record['transport_nuisance_controls']['center']}`",
                f"- Direction regime: `{(record.get('direction') or {}).get('direction_regime', 'unspecified')}`",
                f"- Forward metadata commit: `{record['forward_recheck_metadata']['git_commit']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Surrogate Uncertainty",
            "",
            report["surrogate_uncertainty"]["usage"],
            "",
            "## Final Forward Recheck Results",
            "",
            "Candidate scores above are based on direct-forward recheck spectra from the",
            "external forward interface.",
            "",
        ]
    )
    text = "\n".join(lines)
    _validate_report_text(text)
    path.write_text(text, encoding="utf-8")


def _validate_report_text(text: str) -> None:
    forbidden = (
        "uniquely this RMFT point",
        "uniquely determined",
        "unique microscopic truth",
        "the order parameter is uniquely",
    )
    lowered = text.lower()
    for phrase in forbidden:
        if phrase.lower() in lowered:
            raise ValueError(f"Experiment report contains forbidden uniqueness claim: {phrase!r}.")


def _validate_no_unique_truth_claim(report: dict[str, Any]) -> None:
    text = json.dumps(report, sort_keys=True)
    _validate_report_text(text)
