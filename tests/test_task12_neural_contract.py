from __future__ import annotations

import json
from pathlib import Path

from ar_inverse.datasets.build import load_dataset_config, materialize_dataset_samples


TASK12_DATASET_CONFIG_PATH = Path("configs/datasets/task12_directional_medium_dataset.json")
TASK12_TRAINING_CONFIG_PATH = Path("configs/surrogate/task12_directional_neural_medium.json")
TASK12_EVALUATION_CONFIG_PATH = Path("configs/surrogate/task12_directional_neural_evaluation_medium.json")
TASK12_RUNBOOK_PATH = Path("docs/task12_neural_medium_server_handoff.md")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task12_dataset_config_materializes_medium_scale_named_mode_domain() -> None:
    config = load_dataset_config(TASK12_DATASET_CONFIG_PATH)

    assert config["execution_mode"] == "server_only_medium_neural_validation"
    assert config["allow_diagnostic_raw_angles"] is False
    assert config["frozen_direction_contract"]["unsupported_modes"] == ["c_axis"]
    assert config["frozen_forward_metadata_family"]["git_commit"] == "b85a5cb304acbfd5d51133251ef57293bd0abd2b"
    assert config["frozen_forward_metadata_family"]["git_dirty"] is False

    samples = materialize_dataset_samples(config)
    assert len(samples) == 352
    assert {sample.split for sample in samples} == {"train", "validation", "test"}

    modes = {str(sample.direction["direction_mode"]) for sample in samples if sample.direction is not None}
    assert modes == {"inplane_100", "inplane_110"}
    assert all("interface_angle" not in (sample.direction or {}) for sample in samples)
    assert any((sample.direction or {}).get("directional_spread") for sample in samples)
    assert all(
        not sample.direction or str(sample.direction.get("direction_mode")) != "c_axis"
        for sample in samples
    )


def test_task12_training_and_evaluation_configs_record_neural_stack() -> None:
    training_config = _load_json(TASK12_TRAINING_CONFIG_PATH)
    evaluation_config = _load_json(TASK12_EVALUATION_CONFIG_PATH)

    assert training_config["model_type"] == "neural_mlp_spectrum_surrogate"
    assert training_config["execution_mode"] == "server_only_medium_neural_validation"
    assert training_config["hidden_layer_widths"] == [256, 256, 128]
    assert training_config["optimizer"] == "adamw"
    assert training_config["batch_size"] == 32
    assert training_config["device"] == "auto"
    assert training_config["frozen_forward_metadata_family"]["git_dirty"] is False

    assert evaluation_config["checkpoint"] == "outputs/checkpoints/task12_directional_neural_medium/model.pt"
    assert evaluation_config["dataset_manifest"] == "outputs/datasets/task12_directional_medium_neural/dataset.json"
    assert evaluation_config["device"] == "auto"
    assert evaluation_config["held_out_splits"] == ["validation", "test"]


def test_task12_runbook_records_neural_handoff_requirements() -> None:
    runbook = TASK12_RUNBOOK_PATH.read_text(encoding="utf-8")

    assert "Task 12A prepares the first neural surrogate stack only." in runbook
    assert "Task 12B is the" in runbook
    assert "configs/datasets/task12_directional_medium_dataset.json" in runbook
    assert "configs/surrogate/task12_directional_neural_medium.json" in runbook
    assert "configs/surrogate/task12_directional_neural_evaluation_medium.json" in runbook
    assert "model.pt" in runbook
    assert "352" in runbook
    assert "b85a5cb304acbfd5d51133251ef57293bd0abd2b" in runbook
    assert "outputs/runs/task12_neural_medium_server_run_note.md" in runbook
