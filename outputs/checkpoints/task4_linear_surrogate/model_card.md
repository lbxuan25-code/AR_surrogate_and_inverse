# Task 4 Linear Surrogate Baseline

## Purpose

First lightweight baseline mapping fit-layer and transport controls to AR conductance spectra.
This is a smoke-scale model, not a calibrated inverse-search surrogate.

## Model

- Type: ridge-linear spectrum surrogate
- Ridge alpha: `1e-06`
- Checkpoint: `outputs/checkpoints/task4_linear_surrogate/model.npz`
- Feature order: `delta_zz_s, delta_xx_s, delta_zx_d, delta_perp_z, delta_perp_x, delta_zz_d, delta_xx_d, delta_zx_s, interface_angle, barrier_z, gamma, temperature_kelvin, nk`

## Dataset

- Dataset id: `task3_orchestration_smoke_v1`
- Manifest: `outputs/datasets/task3_orchestration_smoke/dataset.json`
- Sampling policy id: `fit_layer_transport_smoke_v1`
- Rows: `3`
- Splits: `test, train, validation`

## Forward Metadata Family

- forward_interface_version: `ar_forward_v1`
- output_schema_version: `ar_forward_output_v1`
- pairing_convention_id: `round2_physical_channels_task_h_fit_layer_v1`
- formal_baseline_record: `outputs/source/round2_baseline_selection.json`
- formal_baseline_selection_rule: `temperature sweep RMFT pairing data, charge-balanced p≈0 branch, temperature_eV <= 1.0e-3, first 8 samples sorted by temperature`
- git_commit: `4e4c935d1f123c03ee2250f8624d5df3c2c7ebe3`
- git_dirty: `False`

## Metrics

### train

- Rows: `1`
- MAE: `0`
- RMSE: `0`
- Max absolute error: `0`

### validation

- Rows: `1`
- MAE: `0.085753342`
- RMSE: `0.098413207`
- Max absolute error: `0.14850668`

### test

- Rows: `1`
- MAE: `0.16279561`
- RMSE: `0.19309576`
- Max absolute error: `0.30883826`

## Limitations

This baseline is trained on the tiny Task 3 smoke dataset and is intended only
to verify training, checkpointing, metrics, and dataset metadata plumbing.
Calibration and unsafe-regime analysis belong to Task 5.
