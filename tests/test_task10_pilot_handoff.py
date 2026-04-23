from __future__ import annotations

import json
import math
from pathlib import Path


TASK10_DATASET_CONFIG_PATH = Path("configs/datasets/task10_directional_pilot_dataset.json")
TASK10_TRAINING_CONFIG_PATH = Path("configs/surrogate/task10_directional_surrogate_pilot.json")
TASK10_EVALUATION_CONFIG_PATH = Path("configs/surrogate/task10_directional_evaluation_pilot.json")
TASK10_RUNBOOK_PATH = Path("docs/task10_pilot_server_runbook.md")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task10_pilot_dataset_config_uses_only_supported_modes_and_narrow_spread() -> None:
    config = _load_json(TASK10_DATASET_CONFIG_PATH)

    assert config["config_role"] == "current_directional_contract_pilot_entry"
    assert config["execution_mode"] == "server_only_non_smoke_pilot"
    assert config["allow_diagnostic_raw_angles"] is False
    assert config["direction_contract"]["unsupported_modes"] == ["c_axis"]
    assert config["direction_contract"]["diagnostic_raw_angles"] == "excluded from primary pilot pool"

    samples = config["samples"]
    assert len(samples) == 12
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


def test_task10_pilot_training_and_evaluation_configs_reference_canonical_paths() -> None:
    training_config = _load_json(TASK10_TRAINING_CONFIG_PATH)
    evaluation_config = _load_json(TASK10_EVALUATION_CONFIG_PATH)

    for config in (training_config, evaluation_config):
        assert config["execution_mode"] == "server_only_non_smoke_pilot"
        assert config["direction_contract"]["unsupported_modes"] == ["c_axis"]
        assert config["direction_contract"]["diagnostic_raw_angles"] == "excluded from primary pilot pool"

    assert training_config["dataset_manifest"] == "outputs/datasets/task10_directional_pilot/dataset.json"
    assert training_config["checkpoint_dir"] == "outputs/checkpoints/task10_directional_surrogate_pilot"
    assert training_config["run_kind"] == "task10_directional_surrogate_pilot_training"

    assert evaluation_config["dataset_manifest"] == training_config["dataset_manifest"]
    assert evaluation_config["checkpoint"] == "outputs/checkpoints/task10_directional_surrogate_pilot/model.npz"
    assert evaluation_config["report_dir"] == "outputs/runs/task10_directional_evaluation_pilot"
    assert evaluation_config["run_kind"] == "task10_directional_evaluation_pilot"
    assert evaluation_config["held_out_splits"] == ["validation", "test"]


def test_task10_runbook_records_exact_commands_and_review_artifacts() -> None:
    runbook = TASK10_RUNBOOK_PATH.read_text(encoding="utf-8")

    assert "Task 10A prepares the canonical pilot configs" in runbook
    assert "Task 10B is the actual server run." in runbook
    assert "python scripts/datasets/build_dataset.py --config configs/datasets/task10_directional_pilot_dataset.json" in runbook
    assert "python scripts/surrogate/train_surrogate.py --config configs/surrogate/task10_directional_surrogate_pilot.json" in runbook
    assert (
        "python scripts/surrogate/evaluate_surrogate.py --config "
        "configs/surrogate/task10_directional_evaluation_pilot.json"
    ) in runbook
    assert "outputs/runs/task10_pilot_server_run_note.md" in runbook
    assert "Heavy artifacts should stay on the server" in runbook
    assert "Only compact review artifacts should return to GitHub." in runbook
