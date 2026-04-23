# TODO

## Current Task

### Task 12B — Run the first medium-scale neural surrogate validation job

#### Goal
Run the first medium-scale server-side neural surrogate validation job using the
Task 12A configs, then return compact artifacts to GitHub for local review.

This is the first task that should be treated as the beginning of formal neural
surrogate training, but it is still a validation-scale job rather than the
final large-scale production campaign.

#### Intended scale
Target a medium-scale dataset budget large enough to test neural capacity
meaningfully, for example:
- roughly 300 to 600 total rows
- train / validation / test split with explicit regime coverage
- preserved coverage across:
  - `inplane_100_no_spread`
  - `inplane_110_no_spread`
  - `named_mode_narrow_spread`

Do not widen the direction domain during this task.

#### Returned artifacts required for Task 12B review
At minimum:
- dataset run metadata
- training metrics
- model card
- training run metadata
- evaluation report
- evaluation markdown
- evaluation run metadata
- Task 12 server run note
- compact dataset family metadata, or the full manifest if still reviewable

Heavy outputs such as:
- full forward-output directories
- large neural checkpoints
- copied raw spectra collections

should stay on the server unless a later task explicitly requests a compact
canonical sample.

#### Acceptance checklist for Task 12B
- [ ] medium-scale generation used the Task 12 canonical config
- [ ] returned artifacts preserve the frozen forward metadata family
- [ ] returned artifacts preserve the validated direction contract only
- [ ] neural training completed and produced checkpoints/metrics
- [ ] evaluation report exists
- [ ] neural validation is meaningfully stronger than the ridge baseline on at
      least one held-out metric or regime
- [ ] local review confirms no schema / naming / contract mismatch
- [ ] only after this review may Task 13A move into Current Task

#### Promotion rule
Only after Task 12B is complete and reviewed may Task 13A move into Current Task.

---

### Task 13A — Prepare the large-scale surrogate dataset contract

#### Goal
Freeze the first large-scale dataset and training contract for heavy server use,
using the validated neural stack and the still-frozen direction contract.

#### Scope
Do:
- define the first large-scale dataset config;
- define the first large-scale neural training config;
- define the first large-scale evaluation config;
- freeze the sampling budget and regime quotas;
- write a large-scale server handoff note.

Do not:
- start the large-scale run yet;
- widen the direction domain;
- add `c_axis` or diagnostic raw-angle primary rows.

#### Suggested scale planning targets
The contract should be written so the later heavy run can target something like:
- 2,000 to 5,000 total rows
- explicit quotas across supported direction regimes
- explicit quotas across transport regimes
- fixed bias-grid and `nk` policy
- restart-safe run metadata and artifact return rules

#### Acceptance checklist
- [ ] one canonical large-scale dataset config exists
- [ ] one canonical large-scale neural training config exists
- [ ] one canonical large-scale evaluation config exists
- [ ] regime quotas are explicit
- [ ] transport sampling policy is explicit
- [ ] the frozen forward metadata family remains explicit
- [ ] a large-scale server handoff note exists

#### Promotion rule
Only after Task 13A is complete may Task 13B move into Current Task.

---

### Task 13B — Launch the first heavy large-scale surrogate campaign

#### Goal
Run the first truly heavy server-side surrogate campaign:
- large-scale forward dataset generation
- large-scale neural surrogate training
- large-scale evaluation
- compact returned artifacts for local acceptance

This is the first task that should be treated as the full heavy surrogate
training campaign.

#### Returned artifacts required for Task 13B review
At minimum:
- large-scale dataset run metadata
- large-scale training metrics
- large-scale model card
- large-scale evaluation report
- large-scale evaluation markdown
- large-scale training/evaluation run metadata
- server run note
- compact dataset family metadata proving the frozen direction and forward
  contracts used by the heavy run

Do not commit heavyweight outputs unless explicitly promoted.

#### Acceptance checklist
- [ ] heavy run used the frozen large-scale contract
- [ ] large-scale neural training completed successfully
- [ ] returned metrics/evaluation reports exist
- [ ] local review confirms forward-family and direction-contract stability
- [ ] surrogate now defines clearly documented safe and unsafe regimes for later
      inverse acceleration work

---

## Archive

### Task 12A — Prepare the neural surrogate training stack

Completed 2026-04-23.

#### Verification
- Neural surrogate model code and dual-path checkpoint loader:
  `src/ar_inverse/surrogate/models.py`.
- Training code now supports both ridge and neural `model_type`:
  `src/ar_inverse/surrogate/train.py`.
- Evaluation code now reads ridge or neural checkpoints:
  `src/ar_inverse/surrogate/evaluate.py`.
- Dataset config now supports compact `sample_grids` expansion for canonical
  medium-scale planning:
  `src/ar_inverse/datasets/build.py`.
- Canonical Task 12 medium-scale dataset config:
  `configs/datasets/task12_directional_medium_dataset.json`.
- Canonical Task 12 neural training config:
  `configs/surrogate/task12_directional_neural_medium.json`.
- Canonical Task 12 neural evaluation config:
  `configs/surrogate/task12_directional_neural_evaluation_medium.json`.
- Task 12 server handoff note:
  `docs/task12_neural_medium_server_handoff.md`.
- Lightweight Task 12 neural contract test:
  `tests/test_task12_neural_contract.py`.
- Local `pytest` passed:
  `tests/test_task12_neural_contract.py`,
  `tests/test_task11_production_contract.py`,
  `tests/test_surrogate_training.py`,
  `tests/test_surrogate_evaluation.py`.
- Task 12A intentionally did not run medium-scale dataset generation locally
  and did not run server-scale production generation locally.
- Neural smoke checks remained local-only and tiny; no medium-scale outputs were
  fabricated in the workspace.

### Task 11B — Run the first production server job and return compact review artifacts

Completed 2026-04-23.

#### Verification
- Returned production dataset run metadata:
  `outputs/runs/task11_directional_dataset_run_metadata.json`.
- Returned production manifest:
  `outputs/datasets/task11_directional_production/dataset.json`.
- Returned production metrics:
  `outputs/checkpoints/task11_directional_surrogate_production/metrics.json`.
- Returned production model card:
  `outputs/checkpoints/task11_directional_surrogate_production/model_card.md`.
- Returned production training run metadata:
  `outputs/runs/task11_directional_surrogate_production_run_metadata.json`.
- Returned production evaluation report:
  `outputs/runs/task11_directional_evaluation_production/evaluation_report.json`.
- Returned production evaluation markdown:
  `outputs/runs/task11_directional_evaluation_production/evaluation_report.md`.
- Returned production evaluation run metadata:
  `outputs/runs/task11_directional_evaluation_production_run_metadata.json`.
- Returned production server run note:
  `outputs/runs/task11_production_server_run_note.md`.
- Local review confirmed preserved `ar_inverse_dataset_row_v2` rows, preserved
  direction blocks and forward provenance, and one frozen forward metadata
  family with `git_dirty: false`.
- Task 11B intentionally remained a compact production-style validation run,
  not the first large-scale neural campaign.

### Task 11A — Prepare the production server contract

Completed 2026-04-23.

#### Verification
- Canonical production dataset config:
  `configs/datasets/task11_directional_production_dataset.json`.
- Canonical production training config:
  `configs/surrogate/task11_directional_surrogate_production.json`.
- Canonical production evaluation config:
  `configs/surrogate/task11_directional_evaluation_production.json`.
- Production server handoff note:
  `docs/task11_production_server_handoff.md`.
- Lightweight validation test:
  `tests/test_task11_production_contract.py`.
- Local `pytest` passed:
  `tests/test_task11_production_contract.py`,
  `tests/test_task10_pilot_handoff.py`,
  `tests/test_surrogate_training.py`.
- The frozen production contract keeps only `inplane_100`, `inplane_110`, and
  narrow named-mode-centered spread, excludes `c_axis` and diagnostic raw
  angles, and freezes the clean forward metadata family accepted in Task 10B.
- Task 11A intentionally did not run server-scale dataset generation,
  production training, or production evaluation locally.

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
