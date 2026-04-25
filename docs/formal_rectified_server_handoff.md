# Formal Rectified Server Handoff

Task S9 freezes the first formal large-scale post-rectification production
draft.

This handoff supersedes the earlier 96-row `pre_s7_local_observation`
baseline as the intended production-scale target.
That 96-row family remains important as the real pre-S7 observation baseline,
but it is no longer the final formal large-scale goal.

## Status

This handoff is ready for review-gated launch preparation.

It is designed to let the user start the first serious large-scale
dataset-generation, training, and evaluation cycle after rectification while
still preserving the GitHub review gate.

This task does not launch the heavy run.
It freezes the exact draft target that should be launched next on the server
after review approval.

## Why This Draft Replaces The 96-Row Baseline

The 96-row `pre_s7_local_observation` family was necessary because it produced
the first real post-rectification observations for:

- observability integration;
- grouped error reports;
- representative spectrum review;
- and the S7 decision that the current residual architecture should remain
  unchanged for now.

But it is not large enough to serve as the final formal production target.

The larger formal production draft frozen here is the correct next target
because it:

- preserves the S7 "do not expand now" architecture decision;
- keeps S8 active learning deferred rather than silently introducing it early;
- uses the rectified pairing, sampling, joint-sampling, and observability
  contracts;
- and restores a serious production-scale row budget without reviving the older
  pre-rectification `Task 15A` medium draft.

## Exact Config Paths

The exact large-scale formal production draft paths are:

- dataset-generation target:
  `configs/datasets/production/rectified_large_production_dataset.json`
- training target:
  `configs/surrogate/production/rectified_large_production_training.json`
- evaluation target:
  `configs/surrogate/production/rectified_large_production_evaluation.json`

## Frozen Contract Alignment

This formal production draft must obey all of the following already-frozen
contracts:

- pairing representation:
  `docs/contracts/pairing_representation_contract.md`
- quality-first sampling:
  `docs/contracts/sampling_policy_v2.md`
- joint sampling:
  `docs/contracts/joint_sampling_contract.md`
- observability standard:
  `docs/standards/training_observability_standard.md`
- model-capacity decision rule:
  `docs/model_capacity_decision_rules.md`
- active-learning roadmap:
  `docs/active_learning_plan.md`

The practical consequences are:

- full projected complex 7+1 pairing representation;
- global-phase-only gauge fixing;
- no latent pairing compression;
- quality-first anchor / neighborhood / bridge structure;
- explicit nuisance and TB joint-coverage intent;
- full observability artifact family;
- no immediate widening or deepening of the residual architecture;
- no active-learning loop in this first formal large run.

## Dataset-Generation Target

The recommended first formal large-scale row budget is:

- total rows:
  `8192`
- train rows:
  `6144`
- validation rows:
  `1024`
- test rows:
  `1024`

This budget is intentionally larger than the 96-row baseline and also larger
than the earlier 4096-row Task 13 family, while still being modest enough to
serve as the first serious rectified production draft rather than an
irreversible mega-run.

The frozen draft target also records:

- worker count:
  `16`
- bias grid:
  `[-40, 40] meV`, `241` points
- pairing role targets:
  `anchor = 3072`, `neighborhood = 3072`, `bridge = 2048`
- direction regime targets:
  `inplane_100_no_spread = 2048`,
  `inplane_110_no_spread = 2048`,
  `named_mode_narrow_spread = 4096`
- TB regime targets:
  `near_baseline = 6144`,
  `edge_probe = 2048`

The dataset contract explicitly records:

- the canonical 7+1 pairing representation contract;
- the grouped TB training-facing contract plus original-parameter provenance;
- the quality-first sampling policy reference;
- the joint-sampling contract reference;
- the direction-contract boundary;
- and the fact that active learning is deferred until after this round is
  reviewed.

## Training Target

The frozen formal training target is:

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
- learning rate:
  `4e-4`
- weight decay:
  `5e-5`
- batch size:
  `48`
- epoch limit:
  `450`
- early stopping patience:
  `40`
- device:
  `auto`
- CUDA:
  required
- ensemble:
  enabled with seeds `1103`, `2207`, `3301`

This draft keeps the current residual architecture unchanged.
Do not widen hidden width, do not add residual blocks, and do not replace the
residual MLP family in this first formal production launch.

## Evaluation Target

The frozen evaluation target must emit:

- evaluation report;
- grouped error report;
- uncertainty / disagreement diagnostics;
- representative best / median / worst spectrum comparisons;
- and the full observability-linked run metadata needed for local review.

The formal evaluation thresholds are:

- safe RMSE threshold:
  `0.03`
- safe max absolute error threshold:
  `0.075`
- ensemble disagreement thresholds:
  `mean_std = 0.005`,
  `max_std = 0.025`

## Exact Run Commands

These are the exact commands to use for the first formal large-scale
post-rectification run once the review gate approves the launch:

```bash
export LNO327_FORWARD_SRC=/home/liubx25/Ni_Research/Projects/AR/src
python scripts/datasets/build_dataset.py \
  --config configs/datasets/production/rectified_large_production_dataset.json \
  --num-workers 16
python scripts/surrogate/train_surrogate.py \
  --config configs/surrogate/production/rectified_large_production_training.json
python scripts/surrogate/evaluate_surrogate.py \
  --config configs/surrogate/production/rectified_large_production_evaluation.json
```

These commands are frozen here as the next formal server launch sequence.
This task does not execute them locally.

## Heavy Artifacts That Must Stay On The Server

The following artifacts are server-resident heavy outputs and must remain on the
server unless a later task explicitly promotes them:

- full `forward_outputs/` directories under
  `outputs/datasets/rectified_large_production/`
- bulky intermediate spectrum collections
- large per-member ensemble checkpoints beyond the compact checkpoint manifest
- temporary scheduler, CUDA, profiling, cache, and scratch artifacts

## Compact Artifacts That Must Return To GitHub Review

The following compact artifacts must be committed back for review:

- `outputs/datasets/rectified_large_production/dataset.json`
- `outputs/runs/rectified_large_production_dataset_run_metadata.json`
- `outputs/checkpoints/rectified_large_production/ensemble_manifest.json`
- `outputs/checkpoints/rectified_large_production/metrics.json`
- `outputs/checkpoints/rectified_large_production/model_card.md`
- `outputs/runs/rectified_large_production_training_run_metadata.json`
- `outputs/runs/rectified_large_production/training_observability/training_history.json`
- `outputs/runs/rectified_large_production/training_observability/gradient_norm_summary.json`
- `outputs/runs/rectified_large_production/training_observability/parameter_update_summary.json`
- `outputs/runs/rectified_large_production/training_observability/figures/train_vs_validation_loss.png`
- `outputs/runs/rectified_large_production/training_observability/figures/reconstruction_vs_shape_loss.png`
- `outputs/runs/rectified_large_production/training_observability/figures/learning_rate_curve.png`
- `outputs/runs/rectified_large_production_evaluation/evaluation_report.json`
- `outputs/runs/rectified_large_production_evaluation/evaluation_report.md`
- `outputs/runs/rectified_large_production_evaluation/grouped_error_report.json`
- `outputs/runs/rectified_large_production_evaluation/figures/best_spectrum_comparison.png`
- `outputs/runs/rectified_large_production_evaluation/figures/median_spectrum_comparison.png`
- `outputs/runs/rectified_large_production_evaluation/figures/worst_spectrum_comparison.png`
- `outputs/runs/rectified_large_production_evaluation_run_metadata.json`

## Review Gate

This handoff is launch-ready only in the sense that the large-scale production
draft is now frozen with exact config paths and exact launch commands.

The review gate is still mandatory.
The user should not blindly start the heavy run without reviewing this draft,
the committed config trio, and the returned-artifact expectations.

Only after the returned compact artifacts are committed back and accepted in
local review should any later larger production task, architecture revision, or
active-learning stage be promoted.
