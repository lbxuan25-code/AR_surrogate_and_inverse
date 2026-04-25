from __future__ import annotations

from pathlib import Path


JOINT_SAMPLING_CONTRACT_PATH = Path("docs/joint_sampling_contract.md")


def test_joint_sampling_contract_makes_nuisance_and_tb_coupling_explicit() -> None:
    doc = JOINT_SAMPLING_CONTRACT_PATH.read_text(encoding="utf-8")

    assert "use explicit structured correlations, not full independence." in doc
    assert "`gamma` and `temperature_kelvin` use positive correlation strata" in doc
    assert "TB variables and nuisance variables must use structured coupling" in doc
    assert "near-baseline TB regimes receive the widest nuisance coverage" in doc
    assert "edge-TB regimes still receive coverage across the nuisance envelope" in doc


def test_joint_sampling_contract_freezes_bias40_density_implications() -> None:
    doc = JOINT_SAMPLING_CONTRACT_PATH.read_text(encoding="utf-8")

    assert "The widened `[-40, 40] meV` / `241`-point bias contract changes where" in doc
    assert "central window: `|bias| <= 6 meV`" in doc
    assert "inner shoulder: `6 < |bias| <= 18 meV`" in doc
    assert "outer shoulder: `18 < |bias| <= 32 meV`" in doc
    assert "edge guard: `32 < |bias| <= 40 meV`" in doc
    assert "high-barrier regimes with low `gamma`" in doc
    assert "pairing anchors or neighborhoods already flagged as high-complexity" in doc


def test_joint_sampling_contract_freezes_piecewise_gamma_density_rule() -> None:
    doc = JOINT_SAMPLING_CONTRACT_PATH.read_text(encoding="utf-8")

    assert "`gamma` uses piecewise density sampling." in doc
    assert "sharp-feature band: `gamma in [0.40, 0.75]`" in doc
    assert "transition band: `gamma in (0.75, 1.20]`" in doc
    assert "broad-feature band: `gamma in (1.20, 1.80]`" in doc
    assert "sharp-feature band: `0.45`" in doc
    assert "transition band: `0.35`" in doc
    assert "broad-feature band: `0.20`" in doc
    assert "piecewise rather than log-weighted in Task S4" in doc
