from __future__ import annotations

import math

import pytest

from ar_inverse.datasets.schema import (
    PAIRING_AWARE_DATASET_ROW_SCHEMA_VERSION,
    validate_dataset_row,
)
from ar_inverse.pairing.representation import (
    CANONICAL_PAIRING_CHANNEL_ORDER,
    PAIRING_REPRESENTATION_VERSION,
    deserialize_gauge_fixed_pairing_channels,
    gauge_fix_pairing_channels,
    serialize_gauge_fixed_pairing_channels,
)


def _full_projected_channels() -> dict[str, complex]:
    return {
        "delta_zz_s": 0.0 + 0.0j,
        "delta_zz_d": -1.0 + 1.0j,
        "delta_xx_s": 0.3 - 0.4j,
        "delta_xx_d": 0.0 + 0.0j,
        "delta_zx_d": -0.25 + 0.2j,
        "delta_perp_z": 0.05 + 0.1j,
        "delta_perp_x": -0.07 - 0.03j,
        "delta_zx_s": 0.0 + 0.0j,
    }


def _direction_block() -> dict[str, object]:
    return {
        "direction_schema_version": "ar_inverse_direction_v1",
        "direction_mode": "inplane_100",
        "interface_angle": 0.0,
        "direction_support_tier": "A",
        "direction_regime": "inplane_100_no_spread",
        "directional_spread": None,
        "forward_direction_provenance": {
            "metadata_directional_spread": None,
            "request_transport": {"direction_mode": "inplane_100", "interface_angle": 0.0},
            "transport_summary": {
                "direction_mode": "inplane_100",
                "direction_support_tier": "A",
                "interface_angle": 0.0,
            },
        },
    }


def _forward_metadata() -> dict[str, object]:
    return {
        "forward_interface_version": "ar_forward_v1",
        "output_schema_version": "ar_forward_output_v1",
        "pairing_convention_id": "round2_physical_channels_task_h_fit_layer_v1",
        "formal_baseline_record": "outputs/source/round2_baseline_selection.json",
        "formal_baseline_selection_rule": (
            "temperature sweep RMFT pairing data, charge-balanced p≈0 branch, "
            "temperature_eV <= 1.0e-3, first 8 samples sorted by temperature"
        ),
        "projection_config": {
            "gauge_anchor_priority": list(CANONICAL_PAIRING_CHANNEL_ORDER),
        },
        "git_commit": "b85a5cb304acbfd5d51133251ef57293bd0abd2b",
        "git_dirty": False,
    }


def test_gauge_fix_pairing_channels_rotates_one_global_phase_deterministically() -> None:
    channels = _full_projected_channels()

    result = gauge_fix_pairing_channels(channels)

    assert result["pairing_representation_version"] == PAIRING_REPRESENTATION_VERSION
    assert result["gauge_anchor_channel"] == "delta_zz_d"
    assert result["weak_channel_active"] is False

    rotation = complex(
        math.cos(result["global_phase_rotation_rad"]),
        math.sin(result["global_phase_rotation_rad"]),
    )
    expected = {name: channels[name] * rotation for name in CANONICAL_PAIRING_CHANNEL_ORDER}

    for name in CANONICAL_PAIRING_CHANNEL_ORDER:
        actual = result["channels"][name]
        if name == "delta_zz_d":
            assert actual.imag == pytest.approx(0.0, abs=1.0e-12)
            assert actual.real >= 0.0
            assert actual.real == pytest.approx(abs(channels[name]))
        else:
            assert actual.real == pytest.approx(expected[name].real)
            assert actual.imag == pytest.approx(expected[name].imag)


def test_serialize_and_deserialize_round_trip_preserves_metadata_and_channels() -> None:
    gauge_fixed = gauge_fix_pairing_channels(_full_projected_channels())

    payload = serialize_gauge_fixed_pairing_channels(
        gauge_fixed["channels"],
        gauge_anchor_channel=gauge_fixed["gauge_anchor_channel"],
        global_phase_rotation_rad=gauge_fixed["global_phase_rotation_rad"],
        weak_channel_active=gauge_fixed["weak_channel_active"],
    )
    round_trip = deserialize_gauge_fixed_pairing_channels(payload)

    assert payload["pairing_representation_version"] == PAIRING_REPRESENTATION_VERSION
    assert payload["gauge_anchor_channel"] == "delta_zz_d"
    assert payload["weak_channel_active"] is False
    assert round_trip["gauge_anchor_channel"] == payload["gauge_anchor_channel"]
    assert round_trip["global_phase_rotation_rad"] == pytest.approx(payload["global_phase_rotation_rad"])
    assert round_trip["weak_channel_active"] is False
    for name in CANONICAL_PAIRING_CHANNEL_ORDER:
        assert round_trip["channels"][name] == pytest.approx(gauge_fixed["channels"][name])


def test_all_zero_channels_keep_null_anchor_and_zero_rotation() -> None:
    gauge_fixed = gauge_fix_pairing_channels({name: 0.0 + 0.0j for name in CANONICAL_PAIRING_CHANNEL_ORDER})

    assert gauge_fixed["gauge_anchor_channel"] is None
    assert gauge_fixed["global_phase_rotation_rad"] == pytest.approx(0.0)
    assert gauge_fixed["weak_channel_active"] is False
    assert all(gauge_fixed["channels"][name] == pytest.approx(0.0 + 0.0j) for name in CANONICAL_PAIRING_CHANNEL_ORDER)


def test_dataset_schema_accepts_pairing_representation_block_for_v3_rows() -> None:
    gauge_fixed = gauge_fix_pairing_channels(_full_projected_channels())
    serialized = serialize_gauge_fixed_pairing_channels(
        gauge_fixed["channels"],
        gauge_anchor_channel=gauge_fixed["gauge_anchor_channel"],
        global_phase_rotation_rad=gauge_fixed["global_phase_rotation_rad"],
        weak_channel_active=gauge_fixed["weak_channel_active"],
    )
    row = {
        "dataset_row_schema_version": PAIRING_AWARE_DATASET_ROW_SCHEMA_VERSION,
        "row_id": "task14_pairing_demo_000",
        "sampling_policy_id": "task14_pairing_demo_v1",
        "split": "train",
        "forward_request": {"request_kind": "fit_layer"},
        "forward_output_ref": {
            "storage": "local_json",
            "path": "forward_outputs/demo.json",
            "sha256": "abc123",
            "payload_kind": "forward_spectrum",
        },
        "forward_metadata": _forward_metadata(),
        "direction": _direction_block(),
        "controls": {
            "transport_controls": {"barrier_z": 0.4, "gamma": 1.0, "temperature_kelvin": 3.0, "nk": 41},
            "pairing_representation": serialized,
        },
    }

    validate_dataset_row(row)


def test_serialize_rejects_missing_projected_channel() -> None:
    channels = _full_projected_channels()
    channels.pop("delta_zx_s")

    with pytest.raises(ValueError, match="full projected 7\\+1 channels"):
        gauge_fix_pairing_channels(channels)
