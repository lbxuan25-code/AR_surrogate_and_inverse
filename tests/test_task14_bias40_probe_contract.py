from __future__ import annotations

import json
from pathlib import Path


TASK14_BIAS40_DATASET_CONFIG_PATH = Path("configs/datasets/task14_bias40_probe_dataset.json")
TASK14_BIAS40_TRAINING_CONFIG_PATH = Path("configs/surrogate/task14_bias40_probe_training.json")
TASK14_BIAS40_EVALUATION_CONFIG_PATH = Path("configs/surrogate/task14_bias40_probe_evaluation.json")
TASK14_BIAS40_HANDOFF_PATH = Path("docs/task14_bias40_probe_handoff.md")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task14_bias40_probe_configs_freeze_widened_bias_contract() -> None:
    dataset_config = _load_json(TASK14_BIAS40_DATASET_CONFIG_PATH)
    training_config = _load_json(TASK14_BIAS40_TRAINING_CONFIG_PATH)
    evaluation_config = _load_json(TASK14_BIAS40_EVALUATION_CONFIG_PATH)

    assert dataset_config["execution_mode"] == "local_preparation_bias40_probe_contract"
    assert dataset_config["upstream_pairing_source_contract"] == "configs/datasets/task14_rmft_anchor_dataset.json"
    assert dataset_config["fixed_bias_grid"] == {
        "bias_min_mev": -40.0,
        "bias_max_mev": 40.0,
        "num_bias": 241,
    }
    assert dataset_config["pairing_representation_contract"]["pairing_representation_version"] == (
        "projected_7plus1_gauge_fixed_v1"
    )
    assert dataset_config["pairing_representation_contract"]["storage_block"] == "controls.pairing_representation"
    assert dataset_config["probe_transport_contract"]["nk"] == 41

    assert training_config["execution_mode"] == "local_preparation_bias40_probe_contract"
    assert training_config["dataset_manifest"] == "outputs/datasets/task14_bias40_probe/dataset.json"
    assert training_config["checkpoint_dir"] == "outputs/checkpoints/task14_bias40_probe"
    assert training_config["output_spectrum_contract"] == {
        "bias_min_mev": -40.0,
        "bias_max_mev": 40.0,
        "num_bias": 241,
    }
    assert training_config["pairing_representation_contract"]["pairing_representation_version"] == (
        "projected_7plus1_gauge_fixed_v1"
    )
    assert training_config["ensemble"]["enabled"] is True

    assert evaluation_config["execution_mode"] == "local_preparation_bias40_probe_contract"
    assert evaluation_config["checkpoint"] == "outputs/checkpoints/task14_bias40_probe/ensemble_manifest.json"
    assert evaluation_config["dataset_manifest"] == "outputs/datasets/task14_bias40_probe/dataset.json"
    assert evaluation_config["output_spectrum_contract"] == {
        "bias_min_mev": -40.0,
        "bias_max_mev": 40.0,
        "num_bias": 241,
    }
    assert evaluation_config["uncertainty_contract"]["threshold_status"] == "probe_only_task14c_v1"


def test_task14_bias40_handoff_records_prep_only_boundary_and_server_commands() -> None:
    handoff = TASK14_BIAS40_HANDOFF_PATH.read_text(encoding="utf-8")

    assert "Task 14C prepares the canonical widened-bias probe contract only." in handoff
    assert "Do not generate the bias40 dataset" in handoff
    assert "bias_min_mev = -40.0" in handoff
    assert "bias_max_mev = 40.0" in handoff
    assert "num_bias = 241" in handoff
    assert "configs/datasets/task14_bias40_probe_dataset.json" in handoff
    assert "configs/surrogate/task14_bias40_probe_training.json" in handoff
    assert "configs/surrogate/task14_bias40_probe_evaluation.json" in handoff
    assert "python scripts/datasets/build_dataset.py --config configs/datasets/task14_bias40_probe_dataset.json" in handoff
    assert "python scripts/surrogate/train_surrogate.py --config configs/surrogate/task14_bias40_probe_training.json" in handoff
    assert "python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task14_bias40_probe_evaluation.json" in handoff
