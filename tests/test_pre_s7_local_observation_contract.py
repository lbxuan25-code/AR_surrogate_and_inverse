from __future__ import annotations

import json
from pathlib import Path


DATASET_CONFIG_PATH = Path("configs/datasets/local/pre_s7_local_observation_dataset.json")
TRAIN_CONFIG_PATH = Path("configs/surrogate/local/pre_s7_local_observation_training.json")
EVAL_CONFIG_PATH = Path("configs/surrogate/local/pre_s7_local_observation_evaluation.json")
RUNBOOK_PATH = Path("docs/runbooks/pre_s7_local_training_runbook.md")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_pre_s7_local_dataset_contract_exposes_parallel_workers_and_group_labels() -> None:
    config = _load_json(DATASET_CONFIG_PATH)

    assert config["config_role"] == "pre_s7_local_observation_dataset"
    assert config["num_workers"] == 8
    assert config["expected_num_rows"] == 96
    assert config["output_dir"] == "outputs/datasets/pre_s7_local_observation"
    assert config["run_metadata_path"] == "outputs/runs/pre_s7_local_observation/dataset_run_metadata.json"
    assert config["sampling_policy"]["pairing_source_role_targets"] == {
        "anchor": 32,
        "neighborhood": 32,
        "bridge": 32,
    }
    assert config["sampling_policy"]["tb_regime_targets"] == {"tb_unimplemented_local": 96}
    assert all("group_labels" in grid for grid in config["sample_grids"])


def test_pre_s7_local_training_contract_requires_cuda_and_observability_outputs() -> None:
    config = _load_json(TRAIN_CONFIG_PATH)

    assert config["model_type"] == "neural_residual_mlp_spectrum_surrogate"
    assert config["residual_hidden_width"] == 384
    assert config["residual_num_blocks"] == 5
    assert config["batch_size"] == 24
    assert config["device"] == "auto"
    assert config["require_cuda"] is True
    assert config["observability_dir"] == "outputs/runs/pre_s7_local_observation/training_observability"


def test_pre_s7_local_evaluation_contract_and_runbook_point_to_grouped_review_outputs() -> None:
    config = _load_json(EVAL_CONFIG_PATH)
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")

    assert config["report_dir"] == "outputs/runs/pre_s7_local_observation/evaluation"
    assert config["run_metadata_path"] == "outputs/runs/pre_s7_local_observation/evaluation_run_metadata.json"
    assert config["device"] == "auto"
    assert config["require_cuda"] is True
    assert "grouped_error_report.json" in runbook
    assert "best_spectrum_comparison.png" in runbook
    assert "median_spectrum_comparison.png" in runbook
    assert "worst_spectrum_comparison.png" in runbook
