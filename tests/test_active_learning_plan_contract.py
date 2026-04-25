from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/active_learning_plan.md")


def test_active_learning_plan_freezes_the_initial_stage_and_trigger() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "Task S8 freezes the active-learning roadmap" in doc
    assert "This task does not execute active learning." in doc
    assert "## Initial Training Stage" in doc
    assert "start from a committed dataset contract and committed training config" in doc
    assert "emit the full observability artifact set from Task S5" in doc
    assert "## Uncertainty / Difficulty Trigger" in doc
    assert "uncertainty trigger" in doc
    assert "grouped-regime trigger" in doc
    assert "representative-spectrum trigger" in doc


def test_active_learning_plan_freezes_forward_relabel_and_merge_back_rules() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "## Forward Relabel Path" in doc
    assert "external forward truth chain" in doc
    assert "produce a compact candidate-selection artifact" in doc
    assert "run the true forward labeling on the server" in doc
    assert "The active-learning loop must never fabricate true labels" in doc
    assert "inside this" in doc
    assert "repository." in doc
    assert "## Merge-Back Rule" in doc
    assert "new dataset version or explicit" in doc
    assert "dataset-family extension" in doc
    assert "Rows generated under incompatible forward metadata or direction contracts" in doc
    assert "must" in doc
    assert "remain a distinct dataset family" in doc


def test_active_learning_plan_freezes_required_returned_compact_artifacts() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "## Required Returned Compact Artifacts" in doc
    assert "`difficulty_trigger_report.json`" in doc
    assert "`forward_relabel_round_metadata.json`" in doc
    assert "`dataset_merge_report.json`" in doc
    assert "`training_round_metrics.json`" in doc
    assert "`training_round_observability_manifest.json`" in doc
    assert "`round_comparison_report.json`" in doc
    assert "the difficulty trigger was explicit" in doc
    assert "the retrained surrogate emitted full observability artifacts" in doc
