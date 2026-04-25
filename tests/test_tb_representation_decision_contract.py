from __future__ import annotations

from pathlib import Path


AUDIT_PATH = Path("docs/audits/tb_representation_audit.md")
DECISION_PATH = Path("docs/contracts/tb_parameterization_decision.md")


def test_tb_representation_audit_covers_required_families_and_axes() -> None:
    audit = AUDIT_PATH.read_text(encoding="utf-8")

    assert "original forward-exposed normal-state parameter form" in audit
    assert "physically grouped TB parameter form" in audit
    assert "reduced TB coordinate form" in audit
    assert "physical interpretability" in audit
    assert "forward traceability" in audit
    assert "surrogate input dimensionality" in audit
    assert "sampling difficulty" in audit
    assert "expected degeneracy risk" in audit


def test_tb_representation_audit_demotes_the_current_five_coordinate_pilot() -> None:
    audit = AUDIT_PATH.read_text(encoding="utf-8")

    assert "task14_tb_pilot_latent_v1" in audit
    assert "`mu_shift`" in audit
    assert "`bandwidth_scale`" in audit
    assert "`interlayer_scale`" in audit
    assert "`orbital_splitting_shift`" in audit
    assert "`hybridization_scale`" in audit
    assert "not strong enough to serve as the sole canonical TB" in audit
    assert "representation" in audit
    assert "demoted" in audit
    assert "canonical status" in audit


def test_tb_parameterization_decision_freezes_the_two_level_choice() -> None:
    decision = DECISION_PATH.read_text(encoding="utf-8")

    assert "The repository will use a two-level TB representation." in decision
    assert "original forward-exposed normal-state parameter form" in decision
    assert "physically grouped TB parameter form as the canonical training-facing" in decision
    assert "task14_tb_pilot_latent_v1" in decision
    assert "not retained as the canonical long-term" in decision
    assert "representation" in decision
    assert "do not promote `task14_tb_pilot_latent_v1` into the canonical long-term TB" in decision
