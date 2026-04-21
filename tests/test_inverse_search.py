from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ar_inverse.inverse.candidates import validate_candidate_family, validate_inverse_report
from ar_inverse.inverse.search import DEFAULT_TASK6_CONFIG_PATH, run_inverse_search_from_config
from ar_inverse.metadata import missing_forward_metadata_keys


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_run_inverse_search_from_config_writes_candidate_family_report(tmp_path) -> None:
    config = _load_json(DEFAULT_TASK6_CONFIG_PATH)
    config["output_dir"] = str(tmp_path / "inverse")
    config["run_metadata_path"] = str(tmp_path / "run_metadata.json")
    config_path = tmp_path / "task6_config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report_path, markdown_path = run_inverse_search_from_config(config_path)

    assert report_path.exists()
    assert markdown_path.exists()
    assert Path(config["run_metadata_path"]).exists()

    report = _load_json(report_path)
    validate_inverse_report(report)
    assert report["interpretation"] == "the AR data are compatible with these feature families"
    assert report["search"]["surrogate_usage"]["used"] is False
    assert len(report["candidate_families"]) == 2

    for candidate in report["candidate_families"]:
        validate_candidate_family(candidate)
        assert candidate["pairing_controls"]["center"]
        assert candidate["pairing_controls"]["ranges"]
        assert candidate["transport_nuisance_controls"]["center"]
        assert candidate["transport_nuisance_controls"]["ranges"]
        assert candidate["uncertainty_ranges"]
        assert candidate["objective"]["score_kind"] == "spectrum_rmse"
        assert missing_forward_metadata_keys(candidate["forward_recheck"]["metadata"]) == ()


def test_repository_task6_report_has_forward_recheck_metadata() -> None:
    report_path = Path("outputs/inverse/task6_smoke_inverse/inverse_report.json")
    run_metadata_path = Path("outputs/runs/task6_smoke_inverse_run_metadata.json")
    assert report_path.exists()
    assert run_metadata_path.exists()

    report = _load_json(report_path)
    run_metadata = _load_json(run_metadata_path)
    validate_inverse_report(report)

    assert report["target"]["row_id"] == "task3_smoke_train_000"
    assert run_metadata["reported_candidate_count"] == len(report["candidate_families"])
    assert "uniquely" not in Path("outputs/inverse/task6_smoke_inverse/inverse_report.md").read_text(encoding="utf-8")

    for candidate in report["candidate_families"]:
        recheck_ref = candidate["forward_recheck"]["output_ref"]
        recheck_path = report_path.parent / recheck_ref["path"]
        assert recheck_path.exists()
        assert missing_forward_metadata_keys(candidate["forward_recheck"]["metadata"]) == ()


def test_inverse_search_cli_writes_report(tmp_path) -> None:
    config = _load_json(DEFAULT_TASK6_CONFIG_PATH)
    config["output_dir"] = str(tmp_path / "cli_inverse")
    config["run_metadata_path"] = str(tmp_path / "cli_run_metadata.json")
    config_path = tmp_path / "task6_cli_config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/inverse/run_inverse_search.py",
            "--config",
            str(config_path),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    assert str(Path(config["output_dir"]) / "inverse_report.json") in result.stdout
    assert str(Path(config["output_dir"]) / "inverse_report.md") in result.stdout
