# Production Surrogate V1 Handoff

## Status

P1 prepares the first user-approved production-scale rectified surrogate run
contract.

This handoff is local preparation only. It must not run dataset generation,
training, or evaluation. P2 may execute the heavy run only after the user
accepts this P1 contract.

This contract supersedes Codex-proposed S9/S10 production paths. The old
`docs/formal_rectified_server_handoff.md` and
`configs/*/production/rectified_large_production_*` drafts are historical
references only, not the canonical P1 launch path.

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

## Training Target

The frozen training target is:

- model family: `neural_residual_mlp_spectrum_surrogate`
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
  --num-workers 8
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
