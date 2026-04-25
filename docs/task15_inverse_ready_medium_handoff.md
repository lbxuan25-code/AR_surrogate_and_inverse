# Task 15 Inverse-Ready Medium Handoff

Task 15A prepares the first inverse-ready medium-scale contract only.
Do not generate the dataset, run the training, or run the evaluation in the
local Codex workspace.

The later manual server task must use the exact files frozen here.

## Canonical Configs

- Dataset config: `configs/datasets/task15_inverse_ready_medium_dataset.json`
- Training config: `configs/surrogate/task15_inverse_ready_medium_training.json`
- Evaluation config: `configs/surrogate/task15_inverse_ready_medium_evaluation.json`

## Contract Composition

This medium-scale contract combines the already frozen Task 14 inputs:

- RMFT-projected anchor / neighborhood / bridge pairing source
- gauge-fixed projected 7+1 pairing representation
- widened `[-40, 40] meV` spectrum window with `241` bias points
- expanded nuisance-domain contract with core and guard-band coverage
- five-coordinate low-dimensional TB pilot variation
- unchanged truth-grade direction contract:
  `inplane_100`, `inplane_110`, and narrow named-mode-centered spread only

Unsupported direction modes remain out of contract:

- `c_axis`

Generic raw-angle rows remain excluded from the canonical primary pool.

## Fixed Row Budget

The later manual server run must target exactly:

- total rows: `9600`
- train rows: `7680`
- validation rows: `960`
- test rows: `960`

The row budget is out of contract if a different total or split is used.

## Frozen Medium-Contract Sub-Budgets

The later server run must preserve the canonical planning targets recorded in
the dataset config:

- pairing roles:
  `anchor = 3840`,
  `neighborhood = 3840`,
  `bridge = 1920`
- direction regimes:
  `inplane_100_no_spread = 3600`,
  `inplane_110_no_spread = 3600`,
  `named_mode_narrow_spread = 2400`
- transport tiers:
  `core = 7680`,
  `guard_band = 1920`
- TB pilot bands:
  `near_baseline = 6720`,
  `edge_probe = 2880`

## Later Manual Server Commands

When Task 15B is promoted, run from the repository root:

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task15_inverse_ready_medium_dataset.json
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task15_inverse_ready_medium_training.json
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task15_inverse_ready_medium_evaluation.json
```

## Expected Output Paths

- `outputs/datasets/task15_inverse_ready_medium/dataset.json`
- `outputs/runs/task15_inverse_ready_medium_dataset_run_metadata.json`
- `outputs/checkpoints/task15_inverse_ready_medium/ensemble_manifest.json`
- `outputs/checkpoints/task15_inverse_ready_medium/metrics.json`
- `outputs/checkpoints/task15_inverse_ready_medium/model_card.md`
- `outputs/runs/task15_inverse_ready_medium_training_run_metadata.json`
- `outputs/runs/task15_inverse_ready_medium_evaluation/evaluation_report.json`
- `outputs/runs/task15_inverse_ready_medium_evaluation/evaluation_report.md`
- `outputs/runs/task15_inverse_ready_medium_evaluation_run_metadata.json`
- `outputs/runs/task15_inverse_ready_medium_server_run_note.md`

## Returned Artifacts For Review

Task 15B should return these compact review artifacts to GitHub:

- `outputs/datasets/task15_inverse_ready_medium/dataset.json`
- `outputs/runs/task15_inverse_ready_medium_dataset_run_metadata.json`
- `outputs/checkpoints/task15_inverse_ready_medium/ensemble_manifest.json`
- `outputs/checkpoints/task15_inverse_ready_medium/metrics.json`
- `outputs/checkpoints/task15_inverse_ready_medium/model_card.md`
- `outputs/runs/task15_inverse_ready_medium_training_run_metadata.json`
- `outputs/runs/task15_inverse_ready_medium_evaluation/evaluation_report.json`
- `outputs/runs/task15_inverse_ready_medium_evaluation/evaluation_report.md`
- `outputs/runs/task15_inverse_ready_medium_evaluation_run_metadata.json`
- `outputs/runs/task15_inverse_ready_medium_server_run_note.md`

Heavy artifacts should stay on the server, including:

- expanded forward-output directories
- large local checkpoint members beyond the compact manifest
- bulky intermediate spectrum collections

## Review Boundary

Task 15A is not the later server run.
It is complete only as a local preparation step that freezes the first
inverse-ready medium-scale contract and the instructions the later Task 15B
manual server run must follow.
