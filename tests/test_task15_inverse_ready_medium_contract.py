from __future__ import annotations

import json
from pathlib import Path


TASK15_DATASET_CONFIG_PATH = Path("configs/datasets/task15_inverse_ready_medium_dataset.json")
TASK15_TRAINING_CONFIG_PATH = Path("configs/surrogate/task15_inverse_ready_medium_training.json")
TASK15_EVALUATION_CONFIG_PATH = Path("configs/surrogate/task15_inverse_ready_medium_evaluation.json")
TASK15_HANDOFF_PATH = Path("docs/task15_inverse_ready_medium_handoff.md")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task15_medium_dataset_contract_freezes_budget_and_upstream_dependencies() -> None:
    dataset_config = _load_json(TASK15_DATASET_CONFIG_PATH)

    assert dataset_config["config_role"] == "current_task15_inverse_ready_medium_dataset_contract"
    assert dataset_config["execution_mode"] == "local_preparation_inverse_ready_medium_contract"
    assert dataset_config["dataset_id"] == "task15_inverse_ready_medium_dataset_v1"
    assert dataset_config["sampling_policy_id"] == "task15_inverse_ready_medium_dataset_v1"
    assert dataset_config["allow_diagnostic_raw_angles"] is False
    assert dataset_config["upstream_pairing_source_contract"] == "configs/datasets/task14_rmft_anchor_dataset.json"
    assert dataset_config["upstream_bias_contract"] == "configs/datasets/task14_bias40_probe_dataset.json"
    assert dataset_config["upstream_transport_contract"] == "docs/task14_transport_domain_contract.md"
    assert dataset_config["upstream_tb_contract"] == "configs/datasets/task14_tb_pilot_dataset.json"
    assert dataset_config["row_budget"] == {
        "total_rows": 9600,
        "split_targets": {"train": 7680, "validation": 960, "test": 960},
    }
    assert dataset_config["sampling_policy"]["pairing_source_role_targets"] == {
        "anchor": 3840,
        "neighborhood": 3840,
        "bridge": 1920,
    }
    assert dataset_config["sampling_policy"]["direction_regime_targets"] == {
        "inplane_100_no_spread": 3600,
        "inplane_110_no_spread": 3600,
        "named_mode_narrow_spread": 2400,
    }
    assert dataset_config["sampling_policy"]["transport_tier_targets"] == {"core": 7680, "guard_band": 1920}
    assert dataset_config["sampling_policy"]["tb_pilot_band_targets"] == {
        "near_baseline": 6720,
        "edge_probe": 2880,
    }
    assert dataset_config["fixed_bias_grid"] == {
        "bias_min_mev": -40.0,
        "bias_max_mev": 40.0,
        "num_bias": 241,
    }
    assert dataset_config["transport_domain_contract"]["fixed_nk"] == 41
    assert dataset_config["transport_domain_contract"]["core_region"]["target_fraction"] == 0.80
    assert dataset_config["transport_domain_contract"]["guard_band_region"]["target_fraction"] == 0.20
    assert list(dataset_config["tb_pilot_contract"]["coordinates"]) == [
        "mu_shift",
        "bandwidth_scale",
        "interlayer_scale",
        "orbital_splitting_shift",
        "hybridization_scale",
    ]
    assert dataset_config["tb_pilot_contract"]["sampling_structure"]["near_baseline_band"]["target_fraction"] == 0.70
    assert dataset_config["tb_pilot_contract"]["sampling_structure"]["edge_probe_band"]["target_fraction"] == 0.30
    assert dataset_config["frozen_direction_contract"]["supported_truth_grade_modes"] == [
        "inplane_100",
        "inplane_110",
    ]
    assert dataset_config["frozen_direction_contract"]["unsupported_modes"] == ["c_axis"]


def test_task15_training_and_evaluation_configs_freeze_inverse_ready_medium_contract() -> None:
    training_config = _load_json(TASK15_TRAINING_CONFIG_PATH)
    evaluation_config = _load_json(TASK15_EVALUATION_CONFIG_PATH)

    assert training_config["config_role"] == "current_task15_inverse_ready_medium_training_contract"
    assert training_config["execution_mode"] == "local_preparation_inverse_ready_medium_contract"
    assert training_config["dataset_manifest"] == "outputs/datasets/task15_inverse_ready_medium/dataset.json"
    assert training_config["checkpoint_dir"] == "outputs/checkpoints/task15_inverse_ready_medium"
    assert training_config["row_budget"] == {
        "total_rows": 9600,
        "train_rows": 7680,
        "validation_rows": 960,
        "test_rows": 960,
    }
    assert training_config["pairing_representation_contract"]["pairing_representation_version"] == (
        "projected_7plus1_gauge_fixed_v1"
    )
    assert training_config["tb_pilot_contract"]["tb_coordinate_system_version"] == "task14_tb_pilot_latent_v1"
    assert training_config["output_spectrum_contract"] == {
        "bias_min_mev": -40.0,
        "bias_max_mev": 40.0,
        "num_bias": 241,
    }
    assert training_config["ensemble"]["enabled"] is True
    assert training_config["ensemble"]["seeds"] == [1103, 2207, 3301]
    assert training_config["frozen_direction_contract"]["unsupported_modes"] == ["c_axis"]

    assert evaluation_config["config_role"] == "current_task15_inverse_ready_medium_evaluation_contract"
    assert evaluation_config["execution_mode"] == "local_preparation_inverse_ready_medium_contract"
    assert evaluation_config["checkpoint"] == "outputs/checkpoints/task15_inverse_ready_medium/ensemble_manifest.json"
    assert evaluation_config["dataset_manifest"] == "outputs/datasets/task15_inverse_ready_medium/dataset.json"
    assert evaluation_config["row_budget"] == {
        "total_rows": 9600,
        "validation_rows": 960,
        "test_rows": 960,
    }
    assert evaluation_config["output_spectrum_contract"] == {
        "bias_min_mev": -40.0,
        "bias_max_mev": 40.0,
        "num_bias": 241,
    }
    assert evaluation_config["transport_domain_contract"]["source_document"] == "docs/task14_transport_domain_contract.md"
    assert evaluation_config["tb_pilot_contract"]["tb_coordinate_system_version"] == "task14_tb_pilot_latent_v1"
    assert evaluation_config["uncertainty_contract"]["threshold_status"] == "prelaunch_fixed_task15b_v1"
    assert evaluation_config["uncertainty_contract"]["report_axes"] == [
        "bias_sub_window",
        "transport_sub_range",
        "direction_regime",
        "tb_pilot_regime",
    ]


def test_task15_handoff_records_medium_contract_commands_and_review_boundary() -> None:
    handoff = TASK15_HANDOFF_PATH.read_text(encoding="utf-8")

    assert "Task 15A prepares the first inverse-ready medium-scale contract only." in handoff
    assert "total rows: `9600`" in handoff
    assert "train rows: `7680`" in handoff
    assert "validation rows: `960`" in handoff
    assert "test rows: `960`" in handoff
    assert "anchor = 3840" in handoff
    assert "neighborhood = 3840" in handoff
    assert "bridge = 1920" in handoff
    assert "core = 7680" in handoff
    assert "guard_band = 1920" in handoff
    assert "near_baseline = 6720" in handoff
    assert "edge_probe = 2880" in handoff
    assert "configs/datasets/task15_inverse_ready_medium_dataset.json" in handoff
    assert "configs/surrogate/task15_inverse_ready_medium_training.json" in handoff
    assert "configs/surrogate/task15_inverse_ready_medium_evaluation.json" in handoff
    assert "python scripts/datasets/build_dataset.py --config configs/datasets/task15_inverse_ready_medium_dataset.json" in handoff
    assert "python scripts/surrogate/train_surrogate.py --config configs/surrogate/task15_inverse_ready_medium_training.json" in handoff
    assert "python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task15_inverse_ready_medium_evaluation.json" in handoff
    assert "outputs/runs/task15_inverse_ready_medium_server_run_note.md" in handoff
    assert "Task 15A is not the later server run." in handoff
