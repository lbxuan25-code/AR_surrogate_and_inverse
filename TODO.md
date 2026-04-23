# TODO

## Current Task

### Task 13A — Freeze the high-accuracy large-scale surrogate contract and upgrade the training stack

#### Goal
Prepare a high-accuracy large-scale surrogate contract that does more than scale
up row count. This task must also freeze the model/loss/calibration stack that
will be used for the first truly accuracy-driven heavy run.

The objective is not merely “larger training,” but:
- better held-out spectral accuracy,
- better regime robustness,
- explicit uncertainty-aware fallback behavior,
- and a training stack suitable for later inverse acceleration.

#### Why this task now replaces the older generic 13A
Task 12B proved that the first neural MLP beats the ridge baseline under the
frozen forward-family and direction contract. However, the current neural stack
is still only a first-generation model:
- plain feed-forward MLP,
- plain pointwise MSE training,
- no explicit uncertainty estimation,
- no residual/depth-stabilization path,
- no explicit low-bias / shape-aware loss weighting.

Before the first heavy campaign, these accuracy-critical choices must be frozen.

#### Scope
Do:
- define one canonical large-scale dataset config for an accuracy-driven heavy run;
- define one canonical high-accuracy neural training config;
- define one canonical large-scale evaluation config;
- upgrade the neural surrogate stack from “plain MLP + plain MSE” to a more
  stable and accuracy-oriented contract;
- freeze the uncertainty/calibration contract for later inverse use;
- write one large-scale server handoff note with exact commands and artifact rules;
- add lightweight tests validating the new large-scale config and new model/loss wiring.

Do not:
- start the large-scale run yet;
- widen the truth-grade direction domain;
- add `c_axis` or diagnostic raw-angle primary rows;
- silently replace the frozen forward metadata family;
- silently remove the Task 12 plain-MLP comparator path.

#### Frozen truth-domain restrictions
The large-scale contract must remain limited to:
- `inplane_100`, no spread
- `inplane_110`, no spread
- narrow named-mode-centered spread only

The contract must continue to exclude:
- `c_axis`
- diagnostic raw-angle primary rows
- arbitrary wide spread
- experiment-side direction mixtures in the surrogate truth dataset

#### Large-scale dataset contract
The canonical heavy dataset config must target a genuinely large run, for example:
- total rows: `4096`
- train / validation / test: `3072 / 512 / 512`
- explicit quotas across:
  - `inplane_100_no_spread`
  - `inplane_110_no_spread`
  - `named_mode_narrow_spread`
- explicit quotas across transport regimes:
  - low/high barrier
  - low/high gamma
  - low/high temperature
- fixed `nk` and fixed bias-grid policy
- no silent sampling drift across splits

The config must include explicit regime-count targets and a machine-checkable
`expected_num_rows`.

#### High-accuracy model-stack contract
The heavy run must freeze a stronger neural contract than Task 12B.

Required upgrades:
- keep the existing plain neural MLP path as a comparator;
- add one canonical high-accuracy surrogate path using:
  - residual MLP blocks or another equally simple depth-stabilized feed-forward design,
  - normalization support (`LayerNorm` or equivalent),
  - configurable width/depth,
  - checkpoint/readback support fully compatible with evaluation/report code.

Do not introduce architectures that change the meaning of the current feature
contract or output spectrum contract.

#### High-accuracy loss contract
The canonical high-accuracy training config must not use plain pointwise MSE alone.

It must freeze a composite loss with at least:
- weighted spectrum reconstruction loss,
- stronger weight near low-bias / central-bias regions,
- one shape-aware term such as first-difference or local-slope consistency,
- explicit coefficients recorded in config and run metadata.

The loss contract must be documented in the model card and run metadata.

#### Uncertainty and fallback contract
The heavy run must freeze one uncertainty-aware policy for later inverse use.

Preferred contract:
- ensemble of `3` independently seeded high-accuracy models,
- ensemble-mean prediction for reporting,
- ensemble disagreement summary recorded in evaluation artifacts.

At minimum, Task 13A must define:
- the ensemble seed set,
- how ensemble disagreement is summarized,
- which disagreement thresholds trigger direct-forward fallback,
- how this joins the existing regime-level fallback policy.

#### Required repository outputs from Task 13A
- canonical large-scale dataset config
- canonical high-accuracy neural training config
- canonical large-scale evaluation config
- updated surrogate model code for the frozen high-accuracy path
- updated loss implementation and config wiring
- updated uncertainty / ensemble evaluation wiring
- large-scale server handoff note
- lightweight validation tests
- updated `TODO.md` and `AGENTS.md`

#### Acceptance checklist
- [ ] one canonical large-scale dataset config exists
- [ ] one canonical high-accuracy neural training config exists
- [ ] one canonical large-scale evaluation config exists
- [ ] explicit row quotas exist for all supported direction regimes
- [ ] explicit transport-regime quotas exist
- [ ] the frozen forward metadata family remains explicit
- [ ] the high-accuracy model path is implemented and checkpoint-compatible
- [ ] the composite weighted loss is implemented and documented
- [ ] the uncertainty / ensemble contract is explicit
- [ ] a large-scale server handoff note exists
- [ ] lightweight validation tests pass
- [ ] no heavy local outputs were fabricated

#### Promotion rule
Only after Task 13A is complete may Task 13B move into Current Task.

---

### Task 13B — Launch the first high-accuracy heavy surrogate campaign

#### Goal
Run the first truly heavy, accuracy-driven server-side surrogate campaign using
the frozen large-scale contract from Task 13A.

This task is not only a heavy run. It is the first run that must be judged by:
- large-scale held-out accuracy,
- regime robustness,
- uncertainty-aware reliability,
- and suitability for later inverse acceleration.

#### Server-side execution scope
The server run must include:
- large-scale forward dataset generation,
- training of the frozen high-accuracy neural path,
- training of the frozen ensemble members when the ensemble contract is enabled,
- large-scale evaluation on validation/test splits,
- uncertainty-aware reporting,
- compact returned artifacts for local acceptance.

#### Intended heavy scale
The run must follow the canonical Task 13A contract exactly, including:
- total rows around `4096`
- explicit regime quotas
- fixed bias grid
- fixed `nk`
- frozen forward metadata family
- unchanged truth-grade direction contract

Do not widen the direction domain during this task.

#### Required returned artifacts for review
At minimum, commit back:
- large-scale dataset run metadata
- compact dataset family metadata or the full manifest if still reviewable
- high-accuracy training metrics
- high-accuracy model card
- high-accuracy training run metadata
- evaluation report
- evaluation markdown
- evaluation run metadata
- ensemble summary report if ensemble is enabled
- server run note

Heavy artifacts that should remain on the server unless explicitly promoted:
- large forward-output directories
- full raw spectra collections
- individual heavy checkpoints
- copied intermediate training artifacts

#### Mandatory comparison policy
Task 13B review must compare:
- the committed ridge baseline,
- the committed Task 12B plain neural baseline,
- and the new Task 13 heavy model / ensemble result.

The large-scale campaign is not accepted merely because it trains successfully.
It must show that the heavy model is at least as reliable as Task 12B and is
better justified for production inverse acceleration.

#### Accuracy acceptance targets
Task 13B should be accepted only if all of the following hold:

Global held-out requirements:
- [ ] evaluation report exists
- [ ] mean held-out RMSE remains within the configured production-safe range
- [ ] mean held-out max absolute error remains within the configured production-safe range
- [ ] held-out unsafe fraction is no worse than Task 12B and remains near zero

Direction-regime requirements:
- [ ] `inplane_100_no_spread` remains safe for inverse acceleration
- [ ] `inplane_110_no_spread` remains safe for inverse acceleration
- [ ] `named_mode_narrow_spread` remains safe for inverse acceleration

Robustness requirements:
- [ ] no supported held-out direction regime collapses relative to Task 12B
- [ ] no major transport regime becomes newly unsafe without being explicitly documented
- [ ] evaluation includes per-regime metrics and worst-case rows

Uncertainty requirements:
- [ ] ensemble disagreement or equivalent uncertainty summary exists
- [ ] disagreement-triggered fallback policy is explicit
- [ ] high-disagreement or unsafe regions are documented as direct-forward-required

Contract requirements:
- [ ] heavy run used the frozen large-scale dataset config
- [ ] heavy run used the frozen forward metadata family
- [ ] heavy run preserved the validated direction contract only
- [ ] local review confirms no schema / naming / contract mismatch

#### Failure rule
If the heavy run achieves lower average error but introduces unstable or unsafe
regimes not justified by the uncertainty contract, Task 13B is not accepted.

#### Success rule
Task 13B is complete only after local review concludes that the returned heavy
artifacts define a clearly documented, uncertainty-aware, high-accuracy
surrogate family suitable for later inverse acceleration under the frozen
direction contract.

---

## Archive

### Task 12B — Run the first medium-scale neural surrogate validation job

Completed 2026-04-23.

#### Verification
- Returned medium-scale dataset run metadata:
  `outputs/runs/task12_directional_medium_dataset_run_metadata.json`.
- Returned medium-scale manifest:
  `outputs/datasets/task12_directional_medium_neural/dataset.json`.
- Returned neural training metrics:
  `outputs/checkpoints/task12_directional_neural_medium/metrics.json`.
- Returned neural model card:
  `outputs/checkpoints/task12_directional_neural_medium/model_card.md`.
- Returned neural training run metadata:
  `outputs/runs/task12_directional_neural_medium_run_metadata.json`.
- Returned neural evaluation report:
  `outputs/runs/task12_directional_neural_evaluation_medium/evaluation_report.json`.
- Returned neural evaluation markdown:
  `outputs/runs/task12_directional_neural_evaluation_medium/evaluation_report.md`.
- Returned neural evaluation run metadata:
  `outputs/runs/task12_directional_neural_evaluation_medium_run_metadata.json`.
- Returned Task 12 server run note:
  `outputs/runs/task12_neural_medium_server_run_note.md`.
- Local review confirmed the canonical Task 12 config produced `352` rows with
  preserved truth-grade direction coverage:
  `88` `inplane_100_no_spread`,
  `88` `inplane_110_no_spread`,
  `176` `named_mode_narrow_spread`.
- Local review confirmed one frozen clean forward metadata family across the
  returned artifacts with
  `forward_interface_version: ar_forward_v1`,
  `output_schema_version: ar_forward_output_v1`,
  `pairing_convention_id: round2_physical_channels_task_h_fit_layer_v1`,
  `git_commit: b85a5cb304acbfd5d51133251ef57293bd0abd2b`,
  and `git_dirty: false`.
- Local review confirmed the returned Task 12 dataset and reports preserve the
  validated direction contract only: supported named modes
  `inplane_100` / `inplane_110`, narrow named-mode-centered spread only, no
  `c_axis`, and no diagnostic raw-angle primary rows.
- Local review compared the returned Task 12 neural evaluation against the
  committed ridge comparator under the same frozen forward-family and direction
  contract and found meaningful held-out improvement, including:
  mean RMSE `0.0024540644` vs ridge `0.0646178135`,
  max absolute error `0.0145308234` vs ridge `0.2772479170`,
  and unsafe fraction `0.0` vs ridge `0.625`.
- Local review confirmed all three held-out direction regimes in Task 12 were
  marked safe for inverse acceleration under the configured thresholds, whereas
  the committed ridge comparator marked all held-out direction regimes unsafe.

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
