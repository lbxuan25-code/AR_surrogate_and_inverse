# Production Surrogate V1 Handoff

## Status

P1 prepares the first user-approved production-scale rectified surrogate run
contract.

This handoff is local preparation only. It must not run dataset generation,
training, or evaluation. P2 may execute the heavy run only after the user
accepts this P1 contract.

This contract supersedes Codex-proposed S9/S10 production paths. The old
formal-rectified handoff and `rectified_large_production_*` drafts are removed
from the active repository structure and must not be treated as the canonical P1
launch path. They are not the canonical P1 launch path.

## Canonical P1 Files

- dataset config: `configs/datasets/production_surrogate_v1.dataset.json`
- training config: `configs/training/production_surrogate_v1.training.json`
- evaluation config: `configs/evaluation/production_surrogate_v1.evaluation.json`

## Frozen Rectification Rules

This run must follow the completed S1-S8 rectification standards:

- use the full projected complex 7+1 pairing representation;
- remove only the globally redundant phase;
- do not use PCA, latent pairing compression, or learned low-dimensional
  pairing coordinates;
- preserve original TB provenance and use physically grouped TB controls as the
  training-facing form;
- use sampling-policy-v2 quality-first anchor / neighborhood / bridge coverage;
- use the joint sampling contract across pairing, nuisance, direction, and TB
  regimes;
- emit the full training observability artifact family;
- keep the residual MLP architecture unchanged under the S7 capacity decision;
- defer active learning until after production v1 has been run and reviewed.

## Dataset-Generation Target

Production surrogate v1 freezes a first local production-scale row budget:

- total rows: `8192`
- train rows: `6144`
- validation rows: `1024`
- test rows: `1024`
- CPU worker recommendation: `8`
- bias grid: `[-40, 40] meV` with `241` points

The target is intentionally larger than the pre-S7 96-row observation run while
remaining reviewable on the user's local WSL2 machine.

Sampling composition:

- pairing source roles: `anchor = 3072`, `neighborhood = 3072`, `bridge = 2048`
- direction regimes: `inplane_100_no_spread = 2048`,
  `inplane_110_no_spread = 2048`, `named_mode_narrow_spread = 4096`
- nuisance regimes: `core_sharp`, `core_transition`, `core_broad`,
  `guard_band_sharp`, `guard_band_transition`, `guard_band_broad`
- TB regimes: `near_baseline = 6144`, `edge_probe = 2048`

Diagnostic raw angles and `c_axis` are excluded from this production run.

The materializer must use the external forward repository's compact round-2
RMFT projection source:

- `outputs/source/round2_projection_examples.csv`
- `outputs/source/round2_projection_summary.json`

These files stay in the forward repository. This repository consumes only the
compact projected-source metadata needed to select anchors, neighborhoods, and
bridges; it must not copy the authoritative RMFT source implementation.

The forward repository path must be explicit. Set either:

- `LNO327_FORWARD_REPO=/path/to/AR`
- or `LNO327_FORWARD_SRC=/path/to/AR/src`

The repaired P2 materializer fails fast if the RMFT projection CSV is not
available.

Current implementation note:

- role, direction, TB, and split quotas are implemented exactly;
- anchor / neighborhood / bridge rows are deterministically materialized from
  compact RMFT projection records;
- the full sampling-policy-v2 ideal pieces named in the contract, including
  scrambled Sobol continuous sampling, sensitive-region densification scoring,
  and quality-triggered bridge selection, are not yet implemented in this P2
  materializer.

This distinction is intentional: P2 may test the repaired representation and
quota plumbing, but P3 must not claim full sampling-policy-v2 coverage until
those quality-triggered pieces exist.

## Training Target

The frozen training target is:

- model family: `neural_residual_mlp_spectrum_surrogate`
- feature spec: `projected_7plus1_complex_v1`
- residual hidden width: `384`
- residual block count: `5`
- normalization: `layernorm`
- activation: `gelu`
- optimizer: `adamw`
- learning rate: `4e-4`
- weight decay: `5e-5`
- batch size: `48`
- epoch limit: `450`
- early stopping patience: `40`
- device: `auto`
- CUDA: required, with no silent CPU fallback
- ensemble policy: single production member for P2; ensemble expansion requires
  a later user-approved review decision

The width and depth are the current retained architecture. This P1 contract does
not authorize widening, adding blocks, or replacing the residual MLP family.

Representation honesty:

- dataset rows store `controls.pairing_representation` with the gauge-fixed
  projected complex 7+1 channels;
- training uses `feature_spec_id = projected_7plus1_complex_v1`, reading the
  real and imaginary parts of those stored channels;
- the external forward request still uses the stable fit-layer API with real
  `absolute_meV` pairing controls;
- therefore the full complex 7+1 block is the dataset/training representation
  and provenance, not a complex-valued forward truth input.

## Evaluation Target

Evaluation must cover validation and test splits and emit:

- held-out metrics;
- grouped error report;
- representative best / median / worst spectrum comparison plots;
- evaluation report in JSON and Markdown;
- run metadata suitable for P3 review.

Acceptance thresholds for the first review gate:

- RMSE target: `0.03`
- max absolute error target: `0.075`
- grouped warning threshold: no single primary group may exceed `2.0x` the
  global RMSE without P3 review attention

These thresholds are review gates, not automatic scientific acceptance.

## Exact Local Commands

Run these commands only in P2 after the user accepts P1:

```bash
export LNO327_FORWARD_SRC=/home/liubx25/Ni_Research/Projects/AR/src
python scripts/datasets/build_dataset.py \
  --config configs/datasets/production_surrogate_v1.dataset.json \
  --num-workers 8 \
  --force
python scripts/surrogate/train_surrogate.py \
  --config configs/training/production_surrogate_v1.training.json
python scripts/surrogate/evaluate_surrogate.py \
  --config configs/evaluation/production_surrogate_v1.evaluation.json
```

If CUDA is unavailable, training and evaluation must fail explicitly rather than
falling back to CPU.

## Expected Output Directories

- dataset: `outputs/datasets/production_surrogate_v1/`
- checkpoints: `outputs/checkpoints/production_surrogate_v1/`
- training run metadata: `outputs/runs/production_surrogate_v1/training_run_metadata.json`
- training observability: `outputs/runs/production_surrogate_v1/training_observability/`
- evaluation report directory: `outputs/runs/production_surrogate_v1/evaluation/`

## Heavy Artifacts Kept Local

Do not commit these unless a later user-approved task explicitly promotes them:

- full forward-output directories;
- bulky intermediate spectra;
- full generated dataset payloads beyond compact manifests;
- large checkpoints;
- CUDA caches, profiling output, and scratch files.

## Compact Artifacts For Review

P2 should return or keep reviewable compact artifacts:

- `outputs/datasets/production_surrogate_v1/dataset.json`
- `outputs/runs/production_surrogate_v1/dataset_run_metadata.json`
- `outputs/checkpoints/production_surrogate_v1/checkpoint.pt` only if small
  enough for review policy, otherwise keep local and return metadata only
- `outputs/checkpoints/production_surrogate_v1/metrics.json`
- `outputs/checkpoints/production_surrogate_v1/model_card.md`
- `outputs/runs/production_surrogate_v1/training_run_metadata.json`
- `outputs/runs/production_surrogate_v1/training_observability/training_history.json`
- `outputs/runs/production_surrogate_v1/training_observability/gradient_norm_summary.json`
- `outputs/runs/production_surrogate_v1/training_observability/parameter_update_summary.json`
- `outputs/runs/production_surrogate_v1/training_observability/figures/train_vs_validation_loss.png`
- `outputs/runs/production_surrogate_v1/training_observability/figures/reconstruction_vs_shape_loss.png`
- `outputs/runs/production_surrogate_v1/training_observability/figures/learning_rate_curve.png`
- `outputs/runs/production_surrogate_v1/evaluation/evaluation_report.json`
- `outputs/runs/production_surrogate_v1/evaluation/evaluation_report.md`
- `outputs/runs/production_surrogate_v1/evaluation/grouped_error_report.json`
- `outputs/runs/production_surrogate_v1/evaluation/figures/best_spectrum_comparison.png`
- `outputs/runs/production_surrogate_v1/evaluation/figures/median_spectrum_comparison.png`
- `outputs/runs/production_surrogate_v1/evaluation/figures/worst_spectrum_comparison.png`

## Review Gate

P1 freezes the contract only. P2 may run the heavy pipeline after user acceptance,
and P3 must review the compact artifacts before any scaling, capacity change,
training revision, or active-learning step is promoted.
