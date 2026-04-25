from __future__ import annotations

from pathlib import Path


LAYOUT_PATH = Path("docs/repository_layout_v2.md")
NAMING_PATH = Path("docs/naming_convention_v2.md")
MIGRATION_PATH = Path("docs/migration_from_task_named_layout.md")


def test_repository_layout_standard_freezes_content_based_homes() -> None:
    doc = LAYOUT_PATH.read_text(encoding="utf-8")

    assert "The primary organizing key must be content and role, not task number." in doc
    assert "docs/" in doc
    assert "contracts/" in doc
    assert "audits/" in doc
    assert "runbooks/" in doc
    assert "standards/" in doc
    assert "templates/" in doc
    assert "outputs/" in doc
    assert "figures/" in doc
    assert "audits/" in doc
    assert "new contracts go under `docs/contracts/`" in doc
    assert "new figures go under `outputs/figures/`" in doc


def test_naming_convention_v2_prefers_content_and_role_over_task_numbers() -> None:
    doc = NAMING_PATH.read_text(encoding="utf-8")

    assert "file names must describe content and role first." in doc
    assert "<topic>_contract.md" in doc
    assert "<content>_<stage>_dataset.json" in doc
    assert "Task numbers may appear only as compatibility labels" in doc
    assert "legacy" in doc
    assert "archive" in doc
    assert "compatibility alias" in doc
    assert "draft reference" in doc
    assert "task14_pairing_representation_contract.md" in doc
    assert "pairing_representation_contract.md" in doc


def test_migration_plan_freezes_staged_non_destructive_transition() -> None:
    doc = MIGRATION_PATH.read_text(encoding="utf-8")

    assert "Phase 1: Freeze Standards" in doc
    assert "Phase 2: Dual-Path Introduction" in doc
    assert "Phase 3: Alias And Redirect Cleanup" in doc
    assert "Phase 4: Config And Output Harmonization" in doc
    assert "Phase 5: Archive Reduction" in doc
    assert "No large file moves occur in this phase." in doc
    assert "must not:" in doc
    assert "break current lightweight tests without replacement" in doc
    assert "invalidate historical server returned-artifact references" in doc
