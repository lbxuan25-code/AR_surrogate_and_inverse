"""Canonical gauge-fixed 7+1 pairing representation helpers."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

PAIRING_REPRESENTATION_VERSION = "projected_7plus1_gauge_fixed_v1"

CANONICAL_PAIRING_CHANNEL_ORDER: tuple[str, ...] = (
    "delta_zz_s",
    "delta_zz_d",
    "delta_xx_s",
    "delta_xx_d",
    "delta_zx_d",
    "delta_perp_z",
    "delta_perp_x",
    "delta_zx_s",
)

# Keep the anchor priority aligned with the existing projected-pairing contract.
CANONICAL_GAUGE_ANCHOR_PRIORITY: tuple[str, ...] = CANONICAL_PAIRING_CHANNEL_ORDER
DEFAULT_GAUGE_MIN_ANCHOR_ABS = 1.0e-10
WEAK_CHANNEL_NAME = "delta_zx_s"


def _coerce_complex_value(value: Any, *, channel_name: str) -> complex:
    if isinstance(value, Mapping):
        keys = set(value.keys())
        if keys != {"re", "im"}:
            raise ValueError(
                f"Pairing channel {channel_name!r} must use exactly re/im keys when serialized."
            )
        return complex(float(value["re"]), float(value["im"]))
    return complex(value)


def _normalize_channel_mapping(pairing_channels: Mapping[str, Any]) -> dict[str, complex]:
    missing = [name for name in CANONICAL_PAIRING_CHANNEL_ORDER if name not in pairing_channels]
    extra = sorted(set(pairing_channels) - set(CANONICAL_PAIRING_CHANNEL_ORDER))
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append(f"missing channel(s): {', '.join(missing)}")
        if extra:
            details.append(f"unexpected channel(s): {', '.join(extra)}")
        raise ValueError(
            "Pairing representation must contain the full projected 7+1 channels; "
            + "; ".join(details)
            + "."
        )
    return {
        name: _coerce_complex_value(pairing_channels[name], channel_name=name)
        for name in CANONICAL_PAIRING_CHANNEL_ORDER
    }


def gauge_fix_pairing_channels(
    pairing_channels: Mapping[str, Any],
    *,
    anchor_priority: Sequence[str] = CANONICAL_GAUGE_ANCHOR_PRIORITY,
    min_anchor_abs: float = DEFAULT_GAUGE_MIN_ANCHOR_ABS,
) -> dict[str, Any]:
    """Gauge-fix one projected 7+1 pairing sample by removing only global phase."""

    normalized = _normalize_channel_mapping(pairing_channels)
    priority = tuple(str(name) for name in anchor_priority)
    unknown_priority = [name for name in priority if name not in normalized]
    if unknown_priority:
        raise ValueError(f"Gauge anchor priority contains unknown channel(s): {', '.join(unknown_priority)}.")
    if min_anchor_abs < 0.0:
        raise ValueError("min_anchor_abs must be non-negative.")

    gauge_anchor_channel: str | None = None
    for channel_name in priority:
        if abs(normalized[channel_name]) > min_anchor_abs:
            gauge_anchor_channel = channel_name
            break

    global_phase_rotation_rad = 0.0
    rotation_factor = 1.0 + 0.0j
    if gauge_anchor_channel is not None:
        global_phase_rotation_rad = -float(math.atan2(
            normalized[gauge_anchor_channel].imag,
            normalized[gauge_anchor_channel].real,
        ))
        rotation_factor = complex(
            math.cos(global_phase_rotation_rad),
            math.sin(global_phase_rotation_rad),
        )

    gauge_fixed_channels = {
        name: normalized[name] * rotation_factor for name in CANONICAL_PAIRING_CHANNEL_ORDER
    }
    if gauge_anchor_channel is not None:
        anchor_value = gauge_fixed_channels[gauge_anchor_channel]
        gauge_fixed_channels[gauge_anchor_channel] = complex(abs(anchor_value), 0.0)

    return {
        "pairing_representation_version": PAIRING_REPRESENTATION_VERSION,
        "gauge_anchor_channel": gauge_anchor_channel,
        "global_phase_rotation_rad": global_phase_rotation_rad,
        "weak_channel_active": abs(normalized[WEAK_CHANNEL_NAME]) > min_anchor_abs,
        "channels": gauge_fixed_channels,
    }


def serialize_gauge_fixed_pairing_channels(
    gauge_fixed_channels: Mapping[str, Any],
    *,
    gauge_anchor_channel: str | None,
    global_phase_rotation_rad: float,
    weak_channel_active: bool,
) -> dict[str, Any]:
    """Serialize gauge-fixed channels plus metadata into manifest-friendly JSON."""

    normalized = _normalize_channel_mapping(gauge_fixed_channels)
    if gauge_anchor_channel is not None and gauge_anchor_channel not in normalized:
        raise ValueError(f"Unknown gauge_anchor_channel {gauge_anchor_channel!r}.")

    payload = {
        "pairing_representation_version": PAIRING_REPRESENTATION_VERSION,
        "gauge_anchor_channel": gauge_anchor_channel,
        "global_phase_rotation_rad": float(global_phase_rotation_rad),
        "weak_channel_active": bool(weak_channel_active),
        "channels": {
            name: {
                "re": float(normalized[name].real),
                "im": float(normalized[name].imag),
            }
            for name in CANONICAL_PAIRING_CHANNEL_ORDER
        },
    }
    validate_serialized_gauge_fixed_pairing_channels(payload)
    return payload


def deserialize_gauge_fixed_pairing_channels(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Deserialize a manifest-friendly pairing-representation payload."""

    validate_serialized_gauge_fixed_pairing_channels(payload)
    channels = {
        name: complex(
            float(payload["channels"][name]["re"]),
            float(payload["channels"][name]["im"]),
        )
        for name in CANONICAL_PAIRING_CHANNEL_ORDER
    }
    return {
        "pairing_representation_version": str(payload["pairing_representation_version"]),
        "gauge_anchor_channel": payload["gauge_anchor_channel"],
        "global_phase_rotation_rad": float(payload["global_phase_rotation_rad"]),
        "weak_channel_active": bool(payload["weak_channel_active"]),
        "channels": channels,
    }


def validate_serialized_gauge_fixed_pairing_channels(payload: Mapping[str, Any]) -> None:
    """Validate the canonical serialized projected 7+1 pairing payload."""

    if not isinstance(payload, Mapping):
        raise ValueError("Pairing representation payload must be a mapping.")

    required = (
        "pairing_representation_version",
        "gauge_anchor_channel",
        "global_phase_rotation_rad",
        "weak_channel_active",
        "channels",
    )
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"Pairing representation payload is missing key(s): {', '.join(missing)}.")

    if str(payload["pairing_representation_version"]) != PAIRING_REPRESENTATION_VERSION:
        raise ValueError("Unsupported pairing_representation_version.")

    gauge_anchor_channel = payload["gauge_anchor_channel"]
    if gauge_anchor_channel is not None and gauge_anchor_channel not in CANONICAL_PAIRING_CHANNEL_ORDER:
        raise ValueError(f"Unsupported gauge_anchor_channel {gauge_anchor_channel!r}.")

    try:
        float(payload["global_phase_rotation_rad"])
    except (TypeError, ValueError) as exc:
        raise ValueError("global_phase_rotation_rad must be numeric.") from exc

    if not isinstance(payload["weak_channel_active"], bool):
        raise ValueError("weak_channel_active must be a bool.")

    channels = payload["channels"]
    if not isinstance(channels, Mapping):
        raise ValueError("Pairing representation channels must be a mapping.")

    _normalize_channel_mapping(channels)
