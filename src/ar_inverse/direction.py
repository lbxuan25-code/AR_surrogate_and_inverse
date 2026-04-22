"""Local interpretation of the external forward direction contract."""

from __future__ import annotations

import math
from typing import Any

DIRECTION_SCHEMA_VERSION = "ar_inverse_direction_v1"
DIRECTION_PRIOR_SCHEMA_VERSION = "ar_inverse_direction_prior_v1"

SUPPORTED_DIRECTION_MODES: tuple[str, ...] = ("inplane_100", "inplane_110")
UNSUPPORTED_DIRECTION_MODES: tuple[str, ...] = ("c_axis",)
MAX_DIRECTIONAL_SPREAD_HALF_WIDTH = math.pi / 32.0

DIRECTION_PRIOR_KINDS: tuple[str, ...] = (
    "direction_resolved",
    "direction_biased",
    "mixed_or_unknown",
)

REGIME_PRIMARY_SUPPORTED = "primary_supported_named"
REGIME_SECONDARY_SPREAD = "secondary_supported_spread"
REGIME_DIAGNOSTIC_RAW = "diagnostic_raw_angle"


def validate_direction_config(
    direction: dict[str, Any] | None,
    *,
    allow_diagnostic_raw_angles: bool = False,
) -> None:
    """Validate a dataset or candidate direction request before calling forward."""

    if direction is None:
        return
    if not isinstance(direction, dict):
        raise ValueError("Direction config must be a mapping.")

    mode = direction.get("direction_mode")
    interface_angle = direction.get("interface_angle")
    spread = direction.get("directional_spread")

    if mode in UNSUPPORTED_DIRECTION_MODES:
        raise ValueError(
            f"Unsupported direction_mode {mode!r}. The current forward contract supports "
            f"{SUPPORTED_DIRECTION_MODES}; c_axis is not a valid training or inverse target."
        )

    if mode is None:
        if interface_angle is None:
            raise ValueError("Direction config must include direction_mode or diagnostic interface_angle.")
        if not allow_diagnostic_raw_angles:
            raise ValueError(
                "Generic raw interface angles are diagnostic-only. Set "
                "allow_diagnostic_raw_angles=true to generate them separately."
            )
        if spread:
            raise ValueError("Directional spread is only supported around named in-plane modes.")
        return

    if mode not in SUPPORTED_DIRECTION_MODES:
        raise ValueError(
            f"Unsupported direction_mode {mode!r}. Supported named modes are {SUPPORTED_DIRECTION_MODES}."
        )

    if spread is not None:
        validate_directional_spread(spread, expected_mode=str(mode))


def validate_directional_spread(spread: dict[str, Any], *, expected_mode: str | None = None) -> None:
    """Validate the narrow named-mode spread controls accepted by this repository."""

    if not isinstance(spread, dict):
        raise ValueError("directional_spread must be a mapping.")
    mode = str(spread.get("direction_mode", expected_mode or ""))
    if expected_mode is not None and mode not in ("", expected_mode):
        raise ValueError("directional_spread.direction_mode must match direction.direction_mode.")
    if mode and mode not in SUPPORTED_DIRECTION_MODES:
        raise ValueError("Directional spread is only supported for named in-plane modes.")

    half_width = float(spread.get("half_width", 0.0))
    num_samples = int(spread.get("num_samples", 0))
    if half_width <= 0.0:
        raise ValueError("directional_spread.half_width must be positive.")
    if half_width > MAX_DIRECTIONAL_SPREAD_HALF_WIDTH:
        raise ValueError("directional_spread.half_width exceeds the forward contract maximum pi/32.")
    if num_samples < 1:
        raise ValueError("directional_spread.num_samples must be at least 1.")


def normalize_direction_prior(prior: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize and validate the inverse / experiment direction-prior schema."""

    if prior is None:
        return {
            "direction_prior_schema_version": DIRECTION_PRIOR_SCHEMA_VERSION,
            "kind": "mixed_or_unknown",
            "description": "No resolved direction prior was supplied.",
            "allowed_direction_modes": list(SUPPORTED_DIRECTION_MODES),
        }
    if not isinstance(prior, dict):
        raise ValueError("direction_prior must be a mapping.")

    kind = str(prior.get("kind", "mixed_or_unknown"))
    if kind not in DIRECTION_PRIOR_KINDS:
        raise ValueError(f"Unsupported direction prior kind {kind!r}. Expected one of {DIRECTION_PRIOR_KINDS}.")

    allowed_modes = prior.get("allowed_direction_modes", prior.get("direction_modes", SUPPORTED_DIRECTION_MODES))
    allowed = [str(mode) for mode in allowed_modes]
    for mode in allowed:
        validate_direction_config({"direction_mode": mode})

    normalized = dict(prior)
    normalized["direction_prior_schema_version"] = DIRECTION_PRIOR_SCHEMA_VERSION
    normalized["kind"] = kind
    normalized["allowed_direction_modes"] = allowed
    return normalized


def direction_regime_from_block(direction: dict[str, Any] | None) -> str:
    """Return the direction-aware evaluation bucket for a row or candidate."""

    if not isinstance(direction, dict):
        return "legacy_or_unknown_direction"
    spread = direction.get("directional_spread")
    mode = direction.get("direction_mode")
    tier = str(direction.get("direction_support_tier", ""))

    if isinstance(spread, dict) and float(spread.get("half_width", 0.0)) > 0.0:
        return "named_mode_narrow_spread"
    if mode in SUPPORTED_DIRECTION_MODES:
        return f"{mode}_no_spread"
    if tier == "raw_2d_inplane_angle" or mode is None:
        return "diagnostic_raw_angle"
    return "legacy_or_unknown_direction"


def direction_block_from_forward_payload(
    payload: dict[str, Any],
    *,
    configured_direction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extract forward-emitted directional metadata into the local dataset block."""

    request = dict(payload.get("request", {}))
    request_transport = dict(request.get("transport", {}))
    metadata = dict(payload.get("metadata", {}))
    transport_summary = dict(payload.get("transport_summary", {}))

    spread = _normalize_spread(
        transport_summary.get("directional_spread")
        or request.get("directional_spread")
        or metadata.get("directional_spread")
        or (configured_direction or {}).get("directional_spread")
    )
    mode = (
        transport_summary.get("direction_mode")
        or request_transport.get("direction_mode")
        or (configured_direction or {}).get("direction_mode")
    )
    interface_angle = (
        transport_summary.get("interface_angle")
        if "interface_angle" in transport_summary
        else request_transport.get("interface_angle")
    )
    tier = transport_summary.get("direction_support_tier")
    if tier is None:
        tier = "supported_named_inplane" if mode in SUPPORTED_DIRECTION_MODES else "raw_2d_inplane_angle"

    block: dict[str, Any] = {
        "direction_schema_version": DIRECTION_SCHEMA_VERSION,
        "direction_mode": mode,
        "interface_angle": None if interface_angle is None else float(interface_angle),
        "direction_support_tier": tier,
        "direction_crystal_label": transport_summary.get("direction_crystal_label"),
        "direction_dimensionality": transport_summary.get("direction_dimensionality"),
        "direction_is_named_mode": bool(transport_summary.get("direction_is_named_mode", mode in SUPPORTED_DIRECTION_MODES)),
        "directional_spread": spread,
        "forward_direction_provenance": {
            "request_transport": {
                key: request_transport[key]
                for key in ("direction_mode", "interface_angle")
                if key in request_transport
            },
            "transport_summary": {
                key: transport_summary[key]
                for key in (
                    "direction_mode",
                    "interface_angle",
                    "direction_support_tier",
                    "direction_crystal_label",
                    "direction_dimensionality",
                    "direction_is_named_mode",
                    "directional_spread",
                    "directional_spread_samples",
                )
                if key in transport_summary
            },
            "metadata_directional_spread": metadata.get("directional_spread"),
        },
    }
    block["direction_regime"] = direction_regime_from_block(block)
    return block


def _normalize_spread(spread: Any) -> dict[str, Any] | None:
    if spread in (None, False):
        return None
    if not isinstance(spread, dict):
        return None
    normalized = dict(spread)
    if "half_width" in normalized:
        normalized["half_width"] = float(normalized["half_width"])
    if "num_samples" in normalized:
        normalized["num_samples"] = int(normalized["num_samples"])
    return normalized
