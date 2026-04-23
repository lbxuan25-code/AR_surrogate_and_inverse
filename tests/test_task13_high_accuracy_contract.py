from __future__ import annotations

import json
from pathlib import Path

from ar_inverse.datasets.build import load_dataset_config, materialize_dataset_samples


TASK13_DATASET_CONFIG_PATH = Path("configs/datasets/task13_directional_large_accuracy_dataset.json")
TASK13_TRAINING_CONFIG_PATH = Path("configs/surrogate/task13_directional_high_accuracy_large.json")
TASK13_EVALUATION_CONFIG_PATH = Path("configs/surrogate/task13_directional_high_accuracy_evaluation_large.json")
TASK13_RUNBOOK_PATH = Path("docs/task13_high_accuracy_large_server_handoff.md")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task13_dataset_config_materializes_large_scale_named_mode_domain() -> None:
    config = load_dataset_config(TASK13_DATASET_CONFIG_PATH)

    assert config["execution_mode"] == "server_only_large_accuracy_contract"
    assert config["allow_diagnostic_raw_angles"] is False
    assert config["expected_num_rows"] == 4096
    assert config["frozen_direction_contract"]["unsupported_modes"] == ["c_axis"]
    assert config["frozen_forward_metadata_family"]["git_commit"] == "b85a5cb304acbfd5d51133251ef57293bd0abd2b"
    assert config["frozen_forward_metadata_family"]["git_dirty"] is False
    assert config["sampling_policy"]["split_targets"] == {"train": 3072, "validation": 512, "test": 512}
    assert config["sampling_policy"]["regime_targets"] == {
        "inplane_100_no_spread": 1024,
        "inplane_110_no_spread": 1024,
        "named_mode_narrow_spread": 2048,
    }

    samples = materialize_dataset_samples(config)
    assert len(samples) == 4096
    assert {sample.split for sample in samples} == {"train", "validation", "test"}
    assert all(sample.bias_grid["num_bias"] == 121 for sample in samples)
    assert all(sample.transport_controls["nk"] == 41 for sample in samples)

    modes = {str(sample.direction["direction_mode"]) for sample in samples if sample.direction is not None}
    assert modes == {"inplane_100", "inplane_110"}
    assert all("interface_angle" not in (sample.direction or {}) for sample in samples)
    assert any((sample.direction or {}).get("directional_spread") for sample in samples)


def test_task13_training_and_evaluation_configs_record_high_accuracy_contract() -> None:
    training_config = _load_json(TASK13_TRAINING_CONFIG_PATH)
    evaluation_config = _load_json(TASK13_EVALUATION_CONFIG_PATH)

    assert training_config["model_type"] == "neural_residual_mlp_spectrum_surrogate"
    assert training_config["execution_mode"] == "server_only_large_accuracy_contract"
    assert training_config["normalization"] == "layernorm"
    assert training_config["activation"] == "gelu"
    assert training_config["optimizer"] == "adamw"
    assert training_config["loss"]["kind"] == "weighted_mse_plus_first_difference"
    assert training_config["ensemble"]["enabled"] is True
    assert len(training_config["ensemble"]["seeds"]) == 3

    assert evaluation_config["checkpoint"] == "outputs/checkpoints/task13_directional_high_accuracy_large/ensemble_manifest.json"
    assert evaluation_config["dataset_manifest"] == "outputs/datasets/task13_directional_large_accuracy/dataset.json"
    assert evaluation_config["device"] == "auto"
    assert evaluation_config["held_out_splits"] == ["validation", "test"]
    assert evaluation_config["uncertainty_contract"]["threshold_status"] == (
        "pending_held_out_calibration_before_task13b_launch"
    )


def test_task13_runbook_records_large_scale_accuracy_handoff_requirements() -> None:
    runbook = TASK13_RUNBOOK_PATH.read_text(encoding="utf-8")

    assert "Task 13A prepares the first high-accuracy large-scale surrogate contract only." in runbook
    assert "Task 13B is the actual heavy server run." in runbook
    assert "4096" in runbook
    assert "3072 / 512 / 512" in runbook
    assert "configs/datasets/task13_directional_large_accuracy_dataset.json" in runbook
    assert "configs/surrogate/task13_directional_high_accuracy_large.json" in runbook
    assert "configs/surrogate/task13_directional_high_accuracy_evaluation_large.json" in runbook
    assert "ensemble_manifest.json" in runbook
    assert "pending_held_out_calibration_before_task13b_launch" in runbook
    assert "outputs/runs/task13_high_accuracy_large_server_run_note.md" in runbook
