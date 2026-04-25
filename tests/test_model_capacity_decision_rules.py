from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/model_capacity_decision_rules.md")


def test_model_capacity_rules_record_the_current_no_expand_conclusion() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "现阶段无充分证据支持立即扩模，当前先维持架构不变。" in doc
    assert "insufficient evidence to justify an immediate capacity" in doc
    assert "increase, so the architecture remains unchanged for now" in doc
    assert "The current residual architecture is retained unchanged." in doc
    assert "widening the hidden width now" in doc
    assert "adding more residual blocks now" in doc


def test_model_capacity_rules_cite_the_pre_s7_local_observation_run() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "configs/surrogate/local/pre_s7_local_observation_training.json" in doc
    assert "outputs/checkpoints/pre_s7_local_observation/metrics.json" in doc
    assert "outputs/runs/pre_s7_local_observation/training_observability/" in doc
    assert "outputs/runs/pre_s7_local_observation/evaluation/evaluation_report.json" in doc
    assert "outputs/runs/pre_s7_local_observation/evaluation/grouped_error_report.json" in doc
    assert "best_validation_loss = 0.007727396208792925" in doc
    assert "mean_rmse = 0.012935445347415064" in doc
    assert "unsafe_fraction = 0.0" in doc


def test_model_capacity_rules_only_allow_later_capacity_changes_under_explicit_conditions() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "Widening may be considered later only if later observations show clear" in doc
    assert "underfitting, meaning all of the following are true together" in doc
    assert "Adding residual blocks may be considered later only if later observations show" in doc
    assert "persistent regime-specific structural failure" in doc
    assert "Optimization instability is a gating warning" in doc
    assert "not an automatic instruction to" in doc
    assert "expand the model immediately" in doc
    assert "the first action is to diagnose optimization" in doc
    assert "not to" in doc
    assert "silently widen or deepen the model by intuition" in doc
    assert "The architecture must stay unchanged when the latest accepted observations" in doc
    assert "look" in doc
    assert "pre-S7 run" in doc
