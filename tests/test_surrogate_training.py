from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from ar_inverse.surrogate.models import NEURAL_MLP_MODEL_TYPE, RidgeLinearSpectrumSurrogate, load_surrogate_checkpoint
from ar_inverse.surrogate.train import (
    DEFAULT_DIRECTIONAL_SURROGATE_CHECKPOINT_DIR,
    DEFAULT_DIRECTIONAL_SURROGATE_CONFIG_PATH,
    load_dataset_arrays,
    train_surrogate_from_config,
)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_train_surrogate_from_config_writes_checkpoint_metrics_and_card(tmp_path) -> None:
    config = _load_json(DEFAULT_DIRECTIONAL_SURROGATE_CONFIG_PATH)
    config["checkpoint_dir"] = str(tmp_path / "checkpoint")
    config["run_metadata_path"] = str(tmp_path / "run_metadata.json")
    config["model_card_purpose_lines"] = [
        "Custom purpose line one.",
        "Custom purpose line two.",
    ]
    config["model_card_limitations_lines"] = [
        "Custom limitation line one.",
        "Custom limitation line two.",
    ]
    config_path = tmp_path / "task4_config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path, metrics_path, model_card_path = train_surrogate_from_config(config_path)

    assert checkpoint_path.exists()
    assert metrics_path.exists()
    assert model_card_path.exists()
    assert Path(config["run_metadata_path"]).exists()

    metrics = _load_json(metrics_path)
    assert metrics["run_kind"] == "task9_directional_surrogate_smoke_training"
    assert metrics["model_type"] == "ridge_linear_spectrum_surrogate"
    assert metrics["dataset_id"] == "task8_directional_smoke_v1"
    assert metrics["direction_support"]["direction_regime_counts"]["named_mode_narrow_spread"] == 1
    assert "direction_raw_interface_angle" in metrics["feature_spec"]["names"]
    assert "interface_angle" not in metrics["feature_spec"]["names"]
    assert metrics["held_out_splits"] == ["validation", "test"]
    assert set(metrics["splits"]) == {"train", "validation", "test"}
    assert metrics["splits"]["validation"]["num_rows"] == 1
    assert metrics["splits"]["test"]["num_rows"] == 1

    model_card = model_card_path.read_text(encoding="utf-8")
    assert "Forward Metadata Family" in model_card
    assert "Task 9 Directional Surrogate Smoke Checkpoint" in model_card
    assert "task8_directional_smoke_v1" in model_card
    assert "Direction Support" in model_card
    assert "Custom purpose line one." in model_card
    assert "Custom limitation line two." in model_card
    assert "This checkpoint is trained on the tiny Task 8 directional smoke dataset" not in model_card


def test_saved_surrogate_checkpoint_predicts_full_spectrum() -> None:
    dataset = load_dataset_arrays("outputs/datasets/task8_directional_smoke/dataset.json")
    model = RidgeLinearSpectrumSurrogate.load(DEFAULT_DIRECTIONAL_SURROGATE_CHECKPOINT_DIR / "model.npz")

    prediction = model.predict(dataset["features"])

    assert prediction.shape == dataset["targets"].shape
    assert prediction.shape[1] == len(dataset["bias_mev"])
    assert np.all(np.isfinite(prediction))


def test_repository_task9_smoke_artifacts_record_dataset_and_held_out_metrics() -> None:
    checkpoint_dir = DEFAULT_DIRECTIONAL_SURROGATE_CHECKPOINT_DIR
    checkpoint_path = checkpoint_dir / "model.npz"
    metrics_path = checkpoint_dir / "metrics.json"
    model_card_path = checkpoint_dir / "model_card.md"
    run_metadata_path = Path("outputs/runs/task9_directional_surrogate_smoke_run_metadata.json")

    assert checkpoint_path.exists()
    assert metrics_path.exists()
    assert model_card_path.exists()
    assert run_metadata_path.exists()

    metrics = _load_json(metrics_path)
    run_metadata = _load_json(run_metadata_path)

    assert metrics["run_kind"] == "task9_directional_surrogate_smoke_training"
    assert metrics["dataset_manifest"] == "outputs/datasets/task8_directional_smoke/dataset.json"
    assert metrics["direction_support"]["direction_modes"] == ["inplane_100", "inplane_110"]
    assert metrics["held_out_splits"] == ["validation", "test"]
    assert "validation" in metrics["splits"]
    assert "test" in metrics["splits"]
    assert run_metadata["forward_metadata_family"]["forward_interface_version"]
    assert run_metadata["model_card"] == str(model_card_path)


def test_train_surrogate_cli_writes_outputs(tmp_path) -> None:
    config = _load_json(DEFAULT_DIRECTIONAL_SURROGATE_CONFIG_PATH)
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


def test_train_neural_surrogate_from_config_writes_pt_checkpoint_and_metadata(tmp_path) -> None:
    config = _load_json(DEFAULT_DIRECTIONAL_SURROGATE_CONFIG_PATH)
    config["model_type"] = NEURAL_MLP_MODEL_TYPE
    config["checkpoint_dir"] = str(tmp_path / "neural_checkpoint")
    config["run_metadata_path"] = str(tmp_path / "neural_run_metadata.json")
    config["hidden_layer_widths"] = [16, 16]
    config["activation"] = "relu"
    config["optimizer"] = "adam"
    config["learning_rate"] = 0.01
    config["batch_size"] = 2
    config["max_epochs"] = 12
    config["early_stopping_patience"] = 3
    config["random_seed"] = 7
    config["device"] = "cpu"
    config["run_kind"] = "test_task12_neural_training"
    config_path = tmp_path / "task12_neural_config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path, metrics_path, model_card_path = train_surrogate_from_config(config_path)

    assert checkpoint_path.suffix == ".pt"
    assert checkpoint_path.exists()
    assert metrics_path.exists()
    assert model_card_path.exists()

    metrics = _load_json(metrics_path)
    run_metadata = _load_json(Path(config["run_metadata_path"]))
    model = load_surrogate_checkpoint(checkpoint_path)
    dataset = load_dataset_arrays("outputs/datasets/task8_directional_smoke/dataset.json")
    prediction = model.predict(dataset["features"], device="cpu")

    assert metrics["model_type"] == NEURAL_MLP_MODEL_TYPE
    assert metrics["training"]["optimizer"] == "adam"
    assert metrics["training"]["batch_size"] == 2
    assert metrics["training"]["random_seed"] == 7
    assert metrics["training"]["requested_device"] == "cpu"
    assert run_metadata["model_type"] == NEURAL_MLP_MODEL_TYPE
    assert run_metadata["optimizer"] == "adam"
    assert run_metadata["batch_size"] == 2
    assert run_metadata["requested_device"] == "cpu"
    assert prediction.shape == dataset["targets"].shape
    assert np.all(np.isfinite(prediction))
