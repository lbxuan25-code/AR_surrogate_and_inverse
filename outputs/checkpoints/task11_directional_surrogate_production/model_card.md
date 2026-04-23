# Task 11 Directional Surrogate Production Checkpoint

## Purpose

Production-contract direction-aware checkpoint mapping fit-layer, direction, and transport controls to AR conductance spectra.
This is the Task 11 production contract artifact prepared for server execution, not the Task 10 pilot checkpoint and not yet a returned production run result.

## Model

- Type: ridge-linear spectrum surrogate
- Ridge alpha: `1e-06`
- Checkpoint: `outputs/checkpoints/task11_directional_surrogate_production/model.npz`
- Feature order: `delta_zz_s, delta_xx_s, delta_zx_d, delta_perp_z, delta_perp_x, delta_zz_d, delta_xx_d, delta_zx_s, direction_inplane_100, direction_inplane_110, direction_named_mode, direction_diagnostic_raw_angle, direction_has_spread, direction_spread_half_width, direction_spread_num_samples, direction_raw_interface_angle, barrier_z, gamma, temperature_kelvin, nk`

## Dataset

- Dataset id: `task11_directional_production_v1`
- Manifest: `outputs/datasets/task11_directional_production/dataset.json`
- Sampling policy id: `task11_directional_production_v1`
- Rows: `20`
- Splits: `test, train, validation`
- Direction regimes: `{'inplane_100_no_spread': 6, 'inplane_110_no_spread': 6, 'named_mode_narrow_spread': 8}`

## Direction Support

- Supported named modes: `inplane_100`, `inplane_110`.
- `c_axis` is unsupported and is not a valid inverse target.
- Generic raw angles are diagnostic-only and are not primary truth-grade training data.
- Directional spread is represented only as narrow named-mode-centered spread.
- Dataset direction support summary: `{'direction_regime_counts': {'inplane_100_no_spread': 6, 'inplane_110_no_spread': 6, 'named_mode_narrow_spread': 8}, 'direction_modes': ['inplane_100', 'inplane_110'], 'legacy_angle_only_rows': 0, 'diagnostic_raw_angle_rows': 0}`

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

- Rows: `12`
- MAE: `1.8449399e-07`
- RMSE: `2.8282872e-07`
- Max absolute error: `1.0347287e-06`

### validation

- Rows: `4`
- MAE: `0.048650964`
- RMSE: `0.070102897`
- Max absolute error: `0.19370092`

### test

- Rows: `4`
- MAE: `0.050770358`
- RMSE: `0.08521293`
- Max absolute error: `0.27724792`

## Limitations

This checkpoint config targets the Task 11 production dataset contract and should only be generated on the server.
It is limited to supported named in-plane modes and narrow named-mode-centered spread under the frozen forward metadata family documented in the Task 11 contract.
Returned production artifacts must be reviewed locally before Task 11 can be accepted.
