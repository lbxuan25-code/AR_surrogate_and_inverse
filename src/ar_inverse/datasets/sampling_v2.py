"""Quality-first sampling policy helpers for surrogate rectification."""

from __future__ import annotations

from dataclasses import asdict, dataclass


SAMPLING_POLICY_V2_ID = "quality_first_rmft_sampling_v2"
CONTINUOUS_SUBSPACE_SAMPLER_ID = "scrambled_sobol_v1"


@dataclass(frozen=True, slots=True)
class SpectralComplexityInputs:
    """Compact summary features used by the first densification rule."""

    prominent_extrema_count: int
    zero_bias_curvature_abs: float
    mean_abs_first_difference: float
    disagreement_proxy: float


@dataclass(frozen=True, slots=True)
class BridgeCandidateSummary:
    """Minimal bridge-trigger summary between two nearby anchor families."""

    normalized_anchor_distance: float
    complexity_gap: float
    weak_channel_flip: bool = False
    phase_regime_change: bool = False


def continuous_subspace_sampler_spec() -> dict[str, object]:
    """Return the canonical continuous-subspace sampler contract."""

    return {
        "sampler_id": CONTINUOUS_SUBSPACE_SAMPLER_ID,
        "sampler_kind": "scrambled_sobol",
        "scramble": "owen",
        "batch_rule": "power_of_two_prefixes",
        "deduplication": "deterministic hash-level dedupe before forward execution",
        "why_this_sampler": (
            "Low-discrepancy Sobol coverage is the default continuous-subspace sampler for "
            "pairing-adjacent nuisance coordinates because it gives better early coverage than "
            "unspecified continuous sampling and avoids quota-first thinking."
        ),
    }


def anchor_coverage_policy() -> dict[str, object]:
    """Return the canonical anchor-coverage rule set."""

    return {
        "coverage_goal": "cover_every_accepted_rmft_anchor_family_before_budget_rebalancing",
        "minimum_direct_anchor_replicates": 1,
        "extra_anchor_replicates_for_sensitive_anchors": 1,
        "sensitive_anchor_flags": [
            "weak_channel_active",
            "high_complexity_anchor",
            "phase_turning_anchor",
        ],
        "coverage_gate_before_expansion": (
            "No neighborhood-heavy or bridge-heavy expansion is allowed until every accepted "
            "RMFT anchor family has at least one direct representative."
        ),
    }


def neighborhood_density_policy() -> dict[str, object]:
    """Return the canonical neighborhood-density rule set."""

    return {
        "base_samples_per_anchor": 6,
        "dense_samples_per_anchor": 12,
        "max_samples_per_anchor": 18,
        "local_core_radius_fraction": 0.12,
        "dense_resampling_trigger_score": 0.58,
        "increase_conditions": [
            "spectral_complexity_score >= 0.58",
            "physically_sensitive_region_flag is true",
            "local_radius_fraction <= 0.12",
        ],
        "increase_rule": (
            "Increase neighborhood density whenever any increase condition is met; "
            "apply the dense count and cap at the maximum count."
        ),
    }


def bridge_trigger_policy() -> dict[str, object]:
    """Return the canonical bridge-trigger rule set."""

    return {
        "eligible_distance_window": {
            "min": 0.18,
            "max": 0.65,
        },
        "bridge_trigger_conditions": [
            "weak_channel_flip",
            "phase_regime_change",
            "complexity_gap >= 0.20",
        ],
        "bridge_rule": (
            "Trigger bridge samples only for nearby anchor pairs inside the eligible distance "
            "window when at least one bridge-trigger condition is present."
        ),
        "max_bridge_samples_per_pair": 3,
    }


def compute_spectral_complexity_score(inputs: SpectralComplexityInputs) -> float:
    """Compute the first complexity score used by the densification policy."""

    extrema_term = min(max(inputs.prominent_extrema_count, 0), 6) / 6.0
    curvature_term = min(max(inputs.zero_bias_curvature_abs, 0.0), 2.0) / 2.0
    first_difference_term = min(max(inputs.mean_abs_first_difference, 0.0), 0.12) / 0.12
    disagreement_term = min(max(inputs.disagreement_proxy, 0.0), 0.08) / 0.08
    score = (
        0.35 * extrema_term
        + 0.25 * curvature_term
        + 0.25 * first_difference_term
        + 0.15 * disagreement_term
    )
    return round(score, 4)


def should_increase_neighborhood_density(
    *,
    local_radius_fraction: float,
    spectral_complexity_score: float,
    physically_sensitive_region: bool,
) -> bool:
    """Return whether neighborhood density should be increased."""

    policy = neighborhood_density_policy()
    return (
        spectral_complexity_score >= float(policy["dense_resampling_trigger_score"])
        or physically_sensitive_region
        or local_radius_fraction <= float(policy["local_core_radius_fraction"])
    )


def neighborhood_sample_count(
    *,
    local_radius_fraction: float,
    spectral_complexity_score: float,
    physically_sensitive_region: bool,
) -> int:
    """Return the recommended neighborhood sample count for one anchor."""

    policy = neighborhood_density_policy()
    if should_increase_neighborhood_density(
        local_radius_fraction=local_radius_fraction,
        spectral_complexity_score=spectral_complexity_score,
        physically_sensitive_region=physically_sensitive_region,
    ):
        return int(policy["dense_samples_per_anchor"])
    return int(policy["base_samples_per_anchor"])


def should_trigger_bridge(candidate: BridgeCandidateSummary) -> bool:
    """Return whether a bridge between two anchors should be created."""

    policy = bridge_trigger_policy()
    distance_window = policy["eligible_distance_window"]
    if not float(distance_window["min"]) <= candidate.normalized_anchor_distance <= float(distance_window["max"]):
        return False
    if candidate.weak_channel_flip or candidate.phase_regime_change:
        return True
    return candidate.complexity_gap >= 0.20


def sampling_policy_v2() -> dict[str, object]:
    """Return the frozen S3 quality-first sampling policy descriptor."""

    return {
        "sampling_policy_id": SAMPLING_POLICY_V2_ID,
        "policy_kind": "quality_first_rmft_sampling",
        "row_budget_priority": "deferred_until_quality_gates_pass",
        "first_design_inputs": [
            "anchor coverage",
            "neighborhood density",
            "bridge triggers",
            "continuous-subspace sampler choice",
            "spectral-complexity-driven densification",
        ],
        "budget_freeze_gates": [
            "every accepted RMFT anchor family is covered",
            "neighborhood density rules are fixed and reviewable",
            "bridge-trigger frequency can be estimated from pilot audit statistics",
            "dense-resampling trigger behavior is stable under the chosen sampler",
        ],
        "continuous_subspace_sampler": continuous_subspace_sampler_spec(),
        "anchor_coverage": anchor_coverage_policy(),
        "neighborhood_density": neighborhood_density_policy(),
        "bridge_triggers": bridge_trigger_policy(),
        "spectral_complexity_score": {
            "inputs": list(asdict(SpectralComplexityInputs(0, 0.0, 0.0, 0.0))),
            "score_range": [0.0, 1.0],
            "dense_resampling_trigger_score": neighborhood_density_policy()["dense_resampling_trigger_score"],
        },
        "fixed_row_count_status": "not a first-class design input",
    }
