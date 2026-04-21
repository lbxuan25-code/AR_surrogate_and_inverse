from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ar_inverse.experiments.ingest import load_experiment_spectrum, validate_experiment_spectrum
from ar_inverse.experiments.preprocessing import apply_preprocessing
from ar_inverse.experiments.report import DEFAULT_TASK7_CONFIG_PATH, build_experiment_fit_report
from ar_inverse.metadata import missing_forward_metadata_keys


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_no_unique_truth_claim(text: str) -> None:
    forbidden = (
        "the order parameter is uniquely",
        "uniquely this RMFT point",
        "uniquely determined",
    )
    lowered = text.lower()
    assert all(phrase.lower() not in lowered for phrase in forbidden)


def test_experiment_ingest_and_preprocessing_schema() -> None:
    experiment = load_experiment_spectrum(
        "outputs/experiments/task7_synthetic_fit/synthetic_experiment_spectrum.json"
    )
    validate_experiment_spectrum(experiment)
    processed, metadata = apply_preprocessing(experiment)

    assert len(processed["bias_mev"]) == len(processed["conductance"])
    assert metadata["separated_from_physical_inference"] is True
    assert metadata["operations"][0]["operation"] == "identity"


def test_build_experiment_fit_report_writes_separated_sections(tmp_path) -> None:
    config = _load_json(DEFAULT_TASK7_CONFIG_PATH)
    config["output_dir"] = str(tmp_path / "experiment_fit")
    config["run_metadata_path"] = str(tmp_path / "run_metadata.json")
    config_path = tmp_path / "task7_config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report_path, markdown_path = build_experiment_fit_report(config_path)

    assert report_path.exists()
    assert markdown_path.exists()
    assert Path(config["run_metadata_path"]).exists()

    report = _load_json(report_path)
    assert report["run_kind"] == "task7_experiment_fitting_report"
    assert "preprocessing" in report
    assert "transport_nuisance_controls" in report
    assert "order_parameter_feature_claims" in report
    assert "surrogate_uncertainty" in report
    assert "final_forward_recheck_results" in report
    assert report["order_parameter_feature_claims"]["statement"] == (
        "the AR data are compatible with these feature families"
    )
    assert report["order_parameter_feature_claims"]["not_unique_microscopic_truth"] is True

    for record in report["final_forward_recheck_results"]:
        assert missing_forward_metadata_keys(record["forward_recheck_metadata"]) == ()

    _assert_no_unique_truth_claim(markdown_path.read_text(encoding="utf-8"))


def test_repository_task7_report_contract() -> None:
    report_path = Path("outputs/experiments/task7_synthetic_fit/experiment_fit_report.json")
    markdown_path = Path("outputs/experiments/task7_synthetic_fit/experiment_fit_report.md")
    run_metadata_path = Path("outputs/runs/task7_experiment_fit_run_metadata.json")

    assert report_path.exists()
    assert markdown_path.exists()
    assert run_metadata_path.exists()

    report = _load_json(report_path)
    run_metadata = _load_json(run_metadata_path)

    assert report["experiment"]["experiment_id"] == "synthetic_task7_forward_perturbation_v1"
    assert run_metadata["claim_policy"] == "candidate_families_not_unique_microscopic_truth"
    assert report["final_forward_recheck_results"]
    assert report["transport_nuisance_controls"]["candidate_values"]
    assert report["order_parameter_feature_claims"]["candidate_values"]
    _assert_no_unique_truth_claim(json.dumps(report, sort_keys=True))
    _assert_no_unique_truth_claim(markdown_path.read_text(encoding="utf-8"))


def test_fit_experiment_cli_writes_report(tmp_path) -> None:
    config = _load_json(DEFAULT_TASK7_CONFIG_PATH)
    config["output_dir"] = str(tmp_path / "cli_experiment_fit")
    config["run_metadata_path"] = str(tmp_path / "cli_run_metadata.json")
    config_path = tmp_path / "task7_cli_config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/experiments/fit_experiment.py",
            "--config",
            str(config_path),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    assert str(Path(config["output_dir"]) / "experiment_fit_report.json") in result.stdout
    assert str(Path(config["output_dir"]) / "experiment_fit_report.md") in result.stdout


def test_experiment_schema_rejects_missing_fields() -> None:
    with pytest.raises(ValueError, match="missing required key"):
        validate_experiment_spectrum({"experiment_id": "missing_arrays"})
