# Pre-S7 Local Training Runbook

This runbook defines the local observation run that must happen before Task S7
freezes any model-capacity decision rules.

This run does not complete Task S7.
It exists only to produce real optimization and held-out observability artifacts
for the later S7 diagnosis.

## Historical Artifact Availability

The original pre-S7 checkpoint was removed from the repository after its
compact metrics, model card, observability curves, grouped evaluation report,
and representative comparison figures were retained and summarized in
`docs/archive/historical_run_summary.md`.

This runbook remains useful as a reproducible historical contract. To evaluate
it again, regenerate the local dataset if needed and rerun the training command
before using the evaluation config.

## Config Files

- dataset config:
  `configs/datasets/local/pre_s7_local_observation_dataset.json`
- training config:
  `configs/surrogate/local/pre_s7_local_observation_training.json`
- evaluation config:
  `configs/surrogate/local/pre_s7_local_observation_evaluation.json`

## Forward Dependency

The external forward repository must be available through:

```bash
export LNO327_FORWARD_SRC=/home/liubx25/Ni_Research/Projects/AR/src
```

## Dataset Generation

Default worker count for this local run: `8`

```bash
export LNO327_FORWARD_SRC=/home/liubx25/Ni_Research/Projects/AR/src
python scripts/datasets/build_dataset.py \
  --config configs/datasets/local/pre_s7_local_observation_dataset.json \
  --num-workers 8
```

Expected dataset outputs:

- `outputs/datasets/pre_s7_local_observation/dataset.json`
- `outputs/runs/pre_s7_local_observation/dataset_run_metadata.json`

## Training

Training must require CUDA.
If CUDA is not available, the run must fail explicitly instead of silently
falling back to CPU.

```bash
python scripts/surrogate/train_surrogate.py \
  --config configs/surrogate/local/pre_s7_local_observation_training.json
```

Expected training outputs:

- checkpoint:
  `outputs/checkpoints/pre_s7_local_observation/model.pt`
  (not retained in the cleaned repository)
- metrics:
  `outputs/checkpoints/pre_s7_local_observation/metrics.json`
- model card:
  `outputs/checkpoints/pre_s7_local_observation/model_card.md`
- run metadata:
  `outputs/runs/pre_s7_local_observation/training_run_metadata.json`
- observability directory:
  `outputs/runs/pre_s7_local_observation/training_observability/`

Mandatory training observability artifacts:

- `training_history.json`
- `gradient_norm_summary.json`
- `parameter_update_summary.json`
- `figures/train_vs_validation_loss.png`
- `figures/reconstruction_vs_shape_loss.png`
- `figures/learning_rate_curve.png`

## Evaluation

```bash
python scripts/surrogate/evaluate_surrogate.py \
  --config configs/surrogate/local/pre_s7_local_observation_evaluation.json
```

Expected evaluation outputs:

- report directory:
  `outputs/runs/pre_s7_local_observation/evaluation/`
- grouped error report:
  `outputs/runs/pre_s7_local_observation/evaluation/grouped_error_report.json`
- representative plots:
  `outputs/runs/pre_s7_local_observation/evaluation/figures/best_spectrum_comparison.png`
  `outputs/runs/pre_s7_local_observation/evaluation/figures/median_spectrum_comparison.png`
  `outputs/runs/pre_s7_local_observation/evaluation/figures/worst_spectrum_comparison.png`

## What To Inspect First For S7

Inspect these in order:

1. `training_observability/figures/train_vs_validation_loss.png`
2. `training_observability/figures/reconstruction_vs_shape_loss.png`
3. `training_observability/gradient_norm_summary.json`
4. `training_observability/parameter_update_summary.json`
5. `evaluation/grouped_error_report.json`
6. `evaluation/figures/best_spectrum_comparison.png`
7. `evaluation/figures/median_spectrum_comparison.png`
8. `evaluation/figures/worst_spectrum_comparison.png`

The first S7 question is not "should we widen the model?".
The first S7 question is whether these artifacts show underfitting,
overfitting, optimization instability, or regime-specific failure under the
current residual family.
