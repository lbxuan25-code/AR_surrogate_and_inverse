# Task 15 Inverse-Ready Medium Handoff

Task 15A prepares the first inverse-ready medium-scale contract only.
It is now a draft reference handoff retained for comparison during the
surrogate-rectification program. It is not the current next server execution
target.
Do not generate the dataset, run the training, or run the evaluation in the
local Codex workspace.
Do not treat this document as an active server instruction unless a later
`TODO.md` task explicitly re-promotes or replaces this contract after the
rectification program.

Any later task that explicitly revives this contract family should start from
the exact files frozen here, unless that later task replaces them with a new
rectified contract.

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

## Draft Reference Row Budget

The frozen draft contract targeted exactly:

- total rows: `9600`
- train rows: `7680`
- validation rows: `960`
- test rows: `960`

The row budget is out of contract if a different total or split is used for
this draft reference contract.

## Frozen Draft Sub-Budgets

The archived draft contract preserves the canonical planning targets recorded in
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

## Reference Commands If This Draft Is Later Revived

If a later task explicitly revives or supersedes this draft contract, the
reference commands frozen here are:

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task15_inverse_ready_medium_dataset.json
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task15_inverse_ready_medium_training.json
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task15_inverse_ready_medium_evaluation.json
```

## Reference Output Paths

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

## Reference Returned Artifacts For Review

If a later task revives this contract family, the compact review artifacts to
return remain:

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
It remains complete only as a local preparation step that froze the first
inverse-ready medium-scale contract before the repository entered the
rectification-first phase.
