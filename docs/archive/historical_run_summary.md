# Historical Run Summary

This archive note preserves the compact facts needed from pre-production
historical runs after bulky generated artifacts were removed from version
control.

The current `production_surrogate_v1` run is not summarized here and is not part
of this cleanup. Its artifacts remain intact for P3 review.

## Cleanup Scope

The cleanup keeps canonical configs, runbooks, compact metrics, model cards,
dataset manifests, run metadata, and review reports where they remain useful.

The cleanup removes:

- Python bytecode caches;
- obsolete Codex-proposed S9/S10 production draft files superseded by the
  user-approved P1/P2/P3 sequence;
- old evaluation logs and rerun backup files;
- bulky historical forward-output payload directories where compact manifests
  and metrics are enough for archive review;
- historical checkpoints that are not needed for current P2/P3 review.

## Pre-S7 Local Observation

- Dataset: `outputs/datasets/pre_s7_local_observation/dataset.json`
- Dataset id: `pre_s7_local_observation_v1`
- Rows: `96`
- Sampling policy: `pre_s7_local_observation_v1`
- Model: `neural_residual_mlp_spectrum_surrogate`
- Train rows: `72`
- Validation rows: `12`
- Test rows: `12`
- Best epoch: `76`
- Epochs completed: `96`
- Best validation loss: `0.007727396208792925`
- Train RMSE: `0.011731443864854512`
- Validation RMSE: `0.011652447554180542`
- Test RMSE: `0.016295038864328214`
- Gradient warning flags: `[]`

Archive action:

- Kept compact metrics, model card, run metadata, observability summaries,
  evaluation report, grouped error report, and representative figures.
- Removed bulky forward-output payloads and the historical `model.pt`
  checkpoint.

## Task 10 Directional Pilot

- Dataset: `outputs/datasets/task10_directional_pilot/dataset.json`
- Dataset id: `task10_directional_pilot_v1`
- Rows: `12`
- Sampling policy: `task10_directional_pilot_v1`
- Model: `ridge_linear_spectrum_surrogate`
- Train rows: `8`
- Validation rows: `2`
- Test rows: `2`
- Train RMSE: `1.828668825840408e-08`
- Validation RMSE: `0.06124005202355962`
- Test RMSE: `0.15696451545109708`

Archive action:

- Kept compact dataset, checkpoint, metrics, model card, run metadata, and
  evaluation reports because the total artifact size is small.

## Task 11 Directional Production

- Dataset: `outputs/datasets/task11_directional_production/dataset.json`
- Dataset id: `task11_directional_production_v1`
- Rows: `20`
- Sampling policy: `task11_directional_production_v1`
- Model: `ridge_linear_spectrum_surrogate`
- Train rows: `12`
- Validation rows: `4`
- Test rows: `4`
- Train RMSE: `2.8282872134455465e-07`
- Validation RMSE: `0.07010289669742924`
- Test RMSE: `0.08521293032043196`

Archive action:

- Kept compact dataset, checkpoint, metrics, model card, run metadata, and
  evaluation reports because the total artifact size is small.

## Task 12 Directional Neural Medium

- Dataset: `outputs/datasets/task12_directional_medium_neural/dataset.json`
- Dataset id: `task12_directional_medium_neural_v1`
- Rows: `352`
- Sampling policy: `task12_directional_medium_neural_v1`
- Model: `neural_mlp_spectrum_surrogate`
- Train rows: `256`
- Validation rows: `48`
- Test rows: `48`
- Best epoch: `230`
- Epochs completed: `250`
- Best validation loss: `0.0006306761060841382`
- Train RMSE: `0.0009665843529719311`
- Validation RMSE: `0.001994699147843048`
- Test RMSE: `0.0037953593037222916`

Archive action:

- Kept compact dataset manifest, checkpoint, metrics, model card, run metadata,
  and evaluation reports.
- Removed bulky forward-output payloads.

## Task 13 Directional High Accuracy

- Dataset: `outputs/datasets/task13_directional_large_accuracy/dataset.json`
- Dataset id: `task13_directional_large_accuracy_v1`
- Rows: `4096`
- Sampling policy: `task13_directional_large_accuracy_v1`
- Model: `neural_residual_mlp_spectrum_surrogate`
- Train rows: `3072`
- Validation rows: `512`
- Test rows: `512`
- Best epoch: `96`
- Epochs completed: `136`
- Best validation loss: `0.00014574904344044626`
- Train RMSE: `0.0008713884118444987`
- Validation RMSE: `0.001186995056943268`
- Test RMSE: `0.0010833164463790272`

Archive action:

- Kept compact dataset manifest, ensemble manifest, metrics, model card, run
  metadata, and evaluation report.
- Removed bulky forward-output payloads, ensemble member checkpoints, old
  evaluation logs, and obsolete rerun backup JSON.

## Superseded S9/S10 Draft

Codex-proposed S9/S10 files were superseded by the user-approved P1/P2/P3
sequence and the canonical production surrogate v1 contract.

Archive action:

- Removed the obsolete formal rectified server handoff, rectified-large
  production draft configs, and their lightweight contract test.
