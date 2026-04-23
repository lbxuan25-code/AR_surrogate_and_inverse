# TODO

## Current Task

### Task 10 — Build and validate a small non-smoke pilot dataset

#### Goal
Create the first non-smoke direction-aware dataset, still small enough to validate locally,
but large enough to expose sampling, metadata, and training problems before server-scale generation.

#### Why this task exists
The current smoke dataset proves contract wiring, not dataset maturity.
Before spending server time, the repository must prove that:
- non-smoke dataset generation works,
- manifests remain consistent,
- forward metadata families stay fixed,
- direction regimes are sampled intentionally,
- and training code can consume a larger dataset without schema surprises.

#### Scope
Do:
- create a pilot dataset config;
- sample only supported truth-grade direction regimes;
- keep generic raw angles excluded;
- keep `c_axis` excluded;
- generate a local pilot dataset;
- run one pilot training and one pilot evaluation.

Do not:
- start full server-scale generation;
- include experiment-side direction mixtures;
- include diagnostic-only raw angles in the primary pilot pool.

#### Minimum pilot sampling policy
The pilot dataset must include:
- `inplane_100`, no spread
- `inplane_110`, no spread
- a narrow-spread subset around supported named modes

The pilot dataset should cover:
- pairing controls
- `barrier_z`
- `gamma`
- temperature

#### Required outputs
- pilot dataset config
- pilot dataset manifest
- pilot forward-output directory
- pilot training config
- pilot evaluation config
- pilot checkpoint
- pilot evaluation report
- pilot run metadata

#### Acceptance checklist
- [ ] pilot manifest is valid and uses `ar_inverse_dataset_row_v2`
- [ ] every row preserves direction block and forward provenance
- [ ] pilot dataset contains only supported named modes and narrow spread
- [ ] pilot training runs successfully
- [ ] pilot evaluation runs successfully
- [ ] no config or report still pretends that old task4/task5 names are the canonical current path
- [ ] dataset and training metadata clearly identify one fixed forward metadata family

#### Promotion rule
Only after Task 10 is complete and verified may Task 11 move into Current Task.

---

## Backlog

### Task 11 — Freeze the production direction-aware dataset contract for server generation

#### Goal
Define the exact production dataset family and the exact production training contract
that will be sent to the server.

This task does not yet run the full server-scale job.
It prepares a server-ready, version-frozen specification.

#### Why this task exists
Large-scale generation should only happen after the repository has one clear answer to:
- what is in the production dataset,
- what is excluded,
- which forward commit / metadata family it depends on,
- which direction regimes are truth-grade,
- and which training config is the official one.

#### Scope
Do:
- define one production dataset config;
- define one production training config;
- define one production evaluation config;
- freeze the forward metadata family and direction contract version;
- document the exact allowed sampling domain.

Do not:
- include `c_axis`
- include generic raw angles in the primary production pool
- include experiment-side multi-direction mixture fitting in the surrogate truth dataset

#### Production truth-grade training domain
The production surrogate truth domain must be limited to:
- `inplane_100`
- `inplane_110`
- narrow spread around supported named modes

The production domain must explicitly exclude:
- `c_axis`
- arbitrary or wide multi-direction mixtures
- diagnostic raw in-plane angles unless a later separate task promotes them

#### Required outputs
- production dataset config
- production training config
- production evaluation config
- a short production contract note describing:
  - included regimes
  - excluded regimes
  - fixed forward metadata family
  - expected output directories
- one server handoff checklist

#### Acceptance checklist
- [ ] one canonical production dataset config exists
- [ ] one canonical production training config exists
- [ ] one canonical production evaluation config exists
- [ ] included and excluded direction regimes are written explicitly
- [ ] forward metadata family is frozen and documented
- [ ] server handoff checklist is complete
- [ ] no ambiguity remains about what data may enter the production training pool

#### Promotion rule
Only after Task 11 is complete and verified may Task 12 move into Current Task.

---

### Task 12 — Start server-side large-scale dataset generation and first surrogate training run

#### Goal
Use the frozen production configs from Task 11 to begin:
- large-scale forward-backed dataset generation
- and the first real direction-aware surrogate training run

This is the first task intended for the server.

#### Scope
Do:
- launch the production dataset generation using the frozen config;
- verify early manifest growth and metadata consistency;
- launch the first production surrogate training run once enough rows exist;
- save checkpoint, metrics, model card, and run metadata under the canonical production naming.

Do not:
- expand the direction domain during the run;
- add experimental mixed-direction fitting into the training data;
- change the forward repository contract mid-run.

#### Required outputs
- production dataset manifest
- production dataset run metadata
- first production surrogate checkpoint
- first production surrogate metrics
- first production surrogate model card
- production evaluation report
- server run notes with the exact commands and environment used

#### Acceptance checklist
- [ ] large-scale dataset generation starts from the frozen production config
- [ ] generated rows preserve the frozen forward metadata family
- [ ] first production training run starts successfully
- [ ] production checkpoint and metrics are written
- [ ] model card states supported direction regimes and fallback rules
- [ ] production evaluation report is generated
- [ ] run notes are sufficient to restart or continue on the server

---

## Archive

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

#### Verification
- `pytest` passed: 39 tests.
- Direction contract helpers: `src/ar_inverse/direction.py`.
- Direction-aware dataset config:
  `configs/datasets/task8_directional_smoke_dataset.json`.
- Direction-aware dataset manifest:
  `outputs/datasets/task8_directional_smoke/dataset.json`.
- Run metadata:
  `outputs/runs/task8_directional_dataset_run_metadata.json`.
- Dataset rows use `ar_inverse_dataset_row_v2` and include `direction` blocks
  for `inplane_100_no_spread`, `inplane_110_no_spread`, and
  `named_mode_narrow_spread`.
- Surrogate feature extraction now separates named-mode identity, transport
  controls, spread controls, and raw angle auxiliary metadata.
- Evaluation report includes `direction_regime_report` and direction-aware
  fallback fields.
- Inverse and experiment configs accept direction priors and reject unsupported
  direction requests such as `c_axis`.
- README and docs describe supported named modes, unsupported `c_axis`,
  diagnostic-only raw angles, and narrow-spread-only directional spread.

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
