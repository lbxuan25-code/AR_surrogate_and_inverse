from __future__ import annotations

from ar_inverse.datasets.sampling import (
    SMOKE_SAMPLING_POLICY_ID,
    deterministic_smoke_samples,
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
