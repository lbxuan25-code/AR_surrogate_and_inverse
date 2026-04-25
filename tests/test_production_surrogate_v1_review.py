from __future__ import annotations

import json
from pathlib import Path


REVIEW_PATH = Path("docs/reviews/production_surrogate_v1_review.md")
AUDIT_PATH = Path("outputs/audits/production_surrogate_v1/rmft_source_coverage_audit.json")
FIGURE_PATH = Path("outputs/figures/production_surrogate_v1/luo_rmft_sampling_2d.png")


def test_p3_review_records_primary_decision_and_capacity_non_trigger() -> None:
    review = REVIEW_PATH.read_text(encoding="utf-8")

    assert "Revise sampling implementation / metadata before accepting" in review
    assert "not a model-capacity failure" in review
    assert "S7's \"do not expand without evidence\" rule is not triggered" in review
    assert "Do not widen or deepen the model based on current evidence" in review


def test_p3_audit_records_sampling_mismatch_and_rmft_source_warning() -> None:
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))

    assert audit["coverage_judgment"] == "warning"
    assert audit["original_luo_rmft_source"]["available_in_p2_artifacts"] is False
    assert audit["original_luo_rmft_source"]["total_points"] is None
    assert audit["primary_p3_outcome"] == "revise_sampling_and_metadata_before_acceptance"

    composition = audit["contract_vs_actual_sampling"]
    assert composition["pairing_source_role_matches_contract"] is False
    assert composition["direction_regime_matches_contract"] is False
    assert composition["tb_regime_matches_contract"] is False
    assert composition["pairing_source_role_targets"] == {
        "anchor": 3072,
        "neighborhood": 3072,
        "bridge": 2048,
    }
    assert composition["pairing_source_role_actual"] == {
        "anchor": 2732,
        "neighborhood": 2730,
        "bridge": 2730,
    }


def test_p3_luo_rmft_visualization_artifact_exists() -> None:
    assert FIGURE_PATH.is_file()
    assert FIGURE_PATH.stat().st_size > 0
