from __future__ import annotations

import json
from pathlib import Path

from ar_inverse.datasets.schema import PAIRING_AWARE_DATASET_ROW_SCHEMA_VERSION
from ar_inverse.pairing.representation import PAIRING_REPRESENTATION_VERSION


TASK14_DATASET_CONTRACT_PATH = Path("configs/datasets/task14_rmft_anchor_dataset.json")
TASK14_AUDIT_DOC_PATH = Path("docs/task14_rmft_projection_audit.md")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task14_rmft_anchor_dataset_contract_exists_and_freezes_rmft_roles() -> None:
    config = _load_json(TASK14_DATASET_CONTRACT_PATH)

    assert config["config_role"] == "current_task14_rmft_anchor_dataset_contract"
    assert config["execution_mode"] == "local_contract_only_inverse_ready_preparation"
    assert config["dataset_id"] == "task14_rmft_anchor_dataset_v1"
    assert config["sampling_policy_id"] == "task14_rmft_anchor_dataset_v1"
    assert config["audit_metadata_output_path"] == "outputs/runs/task14_rmft_projection_audit.json"
    assert config["allow_diagnostic_raw_angles"] is False
    assert config["frozen_direction_contract"]["unsupported_modes"] == ["c_axis"]

    representation = config["pairing_representation_contract"]
    assert representation["pairing_representation_version"] == PAIRING_REPRESENTATION_VERSION
    assert representation["storage_block"] == "controls.pairing_representation"
    assert representation["row_schema_version"] == PAIRING_AWARE_DATASET_ROW_SCHEMA_VERSION
    assert representation["global_phase_only"] is True
    assert representation["further_compression"] == "forbidden"
    assert representation["channels"] == [
        "delta_zz_s",
        "delta_zz_d",
        "delta_xx_s",
        "delta_xx_d",
        "delta_zx_d",
        "delta_perp_z",
        "delta_perp_x",
        "delta_zx_s",
    ]
    assert representation["required_metadata_keys"] == [
        "pairing_representation_version",
        "gauge_anchor_channel",
        "global_phase_rotation_rad",
        "weak_channel_active",
    ]

    source_contract = config["pairing_source_contract"]
    assert source_contract["canonical_source_kind"] == "rmft_projected_anchor_family"
    assert set(source_contract["sample_roles"]) == {"anchor", "neighborhood", "bridge"}
    assert source_contract["sample_roles"]["anchor"]["priority"] == "primary"
    assert source_contract["sample_roles"]["neighborhood"]["priority"] == "primary"
    assert source_contract["sample_roles"]["bridge"]["priority"] == "secondary"
    assert source_contract["legacy_noncanonical_sources"]["delta_from_baseline_meV"] == (
        "forbidden as the canonical main source"
    )
    assert "symmetry_label" in source_contract["forbidden_training_labels"]
    assert "pca" in source_contract["forbidden_compression"]


def test_task14_rmft_audit_doc_records_required_server_side_review_fields() -> None:
    doc = TASK14_AUDIT_DOC_PATH.read_text(encoding="utf-8")

    assert "outputs/runs/task14_rmft_projection_audit.json" in doc
    assert "projected RMFT anchor points" in doc
    assert "local neighborhoods around projected anchors" in doc
    assert "sparse bridge samples between nearby projected anchors" in doc
    assert "delta_from_baseline_meV" in doc
    assert "controls.pairing_representation" in doc
    assert "ar_inverse_dataset_row_v3" in doc
