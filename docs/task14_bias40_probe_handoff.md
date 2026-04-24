# Task 14 Bias40 Probe Handoff

Task 14C prepares the canonical widened-bias probe contract only.
Do not generate the bias40 dataset, run the bias40 training, or run the bias40
evaluation in the local Codex workspace.

The later manual server task must use the exact files frozen here.

## Canonical Configs

- Dataset config: `configs/datasets/task14_bias40_probe_dataset.json`
- Training config: `configs/surrogate/task14_bias40_probe_training.json`
- Evaluation config: `configs/surrogate/task14_bias40_probe_evaluation.json`

## Probe Intent

This probe changes one primary axis only:

- widen the bias window from `[-20, 20] meV` to `[-40, 40] meV`
- increase the spectrum grid from `121` to `241` bias points

This probe is intended to hold the following contracts fixed while bias is
widened:

- the canonical Task 14 gauge-fixed projected 7+1 pairing representation
- the current supported direction contract
- the current pre-14D nuisance-domain sweep
- fixed `nk = 41`

## Canonical Pairing Contract

The later server probe must preserve:

- `pairing_representation_version = projected_7plus1_gauge_fixed_v1`
- storage under `controls.pairing_representation`
- only one removed global phase redundancy
- no PCA or latent compression after the projected 7+1 channels are formed

## Probe Bias Contract

The later server probe must use exactly:

- `bias_min_mev = -40.0`
- `bias_max_mev = 40.0`
- `num_bias = 241`

The probe is out of contract if a different bias window is used.

## Later Manual Server Commands

When the later server task is promoted, run from the repository root:

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task14_bias40_probe_dataset.json
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task14_bias40_probe_training.json
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task14_bias40_probe_evaluation.json
```

## Expected Output Paths

- `outputs/datasets/task14_bias40_probe/dataset.json`
- `outputs/runs/task14_bias40_probe_dataset_run_metadata.json`
- `outputs/checkpoints/task14_bias40_probe/ensemble_manifest.json`
- `outputs/checkpoints/task14_bias40_probe/metrics.json`
- `outputs/checkpoints/task14_bias40_probe/model_card.md`
- `outputs/runs/task14_bias40_probe_training_run_metadata.json`
- `outputs/runs/task14_bias40_probe_evaluation/evaluation_report.json`
- `outputs/runs/task14_bias40_probe_evaluation/evaluation_report.md`
- `outputs/runs/task14_bias40_probe_evaluation_run_metadata.json`

## Review Boundary

Task 14C is not the later server run.
It is complete only as a local preparation step that freezes the bias40 probe
contract and the later handoff instructions.
