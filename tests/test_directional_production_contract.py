from __future__ import annotations

import json
import math
from pathlib import Path


TASK11_DATASET_CONFIG_PATH = Path("configs/datasets/task11_directional_production_dataset.json")
TASK11_TRAINING_CONFIG_PATH = Path("configs/surrogate/task11_directional_surrogate_production.json")
TASK11_EVALUATION_CONFIG_PATH = Path("configs/surrogate/task11_directional_evaluation_production.json")
TASK11_RUNBOOK_PATH = Path("docs/runbooks/directional_production_runbook.md")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task11_production_dataset_config_documents_frozen_contract() -> None:
    config = _load_json(TASK11_DATASET_CONFIG_PATH)

    assert config["config_role"] == "current_directional_contract_production_entry"
    assert config["execution_mode"] == "server_only_production_contract"
    assert config["allow_diagnostic_raw_angles"] is False
    assert config["frozen_direction_contract"]["unsupported_modes"] == ["c_axis"]
    assert config["frozen_forward_metadata_family"]["git_commit"] == "b85a5cb304acbfd5d51133251ef57293bd0abd2b"
    assert config["frozen_forward_metadata_family"]["git_dirty"] is False

    samples = config["samples"]
    assert len(samples) == 20
    assert {sample["split"] for sample in samples} == {"train", "validation", "test"}

    seen_modes: set[str] = set()
    seen_spread_modes: set[str] = set()
    for sample in samples:
        transport = sample["transport_controls"]
        assert {"barrier_z", "gamma", "temperature_kelvin", "nk"} <= set(transport)

        direction = sample["direction"]
        mode = direction["direction_mode"]
        assert mode in {"inplane_100", "inplane_110"}
        assert "interface_angle" not in direction
        seen_modes.add(mode)

        spread = direction.get("directional_spread")
        if spread:
            assert spread["direction_mode"] == mode
            assert 0.0 < spread["half_width"] <= math.pi / 32.0
            assert spread["num_samples"] >= 1
            seen_spread_modes.add(mode)

    assert seen_modes == {"inplane_100", "inplane_110"}
    assert seen_spread_modes == {"inplane_100", "inplane_110"}


def test_task11_training_and_evaluation_configs_reference_canonical_paths() -> None:
    training_config = _load_json(TASK11_TRAINING_CONFIG_PATH)
    evaluation_config = _load_json(TASK11_EVALUATION_CONFIG_PATH)

    for config in (training_config, evaluation_config):
        assert config["execution_mode"] == "server_only_production_contract"
        assert config["frozen_direction_contract"]["unsupported_modes"] == ["c_axis"]
        assert config["frozen_forward_metadata_family"]["git_commit"] == "b85a5cb304acbfd5d51133251ef57293bd0abd2b"
        assert config["frozen_forward_metadata_family"]["git_dirty"] is False

    assert training_config["dataset_manifest"] == "outputs/datasets/task11_directional_production/dataset.json"
    assert training_config["checkpoint_dir"] == "outputs/checkpoints/task11_directional_surrogate_production"
    assert training_config["run_kind"] == "task11_directional_surrogate_production_training"

    assert evaluation_config["dataset_manifest"] == training_config["dataset_manifest"]
    assert evaluation_config["checkpoint"] == "outputs/checkpoints/task11_directional_surrogate_production/model.npz"
    assert evaluation_config["report_dir"] == "outputs/runs/task11_directional_evaluation_production"
    assert evaluation_config["run_kind"] == "task11_directional_evaluation_production"
    assert evaluation_config["held_out_splits"] == ["validation", "test"]


def test_task11_runbook_records_commands_and_frozen_family() -> None:
    runbook = TASK11_RUNBOOK_PATH.read_text(encoding="utf-8")

    assert "Task 11A prepares the first production server contract only." in runbook
    assert "Task 11B is the actual production server run." in runbook
    assert "git_commit`: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`" in runbook
    assert "python scripts/datasets/build_dataset.py --config configs/datasets/task11_directional_production_dataset.json" in runbook
    assert "python scripts/surrogate/train_surrogate.py --config configs/surrogate/task11_directional_surrogate_production.json" in runbook
    assert (
        "python scripts/surrogate/evaluate_surrogate.py --config "
        "configs/surrogate/task11_directional_evaluation_production.json"
    ) in runbook
    assert "outputs/runs/task11_production_server_run_note.md" in runbook
    assert "compact dataset family metadata proving the frozen forward metadata family was used" in runbook
