from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ar_inverse.surrogate.calibration import direction_regime_label, transport_regime_label
from ar_inverse.surrogate.evaluate import DEFAULT_TASK5_CONFIG_PATH, evaluate_surrogate_from_config


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_evaluate_surrogate_from_config_writes_unsafe_regime_report(tmp_path) -> None:
    config = _load_json(DEFAULT_TASK5_CONFIG_PATH)
    config["report_dir"] = str(tmp_path / "evaluation")
    config["run_metadata_path"] = str(tmp_path / "run_metadata.json")
    config_path = tmp_path / "task5_config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report_path, markdown_path = evaluate_surrogate_from_config(config_path)

    assert report_path.exists()
    assert markdown_path.exists()
    assert Path(config["run_metadata_path"]).exists()

    report = _load_json(report_path)
    assert report["run_kind"] == "task5_surrogate_evaluation_and_calibration"
    assert report["evaluation_scope"]["held_out_splits"] == ["validation", "test"]
    assert report["evaluation_scope"]["num_held_out_rows"] == 2
    assert report["calibration_diagnostics"]["unsafe_fraction"] == 1.0
    assert report["fallback_policy"]["unsafe_transport_regimes"]
    assert report["fallback_policy"]["unsafe_direction_regimes"]
    assert set(report["direction_regime_report"]) == {"inplane_110_no_spread", "named_mode_narrow_spread"}
    assert "direct_forward_required" in report["fallback_policy"]["default_action"]
    assert all(not row["safe_for_inverse_acceleration"] for row in report["row_errors"])


def test_repository_task5_report_identifies_unsafe_inverse_regimes() -> None:
    report_path = Path("outputs/runs/task5_surrogate_evaluation/evaluation_report.json")
    markdown_path = Path("outputs/runs/task5_surrogate_evaluation/evaluation_report.md")
    run_metadata_path = Path("outputs/runs/task5_surrogate_evaluation_run_metadata.json")

    assert report_path.exists()
    assert markdown_path.exists()
    assert run_metadata_path.exists()

    report = _load_json(report_path)
    run_metadata = _load_json(run_metadata_path)

    unsafe_regimes = report["fallback_policy"]["unsafe_transport_regimes"]
    assert len(unsafe_regimes) >= 1
    assert unsafe_regimes == run_metadata["unsafe_transport_regimes"]
    assert report["fallback_policy"]["unsafe_direction_regimes"] == run_metadata["unsafe_direction_regimes"]
    assert report["forward_metadata_family"]["forward_interface_version"]
    assert "unsafe transport regimes" in markdown_path.read_text(encoding="utf-8")
    assert "Direction Regimes" in markdown_path.read_text(encoding="utf-8")


def test_evaluate_surrogate_cli_writes_report(tmp_path) -> None:
    config = _load_json(DEFAULT_TASK5_CONFIG_PATH)
    config["report_dir"] = str(tmp_path / "cli_evaluation")
    config["run_metadata_path"] = str(tmp_path / "cli_run_metadata.json")
    config_path = tmp_path / "task5_cli_config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/surrogate/evaluate_surrogate.py",
            "--config",
            str(config_path),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    assert str(Path(config["report_dir"]) / "evaluation_report.json") in result.stdout
    assert str(Path(config["report_dir"]) / "evaluation_report.md") in result.stdout


def test_transport_regime_label_is_stable() -> None:
    assert (
        transport_regime_label({"barrier_z": 0.8, "gamma": 0.95, "temperature_kelvin": 2.5})
        == "high_barrier|low_gamma|low_temp"
    )


def test_direction_regime_label_is_stable() -> None:
    assert direction_regime_label({"direction": {"direction_mode": "inplane_100", "directional_spread": None}}) == (
        "inplane_100_no_spread"
    )
    assert (
        direction_regime_label(
            {"direction": {"direction_mode": "inplane_110", "directional_spread": {"half_width": 0.01}}}
        )
        == "named_mode_narrow_spread"
    )
