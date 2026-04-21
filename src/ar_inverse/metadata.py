"""Forward-interface metadata helpers for local provenance checks."""

from __future__ import annotations

from collections.abc import Mapping

REQUIRED_FORWARD_METADATA_KEYS: tuple[str, ...] = (
    "forward_interface_version",
    "output_schema_version",
    "pairing_convention_id",
    "formal_baseline_record",
    "formal_baseline_selection_rule",
    "projection_config",
    "git_commit",
    "git_dirty",
)


def missing_forward_metadata_keys(metadata: Mapping[str, object]) -> tuple[str, ...]:
    """Return required forward metadata keys that are absent."""

    return tuple(key for key in REQUIRED_FORWARD_METADATA_KEYS if key not in metadata)


def assert_forward_metadata_complete(metadata: Mapping[str, object]) -> None:
    """Raise when emitted forward metadata is incomplete."""

    missing = missing_forward_metadata_keys(metadata)
    if missing:
        formatted = ", ".join(missing)
        raise ValueError(f"Forward metadata is missing required key(s): {formatted}.")
