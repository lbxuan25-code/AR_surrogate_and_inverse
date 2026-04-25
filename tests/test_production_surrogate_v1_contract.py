from __future__ import annotations

import json
from pathlib import Path

from ar_inverse.datasets.build import load_dataset_config, materialize_dataset_samples
from ar_inverse.surrogate.train import feature_spec_from_config


RUNBOOK_PATH = Path("docs/runbooks/production_surrogate_v1_handoff.md")
DATASET_CONFIG_PATH = Path("configs/datasets/production_surrogate_v1.dataset.json")
TRAINING_CONFIG_PATH = Path("configs/training/production_surrogate_v1.training.json")
EVALUATION_CONFIG_PATH = Path("configs/evaluation/production_surrogate_v1.evaluation.json")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_p1_uses_user_approved_content_based_paths() -> None:
    doc = RUNBOOK_PATH.read_text(encoding="utf-8")

    assert "P1 prepares the first user-approved production-scale" in doc
    assert "configs/datasets/production_surrogate_v1.dataset.json" in doc
    assert "configs/training/production_surrogate_v1.training.json" in doc
    assert "configs/evaluation/production_surrogate_v1.evaluation.json" in doc
    assert "supersedes Codex-proposed S9/S10" in doc
    assert "not the canonical P1 launch path" in doc


def test_dataset_contract_freezes_rectified_sampling_and_local_worker_target() -> None:
    dataset = _load_json(DATASET_CONFIG_PATH)

    assert dataset["dataset_id"] == "production_surrogate_v1"
    assert dataset["num_workers"] == 8
    assert dataset["row_budget"]["recommended_total_rows"] == 8192
    assert dataset["row_budget"]["split_targets"] == {
        "train": 6144,
        "validation": 1024,
        "test": 1024,
    }
    assert dataset["pairing_representation_contract"]["pairing_representation_version"] == (
        "projected_7plus1_gauge_fixed_v1"
    )
    assert dataset["pairing_representation_contract"]["gauge_fixing"] == "global_phase_only"
    assert dataset["pairing_representation_contract"]["further_compression"] == "forbidden"
    assert dataset["sampling_policy_contract"]["source_document"] == "docs/contracts/sampling_policy_v2.md"
    assert dataset["rmft_source_projection"]["required_for_materialization"] is True
    assert dataset["rmft_source_projection"]["projection_examples_csv"] == (
        "outputs/source/round2_projection_examples.csv"
    )
    assert dataset["joint_sampling_contract"]["enabled"] is True
    assert dataset["joint_sampling_contract"]["source_document"] == "docs/contracts/joint_sampling_contract.md"
    assert dataset["direction_contract"]["unsupported_modes"] == ["c_axis"]
    assert dataset["direction_contract"]["diagnostic_raw_angles"] == "excluded"
    assert dataset["active_learning_reference"]["status"] == "deferred_until_after_production_v1_review"


def test_dataset_contract_materializes_executable_production_samples() -> None:
    config = load_dataset_config(DATASET_CONFIG_PATH)
    samples = materialize_dataset_samples(config)

    assert len(samples) == 8192
    assert sum(sample.split == "train" for sample in samples) == 6144
    assert sum(sample.split == "validation" for sample in samples) == 1024
    assert sum(sample.split == "test" for sample in samples) == 1024
    assert {sample.group_labels["pairing_source_role"] for sample in samples} == {
        "anchor",
        "neighborhood",
        "bridge",
    }
    role_counts = {
        role: sum(sample.group_labels["pairing_source_role"] == role for sample in samples)
        for role in ("anchor", "neighborhood", "bridge")
    }
    assert role_counts == {"anchor": 3072, "neighborhood": 3072, "bridge": 2048}
    assert {sample.group_labels["nuisance_regime"] for sample in samples} == {
        "core_sharp",
        "core_transition",
        "core_broad",
        "guard_band_sharp",
        "guard_band_transition",
        "guard_band_broad",
    }
    assert {sample.group_labels["tb_regime"] for sample in samples} == {"near_baseline", "edge_probe"}
    tb_counts = {
        regime: sum(sample.group_labels["tb_regime"] == regime for sample in samples)
        for regime in ("near_baseline", "edge_probe")
    }
    assert tb_counts == {"near_baseline": 6144, "edge_probe": 2048}
    assert {sample.direction["direction_mode"] for sample in samples if sample.direction} == {
        "inplane_100",
        "inplane_110",
    }
    assert sum(not sample.direction.get("directional_spread") for sample in samples if sample.direction) == 4096
    assert sum(bool(sample.direction.get("directional_spread")) for sample in samples if sample.direction) == 4096
    assert not any(sample.direction and sample.direction.get("direction_mode") == "c_axis" for sample in samples)
    assert all(sample.pairing_control_mode == "absolute_meV" for sample in samples)
    assert all(sample.pairing_representation for sample in samples)
    assert all(sample.source_provenance for sample in samples)


def test_training_contract_keeps_s7_capacity_and_requires_cuda() -> None:
    training = _load_json(TRAINING_CONFIG_PATH)

    assert training["model_type"] == "neural_residual_mlp_spectrum_surrogate"
    assert training["feature_spec_id"] == "projected_7plus1_complex_v1"
    assert "delta_zz_s_re" in feature_spec_from_config(training).names
    assert "delta_zx_s_im" in feature_spec_from_config(training).names
    assert training["residual_hidden_width"] == 384
    assert training["residual_num_blocks"] == 5
    assert training["batch_size"] == 48
    assert training["require_cuda"] is True
    assert training["loss"]["kind"] == "weighted_mse_plus_first_difference"
    assert training["ensemble"]["enabled"] is False
    assert training["ensemble"]["policy"] == "single_member_first_production_run"
    assert training["observability_standard_reference"] == "docs/standards/training_observability_standard.md"
    assert training["model_capacity_decision_reference"] == "docs/model_capacity_decision_rules.md"
    assert training["active_learning_reference"]["status"] == "deferred_not_part_of_production_v1"


def test_evaluation_contract_requires_grouped_errors_and_representative_plots() -> None:
    evaluation = _load_json(EVALUATION_CONFIG_PATH)

    assert evaluation["checkpoint"] == "outputs/checkpoints/production_surrogate_v1/model.pt"
    assert evaluation["dataset_manifest"] == "outputs/datasets/production_surrogate_v1/dataset.json"
    assert evaluation["require_cuda"] is True
    assert evaluation["held_out_splits"] == ["validation", "test"]
    assert "grouped_error_report.json" in evaluation["required_reports"]
    assert evaluation["required_figures"] == [
        "figures/best_spectrum_comparison.png",
        "figures/median_spectrum_comparison.png",
        "figures/worst_spectrum_comparison.png",
    ]
    assert evaluation["grouped_error_axes"] == [
        "direction_mode",
        "direction_spread_regime",
        "pairing_source_role",
        "nuisance_regime",
        "tb_regime",
    ]
    assert evaluation["safe_error_thresholds"]["rmse"] == 0.03
    assert evaluation["safe_error_thresholds"]["max_abs_error"] == 0.075


def test_runbook_freezes_exact_p2_commands_and_artifact_boundary() -> None:
    doc = RUNBOOK_PATH.read_text(encoding="utf-8")

    assert "python scripts/datasets/build_dataset.py" in doc
    assert "--config configs/datasets/production_surrogate_v1.dataset.json" in doc
    assert "--num-workers 8" in doc
    assert "--force" in doc
    assert "python scripts/surrogate/train_surrogate.py" in doc
    assert "--config configs/training/production_surrogate_v1.training.json" in doc
    assert "python scripts/surrogate/evaluate_surrogate.py" in doc
    assert "--config configs/evaluation/production_surrogate_v1.evaluation.json" in doc
    assert "Heavy Artifacts Kept Local" in doc
    assert "Compact Artifacts For Review" in doc
    assert "outputs/runs/production_surrogate_v1/training_observability/training_history.json" in doc
    assert "outputs/runs/production_surrogate_v1/evaluation/grouped_error_report.json" in doc
    assert "P2 may run the heavy pipeline after user acceptance" in doc
