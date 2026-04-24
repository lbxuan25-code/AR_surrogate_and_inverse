from __future__ import annotations

import json
from pathlib import Path


TASK14_TB_PILOT_CONFIG_PATH = Path("configs/datasets/task14_tb_pilot_dataset.json")
TASK14_TB_PILOT_DOC_PATH = Path("docs/task14_tb_pilot_contract.md")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task14_tb_pilot_dataset_contract_freezes_exact_coordinate_set() -> None:
    config = _load_json(TASK14_TB_PILOT_CONFIG_PATH)

    assert config["config_role"] == "current_task14_tb_pilot_dataset_contract"
    assert config["execution_mode"] == "local_contract_only_tb_pilot_preparation"
    assert config["dataset_id"] == "task14_tb_pilot_dataset_v1"
    assert config["sampling_policy_id"] == "task14_tb_pilot_dataset_v1"
    assert config["upstream_pairing_source_contract"] == "configs/datasets/task14_rmft_anchor_dataset.json"
    assert config["upstream_bias_contract"] == "configs/datasets/task14_bias40_probe_dataset.json"
    assert config["upstream_transport_contract"] == "docs/task14_transport_domain_contract.md"
    assert config["allow_diagnostic_raw_angles"] is False
    assert config["frozen_direction_contract"]["unsupported_modes"] == ["c_axis"]
    assert config["pairing_representation_contract"]["pairing_representation_version"] == (
        "projected_7plus1_gauge_fixed_v1"
    )

    tb_contract = config["tb_pilot_contract"]
    assert tb_contract["tb_coordinate_system_version"] == "task14_tb_pilot_latent_v1"
    assert tb_contract["storage_block"] == "controls.tb_pilot_coordinates"
    assert list(tb_contract["coordinates"]) == [
        "mu_shift",
        "bandwidth_scale",
        "interlayer_scale",
        "orbital_splitting_shift",
        "hybridization_scale",
    ]
    assert tb_contract["coordinates"]["mu_shift"] == {"min": -0.35, "max": 0.35, "center": 0.0}
    assert tb_contract["coordinates"]["bandwidth_scale"] == {"min": -0.20, "max": 0.20, "center": 0.0}
    assert tb_contract["coordinates"]["interlayer_scale"] == {"min": -0.25, "max": 0.25, "center": 0.0}
    assert tb_contract["coordinates"]["orbital_splitting_shift"] == {"min": -0.30, "max": 0.30, "center": 0.0}
    assert tb_contract["coordinates"]["hybridization_scale"] == {"min": -0.25, "max": 0.25, "center": 0.0}
    assert tb_contract["sampling_structure"]["near_baseline_band"]["target_fraction"] == 0.70
    assert tb_contract["sampling_structure"]["near_baseline_band"]["max_abs_coordinate"] == 0.15
    assert tb_contract["sampling_structure"]["edge_probe_band"]["target_fraction"] == 0.30


def test_task14_tb_pilot_contract_forbids_strong_hard_constraints() -> None:
    config = _load_json(TASK14_TB_PILOT_CONFIG_PATH)
    tb_contract = config["tb_pilot_contract"]

    assert tb_contract["allowed_basic_guards"] == [
        "solver_stability",
        "finite_forward_output",
        "schema_validity",
    ]
    assert tb_contract["forbidden_strong_constraints"] == [
        "band_topology_filter",
        "fermi_surface_filter",
        "manual_phase_diagram_gate",
    ]


def test_task14_tb_pilot_doc_records_coordinates_envelope_and_boundary() -> None:
    doc = TASK14_TB_PILOT_DOC_PATH.read_text(encoding="utf-8")

    assert "The canonical Task 14E TB pilot uses exactly these five coordinates" in doc
    assert "- `mu_shift`" in doc
    assert "- `bandwidth_scale`" in doc
    assert "- `interlayer_scale`" in doc
    assert "- `orbital_splitting_shift`" in doc
    assert "- `hybridization_scale`" in doc
    assert "task14_tb_pilot_latent_v1" in doc
    assert 'row["controls"]["tb_pilot_coordinates"]' in doc
    assert "`mu_shift` in `[-0.35, 0.35]`" in doc
    assert "`bandwidth_scale` in `[-0.20, 0.20]`" in doc
    assert "`interlayer_scale` in `[-0.25, 0.25]`" in doc
    assert "`orbital_splitting_shift` in `[-0.30, 0.30]`" in doc
    assert "`hybridization_scale` in `[-0.25, 0.25]`" in doc
    assert "near-baseline band: target `70%` of TB-varied rows" in doc
    assert "edge-probe band: target `30%` of TB-varied rows" in doc
    assert "band-topology filters" in doc
    assert "Fermi-surface hard filters" in doc
    assert "manual phase-diagram gates" in doc
    assert "Task 14E does not generate a dataset and does not launch a server run." in doc
