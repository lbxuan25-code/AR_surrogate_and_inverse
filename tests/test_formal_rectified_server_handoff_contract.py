from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/formal_rectified_server_handoff.md")


def test_formal_rectified_handoff_promotes_the_pre_s7_config_family() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "Task S9 freezes the first formal post-rectification server handoff." in doc
    assert "`pre_s7_local_observation`" in doc
    assert "older `Task 15A` medium draft" in doc
    assert "docs/runbooks/inverse_ready_medium_draft_runbook.md" in doc
    assert "not the current formal server target" in doc


def test_formal_rectified_handoff_freezes_exact_config_paths_and_commands() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "configs/datasets/local/pre_s7_local_observation_dataset.json" in doc
    assert "configs/surrogate/local/pre_s7_local_observation_training.json" in doc
    assert "configs/surrogate/local/pre_s7_local_observation_evaluation.json" in doc
    assert "python scripts/datasets/build_dataset.py" in doc
    assert "--num-workers 8" in doc
    assert "python scripts/surrogate/train_surrogate.py" in doc
    assert "python scripts/surrogate/evaluate_surrogate.py" in doc
    assert "Do not widen hidden width, add residual blocks, or replace the residual MLP" in doc


def test_formal_rectified_handoff_freezes_returned_artifacts_and_server_resident_outputs() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "Outputs That Must Stay On The Server" in doc
    assert "forward_outputs/" in doc
    assert "Compact Artifacts That Must Return For Review" in doc
    assert "outputs/datasets/pre_s7_local_observation/dataset.json" in doc
    assert "outputs/checkpoints/pre_s7_local_observation/model.pt" in doc
    assert "outputs/runs/pre_s7_local_observation/training_observability/training_history.json" in doc
    assert "outputs/runs/pre_s7_local_observation/evaluation/grouped_error_report.json" in doc
    assert "outputs/runs/pre_s7_local_observation/evaluation/figures/worst_spectrum_comparison.png" in doc
    assert "review gate remains mandatory" in doc
