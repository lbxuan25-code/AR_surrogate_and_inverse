# Task 12 Directional Neural Medium-Scale Checkpoint

## Purpose

Medium-scale direction-aware neural checkpoint mapping fit-layer, direction, and transport controls to full AR conductance spectra.
This is the canonical Task 12 neural validation config prepared for server execution and local artifact review.

## Model

- Type: `neural_mlp_spectrum_surrogate`
- Checkpoint: `outputs/checkpoints/task12_directional_neural_medium/model.pt`
- Feature order: `delta_zz_s, delta_xx_s, delta_zx_d, delta_perp_z, delta_perp_x, delta_zz_d, delta_xx_d, delta_zx_s, direction_inplane_100, direction_inplane_110, direction_named_mode, direction_diagnostic_raw_angle, direction_has_spread, direction_spread_half_width, direction_spread_num_samples, direction_raw_interface_angle, barrier_z, gamma, temperature_kelvin, nk`
- Hidden layer widths: `[256, 256, 128]`
- Depth: `3`
- Activation: `gelu`
- Optimizer: `adamw`
- Learning rate: `0.0005`
- Batch size: `32`
- Epoch limit: `250`
- Best epoch: `230`
- Early-stopping patience: `25`
- Random seed: `1201`
- Requested device: `auto`
- Resolved device: `cuda`

## Dataset

- Dataset id: `task12_directional_medium_neural_v1`
- Manifest: `outputs/datasets/task12_directional_medium_neural/dataset.json`
- Sampling policy id: `task12_directional_medium_neural_v1`
- Rows: `352`
- Splits: `test, train, validation`
- Direction regimes: `{'inplane_100_no_spread': 88, 'inplane_110_no_spread': 88, 'named_mode_narrow_spread': 176}`

## Direction Support

- Supported named modes: `inplane_100`, `inplane_110`.
- `c_axis` is unsupported and is not a valid inverse target.
- Generic raw angles are diagnostic-only and are not primary truth-grade training data.
- Directional spread is represented only as narrow named-mode-centered spread.
- Dataset direction support summary: `{'direction_regime_counts': {'inplane_100_no_spread': 88, 'inplane_110_no_spread': 88, 'named_mode_narrow_spread': 176}, 'direction_modes': ['inplane_100', 'inplane_110'], 'legacy_angle_only_rows': 0, 'diagnostic_raw_angle_rows': 0}`

## Forward Metadata Family

- forward_interface_version: `ar_forward_v1`
- output_schema_version: `ar_forward_output_v1`
- pairing_convention_id: `round2_physical_channels_task_h_fit_layer_v1`
- formal_baseline_record: `outputs/source/round2_baseline_selection.json`
- formal_baseline_selection_rule: `temperature sweep RMFT pairing data, charge-balanced p≈0 branch, temperature_eV <= 1.0e-3, first 8 samples sorted by temperature`
- git_commit: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`
- git_dirty: `False`

## Metrics

### train

- Rows: `256`
- MAE: `0.00064193169`
- RMSE: `0.00096658435`
- Max absolute error: `0.0064005313`

### validation

- Rows: `48`
- MAE: `0.0012909128`
- RMSE: `0.0019946991`
- Max absolute error: `0.0083986808`

### test

- Rows: `48`
- MAE: `0.0025107833`
- RMSE: `0.0037953593`
- Max absolute error: `0.014530783`

## Limitations

This Task 12 neural checkpoint must be generated on the server from the frozen Task 12 medium-scale dataset contract.
It remains limited to supported named in-plane modes and narrow named-mode-centered spread only under the frozen forward metadata family.
Returned medium-scale artifacts must be reviewed locally before any later large-scale contract is accepted.
