"""Deterministic smoke sampling policy for Task 2."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

SMOKE_SAMPLING_POLICY_ID = "fit_layer_transport_smoke_v1"


@dataclass(frozen=True, slots=True)
class SmokeSampleSpec:
    """One deterministic fit-layer smoke sample."""

    row_id: str
    split: str
    pairing_controls: dict[str, float]
    transport_controls: dict[str, float | int]
    bias_grid: dict[str, float | int] = field(
        default_factory=lambda: {
            "bias_min_mev": -20.0,
            "bias_max_mev": 20.0,
            "num_bias": 41,
        }
    )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


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
