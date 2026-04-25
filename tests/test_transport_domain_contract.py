from __future__ import annotations

from pathlib import Path

from ar_inverse.datasets.sampling import (
    TASK14_TRANSPORT_CORE_FRACTION,
    TASK14_TRANSPORT_CORE_RANGES,
    TASK14_TRANSPORT_DOMAIN_POLICY_ID,
    TASK14_TRANSPORT_FIXED_NK,
    TASK14_TRANSPORT_GUARD_BAND_FRACTION,
    TASK14_TRANSPORT_TARGET_RANGES,
    classify_task14_transport_region,
    task14_transport_domain_contract,
)


TASK14_TRANSPORT_DOC_PATH = Path("docs/contracts/transport_domain_contract.md")


def test_task14_transport_domain_contract_freezes_ranges_and_two_tier_split() -> None:
    contract = task14_transport_domain_contract()

    assert contract["sampling_policy_id"] == TASK14_TRANSPORT_DOMAIN_POLICY_ID
    assert contract["policy_kind"] == "continuous_transport_two_tier"
    assert contract["parameters"] == ["barrier_z", "gamma", "temperature_kelvin"]
    assert contract["target_ranges"] == {
        key: {"min": bounds[0], "max": bounds[1]} for key, bounds in TASK14_TRANSPORT_TARGET_RANGES.items()
    }
    assert contract["two_tier_policy"]["core_region"]["ranges"] == {
        key: {"min": bounds[0], "max": bounds[1]} for key, bounds in TASK14_TRANSPORT_CORE_RANGES.items()
    }
    assert contract["two_tier_policy"]["core_region"]["target_fraction"] == TASK14_TRANSPORT_CORE_FRACTION
    assert contract["two_tier_policy"]["guard_band_region"]["target_fraction"] == TASK14_TRANSPORT_GUARD_BAND_FRACTION
    assert contract["two_tier_policy"]["guard_band_region"]["membership_rule"].startswith("at least one")
    assert contract["fixed_nk"] == TASK14_TRANSPORT_FIXED_NK


def test_task14_transport_region_classifier_distinguishes_core_and_guard_band() -> None:
    assert (
        classify_task14_transport_region(
            {"barrier_z": 0.70, "gamma": 1.10, "temperature_kelvin": 5.0, "nk": TASK14_TRANSPORT_FIXED_NK}
        )
        == "core"
    )
    assert (
        classify_task14_transport_region(
            {"barrier_z": 0.12, "gamma": 1.10, "temperature_kelvin": 5.0, "nk": TASK14_TRANSPORT_FIXED_NK}
        )
        == "guard_band"
    )


def test_task14_transport_doc_records_exact_ranges_and_sampling_split() -> None:
    doc = TASK14_TRANSPORT_DOC_PATH.read_text(encoding="utf-8")

    assert "barrier_z` in `[0.10, 1.50]`" in doc
    assert "gamma` in `[0.40, 1.80]`" in doc
    assert "temperature_kelvin` in `[1.0, 15.0]`" in doc
    assert "dense core region: target `80%` of rows" in doc
    assert "sparse guard-band region: target `20%` of rows" in doc
    assert "barrier_z` in `[0.25, 1.20]`" in doc
    assert "gamma` in `[0.55, 1.55]`" in doc
    assert "temperature_kelvin` in `[1.5, 10.0]`" in doc
    assert "task14_transport_domain_contract" in doc
    assert "classify_task14_transport_region" in doc
    assert "task14_transport_domain_v1" in doc
    assert "nk = 41" in doc
