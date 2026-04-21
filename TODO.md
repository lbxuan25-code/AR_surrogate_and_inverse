# TODO

## Current Task

No current task. All planned bootstrap tasks are complete.

---

## Backlog

## Archive

### Task 7 — Experiment-Fitting Report Workflow

Completed 2026-04-21.

#### Verification
- `pytest` passed: 32 tests.
- Experiment ingest schema: `src/ar_inverse/experiments/ingest.py`.
- Preprocessing metadata schema:
  `src/ar_inverse/experiments/preprocessing.py`.
- Report workflow: `src/ar_inverse/experiments/report.py`.
- Experiment-fitting CLI: `scripts/experiments/fit_experiment.py`.
- Synthetic experiment config:
  `configs/experiments/task7_synthetic_experiment.json`.
- Synthetic experiment input:
  `outputs/experiments/task7_synthetic_fit/synthetic_experiment_spectrum.json`.
- Experiment fit report:
  `outputs/experiments/task7_synthetic_fit/experiment_fit_report.json`.
- Markdown report:
  `outputs/experiments/task7_synthetic_fit/experiment_fit_report.md`.
- Run metadata: `outputs/runs/task7_experiment_fit_run_metadata.json`.
- The report separates preprocessing, transport nuisance controls,
  candidate-family compatibility, surrogate uncertainty, and final
  direct-forward recheck results.
- The report does not claim a unique microscopic RMFT point.

### Task 6 — Inverse Search Prototype

Completed 2026-04-21.

#### Verification
- `pytest` passed: 27 tests.
- Inverse search CLI: `scripts/inverse/run_inverse_search.py`.
- Inverse smoke config: `configs/inverse/task6_smoke_inverse.json`.
- Candidate-family contract: `src/ar_inverse/inverse/candidates.py`.
- Smoke inverse report:
  `outputs/inverse/task6_smoke_inverse/inverse_report.json`.
- Markdown report:
  `outputs/inverse/task6_smoke_inverse/inverse_report.md`.
- Direct-forward recheck payloads:
  `outputs/inverse/task6_smoke_inverse/forward_rechecks/`.
- Run metadata: `outputs/runs/task6_smoke_inverse_run_metadata.json`.
- Every reported candidate family includes pairing controls, transport nuisance
  controls, uncertainty ranges, objective score, and forward recheck metadata.
- The report states that the AR data are compatible with candidate families and
  does not claim a unique microscopic truth.

### Task 5 — Surrogate Evaluation And Calibration

Completed 2026-04-21.

#### Verification
- `pytest` passed: 24 tests.
- Evaluation CLI: `scripts/surrogate/evaluate_surrogate.py`.
- Evaluation config: `configs/surrogate/task5_evaluate_linear_surrogate.json`.
- Evaluation report:
  `outputs/runs/task5_surrogate_evaluation/evaluation_report.json`.
- Markdown report:
  `outputs/runs/task5_surrogate_evaluation/evaluation_report.md`.
- Run metadata: `outputs/runs/task5_surrogate_evaluation_run_metadata.json`.
- The report identifies unsafe held-out transport regimes and requires direct
  external-forward fallback for unsafe or unseen regimes.

### Task 4 — Train First Surrogate Baseline

Completed 2026-04-21.

#### Verification
- `pytest` passed: 20 tests.
- Training script: `scripts/surrogate/train_surrogate.py`.
- Training config: `configs/surrogate/task4_linear_surrogate.json`.
- Model definition: `src/ar_inverse/surrogate/models.py`.
- Checkpoint: `outputs/checkpoints/task4_linear_surrogate/model.npz`.
- Metrics: `outputs/checkpoints/task4_linear_surrogate/metrics.json`.
- Model card with dataset and forward metadata:
  `outputs/checkpoints/task4_linear_surrogate/model_card.md`.
- Run metadata: `outputs/runs/task4_linear_surrogate_run_metadata.json`.
- The baseline was evaluated on held-out `validation` and `test` spectra from
  the Task 3 forward-generated dataset.

### Task 3 — Implement Dataset Generation Orchestration

Completed 2026-04-21.

#### Verification
- `pytest` passed: 16 tests.
- Dataset generation CLI: `scripts/datasets/build_dataset.py`.
- Smoke config: `configs/datasets/task3_smoke_dataset.json`.
- Resumable manifest:
  `outputs/datasets/task3_orchestration_smoke/dataset.json`.
- Smoke forward outputs:
  `outputs/datasets/task3_orchestration_smoke/forward_outputs/`.
- Run metadata: `outputs/runs/task3_dataset_generation_run_metadata.json`.
- The generator calls the external `forward` package only through the stable
  interface and does not import or duplicate normal-state, pairing, projection,
  interface, or BTK internals.

### Task 2 — Define Dataset Schema And Sampling Policy

Completed 2026-04-21.

#### Verification
- `pytest` passed: 12 tests.
- Dataset schema note: `docs/dataset_schema.md`.
- Sampling policy note: `docs/sampling_policy.md`.
- Smoke dataset manifest:
  `outputs/datasets/task2_smoke_fit_layer/dataset.json`.
- Smoke forward outputs:
  `outputs/datasets/task2_smoke_fit_layer/forward_outputs/`.
- Run metadata: `outputs/runs/task2_smoke_dataset_run_metadata.json`.
- Every dataset row records forward request, forward output reference, split
  label, sampling policy id, and full forward-interface metadata.

### Task 1 — Bootstrap Repository Skeleton And Forward Dependency

Completed 2026-04-21.

#### Verification
- `pytest` passed: 5 tests.
- Generated payload: `outputs/datasets/fit_layer_forward_smoke_payload.json`.
- Run metadata: `outputs/runs/task1_forward_smoke_run_metadata.json`.
- Forward metadata recorded: `forward_interface_version`,
  `output_schema_version`, `pairing_convention_id`,
  `formal_baseline_record`, `formal_baseline_selection_rule`,
  `projection_config`, `git_commit`, and `git_dirty`.
