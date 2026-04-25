from __future__ import annotations

from ar_inverse.datasets.sampling_v2 import (
    BridgeCandidateSummary,
    CONTINUOUS_SUBSPACE_SAMPLER_ID,
    SAMPLING_POLICY_V2_ID,
    SpectralComplexityInputs,
    compute_spectral_complexity_score,
    continuous_subspace_sampler_spec,
    neighborhood_sample_count,
    sampling_policy_v2,
    should_increase_neighborhood_density,
    should_trigger_bridge,
)


def test_sampling_policy_v2_freezes_quality_first_rules_and_not_fixed_row_counts() -> None:
    policy = sampling_policy_v2()

    assert policy["sampling_policy_id"] == SAMPLING_POLICY_V2_ID
    assert policy["policy_kind"] == "quality_first_rmft_sampling"
    assert policy["row_budget_priority"] == "deferred_until_quality_gates_pass"
    assert policy["fixed_row_count_status"] == "not a first-class design input"
    assert policy["first_design_inputs"] == [
        "anchor coverage",
        "neighborhood density",
        "bridge triggers",
        "continuous-subspace sampler choice",
        "spectral-complexity-driven densification",
    ]
    assert policy["anchor_coverage"]["coverage_goal"] == "cover_every_accepted_rmft_anchor_family_before_budget_rebalancing"


def test_sampling_policy_v2_freezes_scrambled_sobol_and_density_increase_rule() -> None:
    sampler = continuous_subspace_sampler_spec()

    assert sampler["sampler_id"] == CONTINUOUS_SUBSPACE_SAMPLER_ID
    assert sampler["sampler_kind"] == "scrambled_sobol"
    assert sampler["scramble"] == "owen"
    assert sampler["batch_rule"] == "power_of_two_prefixes"

    simple_score = compute_spectral_complexity_score(
        SpectralComplexityInputs(
            prominent_extrema_count=1,
            zero_bias_curvature_abs=0.15,
            mean_abs_first_difference=0.01,
            disagreement_proxy=0.005,
        )
    )
    complex_score = compute_spectral_complexity_score(
        SpectralComplexityInputs(
            prominent_extrema_count=6,
            zero_bias_curvature_abs=1.8,
            mean_abs_first_difference=0.11,
            disagreement_proxy=0.06,
        )
    )

    assert 0.0 <= simple_score < 0.58
    assert complex_score >= 0.58
    assert should_increase_neighborhood_density(
        local_radius_fraction=0.30,
        spectral_complexity_score=simple_score,
        physically_sensitive_region=False,
    ) is False
    assert should_increase_neighborhood_density(
        local_radius_fraction=0.30,
        spectral_complexity_score=complex_score,
        physically_sensitive_region=False,
    ) is True
    assert neighborhood_sample_count(
        local_radius_fraction=0.30,
        spectral_complexity_score=simple_score,
        physically_sensitive_region=False,
    ) == 6
    assert neighborhood_sample_count(
        local_radius_fraction=0.30,
        spectral_complexity_score=complex_score,
        physically_sensitive_region=False,
    ) == 12


def test_sampling_policy_v2_triggers_bridges_only_for_eligible_pairs() -> None:
    assert should_trigger_bridge(
        BridgeCandidateSummary(
            normalized_anchor_distance=0.30,
            complexity_gap=0.24,
        )
    ) is True
    assert should_trigger_bridge(
        BridgeCandidateSummary(
            normalized_anchor_distance=0.30,
            complexity_gap=0.05,
            weak_channel_flip=True,
        )
    ) is True
    assert should_trigger_bridge(
        BridgeCandidateSummary(
            normalized_anchor_distance=0.10,
            complexity_gap=0.30,
        )
    ) is False
    assert should_trigger_bridge(
        BridgeCandidateSummary(
            normalized_anchor_distance=0.40,
            complexity_gap=0.05,
            weak_channel_flip=False,
            phase_regime_change=False,
        )
    ) is False
