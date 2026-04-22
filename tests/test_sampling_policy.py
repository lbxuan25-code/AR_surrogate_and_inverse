from __future__ import annotations

from ar_inverse.datasets.sampling import (
    DIRECTIONAL_SMOKE_SAMPLING_POLICY_ID,
    SMOKE_SAMPLING_POLICY_ID,
    deterministic_directional_smoke_samples,
    deterministic_smoke_samples,
    directional_smoke_sampling_policy,
    smoke_sampling_policy,
)
from ar_inverse.datasets.schema import SPLIT_LABELS


def test_smoke_sampling_policy_is_deterministic_and_split_complete() -> None:
    policy = smoke_sampling_policy()
    samples = deterministic_smoke_samples()

    assert policy["sampling_policy_id"] == SMOKE_SAMPLING_POLICY_ID
    assert policy["policy_kind"] == "deterministic_smoke"
    assert tuple(policy["splits"]) == SPLIT_LABELS

    assert len(samples) == 3
    assert tuple(sample.split for sample in samples) == SPLIT_LABELS
    assert tuple(sample.row_id for sample in samples) == (
        "smoke_train_000",
        "smoke_validation_000",
        "smoke_test_000",
    )
    assert all(sample.transport_controls["nk"] == 11 for sample in samples)


def test_directional_smoke_policy_splits_primary_spread_and_diagnostic_regimes() -> None:
    policy = directional_smoke_sampling_policy()
    samples = deterministic_directional_smoke_samples()

    assert policy["sampling_policy_id"] == DIRECTIONAL_SMOKE_SAMPLING_POLICY_ID
    assert policy["direction_regimes"]["primary_supported_regime"]["direction_modes"] == [
        "inplane_100",
        "inplane_110",
    ]
    assert policy["direction_regimes"]["diagnostic_only_regime"]["generic_raw_angles"].startswith("explicit")
    assert policy["direction_regimes"]["unsupported_regime"]["c_axis"].startswith("rejected")

    assert len(samples) == 3
    assert samples[0].direction == {"direction_mode": "inplane_100"}
    assert samples[1].direction == {"direction_mode": "inplane_110"}
    assert samples[2].direction["directional_spread"]["num_samples"] == 3
    assert all("interface_angle" not in sample.transport_controls for sample in samples)
