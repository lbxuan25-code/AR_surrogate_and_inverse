"""Deterministic smoke sampling policies for forward-backed datasets."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

SMOKE_SAMPLING_POLICY_ID = "fit_layer_transport_smoke_v1"
DIRECTIONAL_SMOKE_SAMPLING_POLICY_ID = "directional_fit_layer_transport_smoke_v1"
TASK14_TRANSPORT_DOMAIN_POLICY_ID = "task14_transport_domain_v1"

TASK14_TRANSPORT_TARGET_RANGES: dict[str, tuple[float, float]] = {
    "barrier_z": (0.10, 1.50),
    "gamma": (0.40, 1.80),
    "temperature_kelvin": (1.0, 15.0),
}
TASK14_TRANSPORT_CORE_RANGES: dict[str, tuple[float, float]] = {
    "barrier_z": (0.25, 1.20),
    "gamma": (0.55, 1.55),
    "temperature_kelvin": (1.5, 10.0),
}
TASK14_TRANSPORT_CORE_FRACTION = 0.80
TASK14_TRANSPORT_GUARD_BAND_FRACTION = 0.20
TASK14_TRANSPORT_FIXED_NK = 41


@dataclass(frozen=True, slots=True)
class SmokeSampleSpec:
    """One deterministic fit-layer smoke sample."""

    row_id: str
    split: str
    pairing_controls: dict[str, float]
    transport_controls: dict[str, float | int]
    direction: dict[str, object] | None = None
    group_labels: dict[str, str] = field(default_factory=dict)
    bias_grid: dict[str, float | int] = field(
        default_factory=lambda: {
            "bias_min_mev": -20.0,
            "bias_max_mev": 20.0,
            "num_bias": 41,
        }
    )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def task14_transport_domain_contract() -> dict[str, object]:
    """Return the canonical Task 14 nuisance-domain sampling contract."""

    return {
        "sampling_policy_id": TASK14_TRANSPORT_DOMAIN_POLICY_ID,
        "policy_kind": "continuous_transport_two_tier",
        "description": (
            "Task 14 nuisance-domain contract for inverse-ready datasets. "
            "Sample densely from a central core region and sparsely from a guard-band "
            "region that reaches the full target nuisance envelope."
        ),
        "parameters": ["barrier_z", "gamma", "temperature_kelvin"],
        "target_ranges": {
            key: {"min": bounds[0], "max": bounds[1]} for key, bounds in TASK14_TRANSPORT_TARGET_RANGES.items()
        },
        "two_tier_policy": {
            "core_region": {
                "ranges": {
                    key: {"min": bounds[0], "max": bounds[1]} for key, bounds in TASK14_TRANSPORT_CORE_RANGES.items()
                },
                "target_fraction": TASK14_TRANSPORT_CORE_FRACTION,
                "sampling_density": "dense",
            },
            "guard_band_region": {
                "ranges": {
                    key: {"min": bounds[0], "max": bounds[1]} for key, bounds in TASK14_TRANSPORT_TARGET_RANGES.items()
                },
                "target_fraction": TASK14_TRANSPORT_GUARD_BAND_FRACTION,
                "sampling_density": "sparse",
                "membership_rule": "at least one nuisance coordinate lies outside the dense core region",
            },
        },
        "fixed_nk": TASK14_TRANSPORT_FIXED_NK,
    }


def classify_task14_transport_region(transport_controls: dict[str, float | int]) -> str:
    """Classify transport controls as dense-core or sparse guard-band."""

    values: dict[str, float] = {}
    for key, (minimum, maximum) in TASK14_TRANSPORT_TARGET_RANGES.items():
        if key not in transport_controls:
            raise ValueError(f"Task 14 transport controls are missing required key {key!r}.")
        value = float(transport_controls[key])
        if value < minimum or value > maximum:
            raise ValueError(
                f"Task 14 transport control {key!r}={value} lies outside the canonical range [{minimum}, {maximum}]."
            )
        values[key] = value

    inside_core = all(
        minimum <= values[key] <= maximum for key, (minimum, maximum) in TASK14_TRANSPORT_CORE_RANGES.items()
    )
    return "core" if inside_core else "guard_band"


def smoke_sampling_policy() -> dict[str, object]:
    """Return the documented deterministic policy descriptor."""

    return {
        "sampling_policy_id": SMOKE_SAMPLING_POLICY_ID,
        "policy_kind": "deterministic_smoke",
        "description": "Three fixed fit-layer samples for schema and metadata validation.",
        "fit_layer_pairing_controls": {
            "mode": "delta_from_baseline_meV",
            "channels": [
                "delta_zz_s",
                "delta_xx_s",
                "delta_zx_d",
                "delta_perp_z",
                "delta_perp_x",
            ],
            "weak_delta_zx_s": "closed",
        },
        "transport_controls": {
            "interface_angle": "fixed small set in radians",
            "barrier_z": "fixed smoke values",
            "gamma": "fixed positive broadening in meV",
            "temperature_kelvin": "fixed non-negative smoke values",
            "nk": "small odd grid for fast smoke checks",
        },
        "splits": ["train", "validation", "test"],
    }


def directional_smoke_sampling_policy() -> dict[str, object]:
    """Return the Task 8 direction-aware smoke policy descriptor."""

    return {
        "sampling_policy_id": DIRECTIONAL_SMOKE_SAMPLING_POLICY_ID,
        "policy_kind": "directional_contract_smoke",
        "description": "Three smoke samples covering supported named modes and narrow spread.",
        "direction_regimes": {
            "primary_supported_regime": {
                "direction_modes": ["inplane_100", "inplane_110"],
                "directional_spread": None,
                "generic_raw_angles": "excluded",
            },
            "secondary_supported_regime": {
                "direction_modes": ["inplane_100", "inplane_110"],
                "directional_spread": "narrow named-mode-centered, half_width <= pi/32",
            },
            "diagnostic_only_regime": {
                "generic_raw_angles": "explicit opt-in only; excluded from primary training",
            },
            "unsupported_regime": {
                "c_axis": "rejected at config validation time",
            },
        },
        "fit_layer_pairing_controls": smoke_sampling_policy()["fit_layer_pairing_controls"],
        "transport_controls": {
            "barrier_z": "fixed smoke values",
            "gamma": "fixed positive broadening in meV",
            "temperature_kelvin": "fixed non-negative smoke values",
            "nk": "small odd grid for fast smoke checks",
        },
        "splits": ["train", "validation", "test"],
    }


def deterministic_smoke_samples() -> tuple[SmokeSampleSpec, ...]:
    """Return a stable tiny sample set, not a general sampling engine."""

    return (
        SmokeSampleSpec(
            row_id="smoke_train_000",
            split="train",
            pairing_controls={"delta_zz_s": 0.20, "delta_perp_x": -0.10},
            transport_controls={
                "interface_angle": 0.0,
                "barrier_z": 0.45,
                "gamma": 1.0,
                "temperature_kelvin": 3.0,
                "nk": 11,
            },
        ),
        SmokeSampleSpec(
            row_id="smoke_validation_000",
            split="validation",
            pairing_controls={"delta_xx_s": -0.15, "delta_zx_d": 0.12},
            transport_controls={
                "interface_angle": 0.15,
                "barrier_z": 0.60,
                "gamma": 1.2,
                "temperature_kelvin": 4.0,
                "nk": 11,
            },
        ),
        SmokeSampleSpec(
            row_id="smoke_test_000",
            split="test",
            pairing_controls={"delta_perp_z": 0.10, "delta_perp_x": 0.05},
            transport_controls={
                "interface_angle": -0.10,
                "barrier_z": 0.75,
                "gamma": 0.9,
                "temperature_kelvin": 2.5,
                "nk": 11,
            },
        ),
    )


def deterministic_directional_smoke_samples() -> tuple[SmokeSampleSpec, ...]:
    """Return a tiny Task 8 sample set exercising supported direction regimes."""

    return (
        SmokeSampleSpec(
            row_id="task8_direction_train_inplane_100",
            split="train",
            pairing_controls={"delta_zz_s": 0.18, "delta_perp_x": -0.08},
            transport_controls={
                "barrier_z": 0.50,
                "gamma": 1.0,
                "temperature_kelvin": 3.0,
                "nk": 11,
            },
            direction={"direction_mode": "inplane_100"},
        ),
        SmokeSampleSpec(
            row_id="task8_direction_validation_inplane_110",
            split="validation",
            pairing_controls={"delta_xx_s": -0.12, "delta_zx_d": 0.10},
            transport_controls={
                "barrier_z": 0.65,
                "gamma": 1.1,
                "temperature_kelvin": 3.5,
                "nk": 11,
            },
            direction={"direction_mode": "inplane_110"},
        ),
        SmokeSampleSpec(
            row_id="task8_direction_test_inplane_110_spread",
            split="test",
            pairing_controls={"delta_perp_z": 0.08, "delta_perp_x": 0.04},
            transport_controls={
                "barrier_z": 0.80,
                "gamma": 0.95,
                "temperature_kelvin": 2.5,
                "nk": 11,
            },
            direction={
                "direction_mode": "inplane_110",
                "directional_spread": {
                    "direction_mode": "inplane_110",
                    "half_width": 0.02454369260617026,
                    "num_samples": 3,
                },
            },
        ),
    )
