"""Canonical dataset schema helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from ar_inverse.metadata import assert_forward_metadata_complete, missing_forward_metadata_keys

DATASET_ROW_SCHEMA_VERSION = "ar_inverse_dataset_row_v1"
DATASET_MANIFEST_SCHEMA_VERSION = "ar_inverse_dataset_manifest_v1"
RESUMABLE_MANIFEST_SCHEMA_VERSION = "ar_inverse_resumable_manifest_v1"

SPLIT_LABELS: tuple[str, ...] = ("train", "validation", "test")
RESUMABLE_ROW_STATUSES: tuple[str, ...] = ("pending", "completed", "failed")

REQUIRED_DATASET_ROW_KEYS: tuple[str, ...] = (
    "dataset_row_schema_version",
    "row_id",
    "sampling_policy_id",
    "split",
    "forward_request",
    "forward_output_ref",
    "forward_metadata",
)

REQUIRED_FORWARD_OUTPUT_REF_KEYS: tuple[str, ...] = (
    "storage",
    "path",
    "sha256",
    "payload_kind",
)

REQUIRED_PLAN_ENTRY_KEYS: tuple[str, ...] = (
    "row_id",
    "split",
    "sampling_policy_id",
    "status",
)


def file_sha256(path: Path | str) -> str:
    """Return the SHA-256 digest for a local artifact."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def forward_output_ref(path: Path | str, *, base_dir: Path | str | None = None) -> dict[str, str]:
    """Build a local forward-output reference for a dataset row."""

    output_path = Path(path)
    reference_path = output_path
    if base_dir is not None:
        reference_path = output_path.relative_to(Path(base_dir))
    return {
        "storage": "local_json",
        "path": reference_path.as_posix(),
        "sha256": file_sha256(output_path),
        "payload_kind": "forward_spectrum",
    }


def make_dataset_row(
    *,
    row_id: str,
    sampling_policy_id: str,
    split: str,
    forward_request: dict[str, object],
    forward_output_ref_payload: dict[str, str],
    forward_metadata: dict[str, object],
    controls: dict[str, object] | None = None,
) -> dict[str, object]:
    """Create and validate a canonical dataset row."""

    row: dict[str, object] = {
        "dataset_row_schema_version": DATASET_ROW_SCHEMA_VERSION,
        "row_id": row_id,
        "sampling_policy_id": sampling_policy_id,
        "split": split,
        "forward_request": forward_request,
        "forward_output_ref": forward_output_ref_payload,
        "forward_metadata": forward_metadata,
    }
    if controls is not None:
        row["controls"] = controls
    validate_dataset_row(row)
    return row


def validate_dataset_row(row: dict[str, Any]) -> None:
    """Validate the Task 2 dataset-row contract."""

    missing = [key for key in REQUIRED_DATASET_ROW_KEYS if key not in row]
    if missing:
        raise ValueError(f"Dataset row is missing required key(s): {', '.join(missing)}.")

    if row["dataset_row_schema_version"] != DATASET_ROW_SCHEMA_VERSION:
        raise ValueError(f"Unsupported dataset row schema version: {row['dataset_row_schema_version']!r}.")

    if row["split"] not in SPLIT_LABELS:
        raise ValueError(f"Unsupported split label: {row['split']!r}. Expected one of {SPLIT_LABELS}.")

    if not isinstance(row["forward_request"], dict):
        raise ValueError("Dataset row forward_request must be a mapping.")

    output_ref = row["forward_output_ref"]
    if not isinstance(output_ref, dict):
        raise ValueError("Dataset row forward_output_ref must be a mapping.")
    missing_ref = [key for key in REQUIRED_FORWARD_OUTPUT_REF_KEYS if key not in output_ref]
    if missing_ref:
        raise ValueError(f"Dataset row forward_output_ref is missing key(s): {', '.join(missing_ref)}.")

    metadata = row["forward_metadata"]
    if not isinstance(metadata, dict):
        raise ValueError("Dataset row forward_metadata must be a mapping.")
    assert_forward_metadata_complete(metadata)


def validate_dataset_manifest(manifest: dict[str, Any]) -> None:
    """Validate a small dataset manifest and every row it contains."""

    if manifest.get("dataset_manifest_schema_version") != DATASET_MANIFEST_SCHEMA_VERSION:
        raise ValueError("Unsupported or missing dataset_manifest_schema_version.")
    rows = manifest.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Dataset manifest must contain a non-empty rows list.")

    row_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Every dataset manifest row must be a mapping.")
        validate_dataset_row(row)
        row_id = str(row["row_id"])
        if row_id in row_ids:
            raise ValueError(f"Duplicate dataset row_id: {row_id}.")
        row_ids.add(row_id)

    missing_by_row = {
        str(row["row_id"]): missing_forward_metadata_keys(row["forward_metadata"]) for row in rows
    }
    incomplete = {row_id: missing for row_id, missing in missing_by_row.items() if missing}
    if incomplete:
        raise ValueError(f"Dataset manifest contains incomplete forward metadata: {incomplete}.")


def validate_resumable_manifest(manifest: dict[str, Any]) -> None:
    """Validate resumable orchestration fields plus completed dataset rows."""

    if manifest.get("resumable_manifest_schema_version") != RESUMABLE_MANIFEST_SCHEMA_VERSION:
        raise ValueError("Unsupported or missing resumable_manifest_schema_version.")

    plan = manifest.get("plan")
    if not isinstance(plan, list) or not plan:
        raise ValueError("Resumable manifest must contain a non-empty plan list.")

    plan_ids: set[str] = set()
    for entry in plan:
        if not isinstance(entry, dict):
            raise ValueError("Every resumable plan entry must be a mapping.")
        missing = [key for key in REQUIRED_PLAN_ENTRY_KEYS if key not in entry]
        if missing:
            raise ValueError(f"Resumable plan entry is missing key(s): {', '.join(missing)}.")
        if entry["split"] not in SPLIT_LABELS:
            raise ValueError(f"Unsupported plan split label: {entry['split']!r}.")
        if entry["status"] not in RESUMABLE_ROW_STATUSES:
            raise ValueError(f"Unsupported plan status: {entry['status']!r}.")

        row_id = str(entry["row_id"])
        if row_id in plan_ids:
            raise ValueError(f"Duplicate resumable plan row_id: {row_id}.")
        plan_ids.add(row_id)

    rows = manifest.get("rows")
    if rows:
        validate_dataset_manifest(manifest)
        row_ids = {str(row["row_id"]) for row in rows}
        unknown = sorted(row_ids - plan_ids)
        if unknown:
            raise ValueError(f"Completed rows are missing from resumable plan: {unknown}.")

    completed_plan_ids = {str(entry["row_id"]) for entry in plan if entry["status"] == "completed"}
    completed_row_ids = {str(row["row_id"]) for row in rows or []}
    missing_rows = sorted(completed_plan_ids - completed_row_ids)
    if missing_rows:
        raise ValueError(f"Completed plan entries are missing dataset rows: {missing_rows}.")
