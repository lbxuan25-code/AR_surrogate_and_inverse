# TODO

## Current Task

### Task 11A — Prepare the production server contract

#### Goal
Prepare one production dataset contract and one production training contract for
server-scale generation, without launching the server-scale run yet.

#### Scope
Do:
- define one canonical production dataset config;
- define one canonical production training config;
- define one canonical production evaluation config;
- freeze the forward metadata family and direction contract version;
- write a production server handoff checklist.

Do not:
- start server-scale generation;
- start production training;
- widen the direction domain;
- add experiment-side multi-direction mixtures to the surrogate truth dataset.

#### Production truth-grade domain
The production surrogate truth domain must remain limited to:
- `inplane_100`
- `inplane_110`
- narrow spread around supported named modes

The production domain must explicitly exclude:
- `c_axis`
- arbitrary or wide multi-direction mixtures
- diagnostic raw in-plane angles unless a later task promotes them

#### Acceptance checklist
- [ ] one canonical production dataset config exists
- [ ] one canonical production training config exists
- [ ] one canonical production evaluation config exists
- [ ] included and excluded direction regimes are written explicitly
- [ ] the fixed forward metadata family is documented
- [ ] a server handoff checklist exists

#### Promotion rule
Only after Task 11A is complete may Task 11B move into Current Task.

---

## Backlog

### Task 11B — Run the first production server job and return compact review artifacts

#### Goal
Run the first server-scale production dataset generation and surrogate training,
then return compact review artifacts to GitHub for local Codex validation.

#### Returned artifacts required for Task 11B review
At minimum:
- production run metadata
- production metrics
- production evaluation report
- production model card
- production server run note
- compact dataset family metadata proving the frozen forward metadata family was used

Do not commit heavyweight production outputs unless explicitly requested.

#### Acceptance checklist
- [ ] server-scale generation used the frozen production config
- [ ] returned artifacts identify the frozen forward metadata family
- [ ] first production training run started successfully
- [ ] metrics and evaluation report exist
- [ ] model card states supported direction regimes and fallback rules
- [ ] local review confirms consistency before any later task proceeds

---

## Archive

### Task 10B — Run the pilot on the server and validate the returned artifacts

Completed 2026-04-23.

#### Verification
- GitHub review commit accepted:
  `be2c1f178902e087418bf199a6f5541ee1433019`.
- Returned pilot manifest:
  `outputs/datasets/task10_directional_pilot/dataset.json`.
- Returned pilot dataset run metadata:
  `outputs/runs/task10_directional_dataset_run_metadata.json`.
- Returned pilot training metrics:
  `outputs/checkpoints/task10_directional_surrogate_pilot/metrics.json`.
- Returned pilot model card:
  `outputs/checkpoints/task10_directional_surrogate_pilot/model_card.md`.
- Returned pilot training run metadata:
  `outputs/runs/task10_directional_surrogate_pilot_run_metadata.json`.
- Returned pilot evaluation report:
  `outputs/runs/task10_directional_evaluation_pilot/evaluation_report.json`.
- Returned pilot evaluation markdown:
  `outputs/runs/task10_directional_evaluation_pilot/evaluation_report.md`.
- Returned pilot evaluation run metadata:
  `outputs/runs/task10_directional_evaluation_pilot_run_metadata.json`.
- Returned server run note:
  `outputs/runs/task10_pilot_server_run_note.md`.
- Local review confirmed `ar_inverse_dataset_row_v2` rows, preserved direction
  blocks and forward provenance, supported named modes plus narrow spread only,
  and one clean forward metadata family with `git_dirty: false`.

### Task 10A — Prepare the small non-smoke pilot for server execution

Completed 2026-04-23.

#### Verification
- Canonical pilot dataset config:
  `configs/datasets/task10_directional_pilot_dataset.json`.
- Canonical pilot training config:
  `configs/surrogate/task10_directional_surrogate_pilot.json`.
- Canonical pilot evaluation config:
  `configs/surrogate/task10_directional_evaluation_pilot.json`.
- Canonical server runbook:
  `docs/task10_pilot_server_runbook.md`.
- Lightweight validation test:
  `tests/test_task10_pilot_handoff.py`.
- Task 10A intentionally did not run pilot dataset generation, pilot training,
  or pilot evaluation in the local workspace.
- No heavy pilot outputs were fabricated locally.

### Task 9 — Complete the direction-aware surrogate smoke training loop

Completed 2026-04-23.

#### Verification
- `pytest` passed: 39 tests.
- Canonical dataset config rerun:
  `configs/datasets/task8_directional_smoke_dataset.json`.
- Canonical training config rerun:
  `configs/surrogate/task9_directional_surrogate_smoke.json`.
- Canonical evaluation config rerun:
  `configs/surrogate/task9_directional_evaluation_smoke.json`.
- Smoke checkpoint:
  `outputs/checkpoints/task9_directional_surrogate_smoke/model.npz`.
- Smoke metrics:
  `outputs/checkpoints/task9_directional_surrogate_smoke/metrics.json`.
- Smoke model card:
  `outputs/checkpoints/task9_directional_surrogate_smoke/model_card.md`.
- Smoke evaluation report:
  `outputs/runs/task9_directional_evaluation_smoke/evaluation_report.json`.
- Smoke evaluation markdown:
  `outputs/runs/task9_directional_evaluation_smoke/evaluation_report.md`.
- Smoke run metadata:
  `outputs/runs/task9_directional_surrogate_smoke_run_metadata.json` and
  `outputs/runs/task9_directional_evaluation_smoke_run_metadata.json`.
- The checkpoint feature names include explicit direction semantics, spread
  controls, and raw angle only as auxiliary metadata.
- The evaluation report includes both `transport_regime_report` and
  `direction_regime_report`.
- Task 9 note:
  `docs/task9_directional_smoke_training_note.md`.
- Legacy `task3`, `task4`, and `task5` configs remain readable and marked as
  non-canonical legacy paths.

### Task 8 — Integrate the directional feature contract into the surrogate/inverse repository

Completed 2026-04-22.

### Task 7 — Experiment-fitting report workflow

Completed previously.

### Task 6 — Inverse search prototype

Completed previously.

### Task 5 — Surrogate evaluation and calibration

Completed previously.

### Task 4 — Train first surrogate baseline

Completed previously.

### Task 3 — Implement dataset generation orchestration

Completed previously.

### Task 2 — Define dataset schema and sampling policy

Completed previously.

### Task 1 — Bootstrap repository skeleton and forward dependency

Completed previously.
