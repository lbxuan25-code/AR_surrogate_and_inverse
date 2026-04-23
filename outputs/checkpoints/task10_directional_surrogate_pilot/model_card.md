# Task 10 Directional Surrogate Pilot Checkpoint

## Purpose

Small non-smoke direction-aware pilot checkpoint mapping fit-layer, direction, and transport controls to AR conductance spectra.
This is the Task 10 pilot artifact prepared for server execution review, not the Task 9 smoke-loop artifact and not a server-scale production run.

## Model

- Type: ridge-linear spectrum surrogate
- Ridge alpha: `1e-06`
- Checkpoint: `outputs/checkpoints/task10_directional_surrogate_pilot/model.npz`
- Feature order: `delta_zz_s, delta_xx_s, delta_zx_d, delta_perp_z, delta_perp_x, delta_zz_d, delta_xx_d, delta_zx_s, direction_inplane_100, direction_inplane_110, direction_named_mode, direction_diagnostic_raw_angle, direction_has_spread, direction_spread_half_width, direction_spread_num_samples, direction_raw_interface_angle, barrier_z, gamma, temperature_kelvin, nk`

## Dataset

- Dataset id: `task10_directional_pilot_v1`
- Manifest: `outputs/datasets/task10_directional_pilot/dataset.json`
- Sampling policy id: `task10_directional_pilot_v1`
- Rows: `12`
- Splits: `test, train, validation`
- Direction regimes: `{'inplane_100_no_spread': 4, 'inplane_110_no_spread': 3, 'named_mode_narrow_spread': 5}`

## Direction Support

- Supported named modes: `inplane_100`, `inplane_110`.
- `c_axis` is unsupported and is not a valid inverse target.
- Generic raw angles are diagnostic-only and are not primary truth-grade training data.
- Directional spread is represented only as narrow named-mode-centered spread.
- Dataset direction support summary: `{'direction_regime_counts': {'inplane_100_no_spread': 4, 'inplane_110_no_spread': 3, 'named_mode_narrow_spread': 5}, 'direction_modes': ['inplane_100', 'inplane_110'], 'legacy_angle_only_rows': 0, 'diagnostic_raw_angle_rows': 0}`

## Forward Metadata Family

- forward_interface_version: `ar_forward_v1`
- output_schema_version: `ar_forward_output_v1`
- pairing_convention_id: `round2_physical_channels_task_h_fit_layer_v1`
- formal_baseline_record: `outputs/source/round2_baseline_selection.json`
- formal_baseline_selection_rule: `temperature sweep RMFT pairing data, charge-balanced p≈0 branch, temperature_eV <= 1.0e-3, first 8 samples sorted by temperature`
- git_commit: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`
- git_dirty: `True`

## Metrics

### train

- Rows: `8`
- MAE: `1.3192379e-08`
- RMSE: `1.8286688e-08`
- Max absolute error: `4.5451581e-08`

### validation

- Rows: `2`
- MAE: `0.041043448`
- RMSE: `0.061240052`
- Max absolute error: `0.13352574`

### test

- Rows: `2`
- MAE: `0.11645278`
- RMSE: `0.15696452`
- Max absolute error: `0.30716892`

## Limitations

This checkpoint is trained on the Task 10 directional pilot dataset and remains a compact pilot artifact.
It verifies direction-aware feature intake, checkpointing, metrics, and returned-artifact review under the split local-edit and server-run workflow.
Production-scale dataset generation and training belong to later tasks.
