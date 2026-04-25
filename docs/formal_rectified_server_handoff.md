# Formal Rectified Server Handoff

Task S9 freezes the first formal post-rectification server handoff.

This handoff is the first serious server-side dataset-generation, training, and
evaluation baseline after Tasks S1-S8.
It deliberately promotes the already observed `pre_s7_local_observation`
config family as the first formal rectified baseline rather than reviving the
older `Task 15A` medium draft.

## Why This Is The Formal Baseline

This formal handoff uses the only config family that already satisfies all of
the following together:

- post-S2 TB caution:
  it does not silently re-promote the old TB pilot as canonical truth;
- post-S3 / S4 sampling structure:
  anchor / neighborhood / bridge roles, explicit nuisance labels, and widened
  bias40 review behavior are already present;
- post-S5 observability:
  the training and evaluation paths emit curves, optimization summaries,
  grouped error reports, and representative spectrum figures;
- post-S7 decision rule:
  the architecture stays unchanged for now because there is not yet sufficient
  evidence to justify immediate widening or deepening;
- post-S8 roadmap:
  active learning remains a later loop, not the immediate next execution step.

The old `docs/runbooks/inverse_ready_medium_draft_runbook.md` remains a draft
reference only.
It is not the current formal server target because it still carries the older
medium draft family and its TB pilot assumptions.

## Formal Config Paths

The exact formal rectified server handoff paths are:

- dataset config:
  `configs/datasets/local/pre_s7_local_observation_dataset.json`
- training config:
  `configs/surrogate/local/pre_s7_local_observation_training.json`
- evaluation config:
  `configs/surrogate/local/pre_s7_local_observation_evaluation.json`

## Exact Server Commands

The exact server commands for the first formal rectified baseline are:

```bash
export LNO327_FORWARD_SRC=/home/liubx25/Ni_Research/Projects/AR/src
python scripts/datasets/build_dataset.py \
  --config configs/datasets/local/pre_s7_local_observation_dataset.json \
  --num-workers 8
python scripts/surrogate/train_surrogate.py \
  --config configs/surrogate/local/pre_s7_local_observation_training.json
python scripts/surrogate/evaluate_surrogate.py \
  --config configs/surrogate/local/pre_s7_local_observation_evaluation.json
```

This baseline keeps the current residual architecture unchanged.
Do not widen hidden width, add residual blocks, or replace the residual MLP
family in this first formal rectified handoff.

## Formal Targets

### Dataset-generation target

- dataset id:
  `pre_s7_local_observation_v1`
- expected rows:
  `96`
- worker count:
  `8`
- supported direction regimes:
  `inplane_100_no_spread`, `inplane_110_no_spread`,
  `named_mode_narrow_spread`
- pairing source roles:
  `anchor`, `neighborhood`, `bridge`

### Training target

- model type:
  `neural_residual_mlp_spectrum_surrogate`
- residual hidden width:
  `384`
- residual block count:
  `5`
- normalization:
  `layernorm`
- activation:
  `gelu`
- optimizer:
  `adamw`
- batch size:
  `24`
- CUDA:
  required

### Evaluation target

The server run must emit:

- evaluation report;
- grouped error report;
- representative best / median / worst spectrum comparisons;
- training observability curves and optimization summaries.

## Outputs That Must Stay On The Server

The following outputs are server-resident heavy artifacts and should not be
committed back to GitHub unless a later task explicitly promotes them:

- full `forward_outputs/` directories under
  `outputs/datasets/pre_s7_local_observation/`
- bulky intermediate spectrum collections
- any temporary training-state artifacts beyond the compact checkpoint family
- any copied CUDA cache, scratch, or profiling files

## Compact Artifacts That Must Return For Review

The following compact artifacts must be returned to GitHub for local review:

- `outputs/datasets/pre_s7_local_observation/dataset.json`
- `outputs/runs/pre_s7_local_observation/dataset_run_metadata.json`
- `outputs/checkpoints/pre_s7_local_observation/model.pt`
- `outputs/checkpoints/pre_s7_local_observation/metrics.json`
- `outputs/checkpoints/pre_s7_local_observation/model_card.md`
- `outputs/runs/pre_s7_local_observation/training_run_metadata.json`
- `outputs/runs/pre_s7_local_observation/training_observability/training_history.json`
- `outputs/runs/pre_s7_local_observation/training_observability/gradient_norm_summary.json`
- `outputs/runs/pre_s7_local_observation/training_observability/parameter_update_summary.json`
- `outputs/runs/pre_s7_local_observation/training_observability/figures/train_vs_validation_loss.png`
- `outputs/runs/pre_s7_local_observation/training_observability/figures/reconstruction_vs_shape_loss.png`
- `outputs/runs/pre_s7_local_observation/training_observability/figures/learning_rate_curve.png`
- `outputs/runs/pre_s7_local_observation/evaluation/evaluation_report.json`
- `outputs/runs/pre_s7_local_observation/evaluation/evaluation_report.md`
- `outputs/runs/pre_s7_local_observation/evaluation/grouped_error_report.json`
- `outputs/runs/pre_s7_local_observation/evaluation/figures/best_spectrum_comparison.png`
- `outputs/runs/pre_s7_local_observation/evaluation/figures/median_spectrum_comparison.png`
- `outputs/runs/pre_s7_local_observation/evaluation/figures/worst_spectrum_comparison.png`
- `outputs/runs/pre_s7_local_observation/evaluation_run_metadata.json`

## Review Gate

This handoff is accepted only as the first formal rectified baseline.
It does not automatically promote any larger row-budget run.

After the returned compact artifacts are reviewed, the next decision may be one
of:

- keep the same baseline family and scale further;
- revise the dataset contract before scaling;
- revise the training contract before scaling;
- or promote a later larger formal server task.

The review gate remains mandatory before any larger formal rectified run is
promoted.
