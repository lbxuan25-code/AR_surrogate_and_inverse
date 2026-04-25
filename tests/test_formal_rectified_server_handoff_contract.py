from __future__ import annotations

import json
from pathlib import Path


DOC_PATH = Path("docs/formal_rectified_server_handoff.md")
DATASET_CONFIG_PATH = Path("configs/datasets/production/rectified_large_production_dataset.json")
TRAINING_CONFIG_PATH = Path("configs/surrogate/production/rectified_large_production_training.json")
EVALUATION_CONFIG_PATH = Path("configs/surrogate/production/rectified_large_production_evaluation.json")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_formal_rectified_handoff_promotes_the_large_production_draft() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "first formal large-scale post-rectification production" in doc
    assert "supersedes the earlier 96-row" in doc
    assert "`pre_s7_local_observation`" in doc
    assert "baseline" in doc
    assert "no longer the final formal large-scale goal" in doc
    assert "goal" in doc
    assert "without reviving the older" in doc
    assert "`Task 15A` medium draft" in doc


def test_formal_rectified_handoff_freezes_exact_large_production_config_paths_and_commands() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")
    dataset = _load_json(DATASET_CONFIG_PATH)
    training = _load_json(TRAINING_CONFIG_PATH)
    evaluation = _load_json(EVALUATION_CONFIG_PATH)

    assert "configs/datasets/production/rectified_large_production_dataset.json" in doc
    assert "configs/surrogate/production/rectified_large_production_training.json" in doc
    assert "configs/surrogate/production/rectified_large_production_evaluation.json" in doc
    assert "python scripts/datasets/build_dataset.py" in doc
    assert "--num-workers 16" in doc
    assert "python scripts/surrogate/train_surrogate.py" in doc
    assert "python scripts/surrogate/evaluate_surrogate.py" in doc

    assert dataset["row_budget"]["recommended_total_rows"] == 8192
    assert dataset["num_workers"] == 16
    assert dataset["pairing_representation_contract"]["pairing_representation_version"] == "projected_7plus1_gauge_fixed_v1"
    assert dataset["pairing_representation_contract"]["global_phase_only"] is True
    assert dataset["pairing_representation_contract"]["further_compression"] == "forbidden"
    assert dataset["sampling_policy_contract"]["source_document"] == "docs/contracts/sampling_policy_v2.md"
    assert dataset["joint_sampling_contract"]["source_document"] == "docs/contracts/joint_sampling_contract.md"
    assert training["residual_hidden_width"] == 384
    assert training["residual_num_blocks"] == 5
    assert training["require_cuda"] is True
    assert training["active_learning_reference"]["status"] == "deferred_not_part_of_this_formal_training_run"
    assert evaluation["require_cuda"] is True
    assert evaluation["active_learning_reference"]["status"] == "deferred_not_part_of_this_formal_evaluation_run"


def test_formal_rectified_handoff_freezes_returned_artifacts_and_server_review_gate() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "Heavy Artifacts That Must Stay On The Server" in doc
    assert "forward_outputs/" in doc
    assert "Compact Artifacts That Must Return To GitHub Review" in doc
    assert "outputs/datasets/rectified_large_production/dataset.json" in doc
    assert "outputs/checkpoints/rectified_large_production/ensemble_manifest.json" in doc
    assert "outputs/runs/rectified_large_production/training_observability/training_history.json" in doc
    assert "outputs/runs/rectified_large_production_evaluation/grouped_error_report.json" in doc
    assert "outputs/runs/rectified_large_production_evaluation/figures/worst_spectrum_comparison.png" in doc
    assert "The review gate is still mandatory." in doc
