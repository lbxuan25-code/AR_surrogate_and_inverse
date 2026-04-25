from __future__ import annotations

from pathlib import Path


def test_cleanup_creates_content_based_docs_homes_and_removes_old_top_level_task_docs() -> None:
    assert Path("docs/contracts/pairing_representation_contract.md").is_file()
    assert Path("docs/runbooks/directional_pilot_runbook.md").is_file()
    assert Path("docs/standards/training_observability_standard.md").is_file()
    assert Path("docs/archive/legacy_tb_pilot_contract.md").is_file()

    assert not Path("docs/task10_pilot_server_runbook.md").exists()
    assert not Path("docs/task14_pairing_representation_contract.md").exists()
    assert not Path("docs/task14_tb_pilot_contract.md").exists()


def test_cleanup_moves_current_rectification_configs_into_content_based_homes() -> None:
    assert Path("configs/datasets/smoke/directional_smoke_dataset.json").is_file()
    assert Path("configs/datasets/contracts/rmft_anchor_dataset_contract.json").is_file()
    assert Path("configs/datasets/contracts/bias40_probe_dataset_contract.json").is_file()
    assert Path("configs/datasets/drafts/inverse_ready_medium_dataset_draft.json").is_file()
    assert Path("configs/surrogate/smoke/directional_smoke_training.json").is_file()
    assert Path("configs/surrogate/smoke/directional_smoke_evaluation.json").is_file()

    assert not Path("configs/datasets/task8_directional_smoke_dataset.json").exists()
    assert not Path("configs/datasets/task15_inverse_ready_medium_dataset.json").exists()
    assert not Path("configs/surrogate/task9_directional_surrogate_smoke.json").exists()
    assert not Path("configs/surrogate/task15_inverse_ready_medium_training.json").exists()
