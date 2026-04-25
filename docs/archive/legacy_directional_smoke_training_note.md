# Task 9 Directional Surrogate Smoke Training Note

Task 9 is the smoke-scale direction-aware surrogate training loop. It verifies
that the canonical direction-aware dataset, training, evaluation, checkpoint,
and run-metadata paths line up before any non-smoke pilot or server-scale work.

## Canonical Entries

- Dataset config: `configs/datasets/smoke/directional_smoke_dataset.json`
- Training config: `configs/surrogate/smoke/directional_smoke_training.json`
- Evaluation config: `configs/surrogate/smoke/directional_smoke_evaluation.json`

## Canonical Outputs

- Dataset manifest: `outputs/datasets/task8_directional_smoke/dataset.json`
- Dataset run metadata: `outputs/runs/task8_directional_dataset_run_metadata.json`
- Checkpoint: `outputs/checkpoints/task9_directional_surrogate_smoke/model.npz`
- Metrics: `outputs/checkpoints/task9_directional_surrogate_smoke/metrics.json`
- Model card: `outputs/checkpoints/task9_directional_surrogate_smoke/model_card.md`
- Evaluation report: `outputs/runs/task9_directional_evaluation_smoke/evaluation_report.json`
- Evaluation markdown: `outputs/runs/task9_directional_evaluation_smoke/evaluation_report.md`
- Evaluation run metadata:
  `outputs/runs/task9_directional_evaluation_smoke_run_metadata.json`

## Legacy Non-Canonical Paths

These remain readable for compatibility, but they are not the current canonical
entry points:

- `configs/datasets/task3_smoke_dataset.json`
- `configs/surrogate/task4_linear_surrogate.json`
- `configs/surrogate/task5_evaluate_linear_surrogate.json`
- `outputs/datasets/task3_orchestration_smoke/`
- `outputs/checkpoints/task4_linear_surrogate/`
- `outputs/runs/task5_surrogate_evaluation/`

The legacy configs carry `legacy_*` roles and point to their current canonical
successors.

## Verified Direction Contract

The Task 9 smoke loop uses only:

- `inplane_100`, no spread;
- `inplane_110`, no spread;
- narrow named-mode spread around `inplane_110`.

It excludes `c_axis`, generic raw-angle primary training data, non-smoke pilot
sampling, and server-scale generation.
