from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from ar_inverse.surrogate.models import RidgeLinearSpectrumSurrogate
from ar_inverse.surrogate.train import (
    DEFAULT_TASK4_CHECKPOINT_DIR,
    DEFAULT_TASK4_CONFIG_PATH,
    load_dataset_arrays,
    train_surrogate_from_config,
)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_train_surrogate_from_config_writes_checkpoint_metrics_and_card(tmp_path) -> None:
    config = _load_json(DEFAULT_TASK4_CONFIG_PATH)
    config["checkpoint_dir"] = str(tmp_path / "checkpoint")
    config["run_metadata_path"] = str(tmp_path / "run_metadata.json")
    config_path = tmp_path / "task4_config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path, metrics_path, model_card_path = train_surrogate_from_config(config_path)

    assert checkpoint_path.exists()
    assert metrics_path.exists()
    assert model_card_path.exists()
    assert Path(config["run_metadata_path"]).exists()

    metrics = _load_json(metrics_path)
    assert metrics["model_type"] == "ridge_linear_spectrum_surrogate"
    assert metrics["dataset_id"] == "task3_orchestration_smoke_v1"
    assert metrics["held_out_splits"] == ["validation", "test"]
    assert set(metrics["splits"]) == {"train", "validation", "test"}
    assert metrics["splits"]["validation"]["num_rows"] == 1
    assert metrics["splits"]["test"]["num_rows"] == 1

    model_card = model_card_path.read_text(encoding="utf-8")
    assert "Forward Metadata Family" in model_card
    assert "task3_orchestration_smoke_v1" in model_card


def test_saved_surrogate_checkpoint_predicts_full_spectrum() -> None:
    dataset = load_dataset_arrays("outputs/datasets/task3_orchestration_smoke/dataset.json")
    model = RidgeLinearSpectrumSurrogate.load(DEFAULT_TASK4_CHECKPOINT_DIR / "model.npz")

    prediction = model.predict(dataset["features"])

    assert prediction.shape == dataset["targets"].shape
    assert prediction.shape[1] == len(dataset["bias_mev"])
    assert np.all(np.isfinite(prediction))


def test_repository_task4_artifacts_record_dataset_and_held_out_metrics() -> None:
    checkpoint_dir = DEFAULT_TASK4_CHECKPOINT_DIR
    checkpoint_path = checkpoint_dir / "model.npz"
    metrics_path = checkpoint_dir / "metrics.json"
    model_card_path = checkpoint_dir / "model_card.md"
    run_metadata_path = Path("outputs/runs/task4_linear_surrogate_run_metadata.json")

    assert checkpoint_path.exists()
    assert metrics_path.exists()
    assert model_card_path.exists()
    assert run_metadata_path.exists()

    metrics = _load_json(metrics_path)
    run_metadata = _load_json(run_metadata_path)

    assert metrics["dataset_manifest"] == "outputs/datasets/task3_orchestration_smoke/dataset.json"
    assert metrics["held_out_splits"] == ["validation", "test"]
    assert "validation" in metrics["splits"]
    assert "test" in metrics["splits"]
    assert run_metadata["forward_metadata_family"]["forward_interface_version"]
    assert run_metadata["model_card"] == str(model_card_path)


def test_train_surrogate_cli_writes_outputs(tmp_path) -> None:
    config = _load_json(DEFAULT_TASK4_CONFIG_PATH)
    config["checkpoint_dir"] = str(tmp_path / "cli_checkpoint")
    config["run_metadata_path"] = str(tmp_path / "cli_run_metadata.json")
    config_path = tmp_path / "task4_cli_config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/surrogate/train_surrogate.py",
            "--config",
            str(config_path),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    assert str(Path(config["checkpoint_dir"]) / "model.npz") in result.stdout
    assert str(Path(config["checkpoint_dir"]) / "metrics.json") in result.stdout
    assert str(Path(config["checkpoint_dir"]) / "model_card.md") in result.stdout
