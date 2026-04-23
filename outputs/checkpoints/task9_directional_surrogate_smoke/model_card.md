# Task 9 Directional Surrogate Smoke Checkpoint

## Purpose

Smoke-scale direction-aware checkpoint mapping fit-layer, direction, and transport controls to AR conductance spectra.
This is a naming-clean smoke artifact and not the formal large Task 9 surrogate training run.

## Model

- Type: ridge-linear spectrum surrogate
- Ridge alpha: `1e-06`
- Checkpoint: `outputs/checkpoints/task9_directional_surrogate_smoke/model.npz`
- Feature order: `delta_zz_s, delta_xx_s, delta_zx_d, delta_perp_z, delta_perp_x, delta_zz_d, delta_xx_d, delta_zx_s, direction_inplane_100, direction_inplane_110, direction_named_mode, direction_diagnostic_raw_angle, direction_has_spread, direction_spread_half_width, direction_spread_num_samples, direction_raw_interface_angle, barrier_z, gamma, temperature_kelvin, nk`

## Dataset

- Dataset id: `task8_directional_smoke_v1`
- Manifest: `outputs/datasets/task8_directional_smoke/dataset.json`
- Sampling policy id: `directional_fit_layer_transport_smoke_v1`
- Rows: `3`
- Splits: `test, train, validation`
- Direction regimes: `{'inplane_100_no_spread': 1, 'inplane_110_no_spread': 1, 'named_mode_narrow_spread': 1}`

## Direction Support

- Supported named modes: `inplane_100`, `inplane_110`.
- `c_axis` is unsupported and is not a valid inverse target.
- Generic raw angles are diagnostic-only and are not primary truth-grade training data.
- Directional spread is represented only as narrow named-mode-centered spread.
- Dataset direction support summary: `{'direction_regime_counts': {'inplane_100_no_spread': 1, 'inplane_110_no_spread': 1, 'named_mode_narrow_spread': 1}, 'direction_modes': ['inplane_100', 'inplane_110'], 'legacy_angle_only_rows': 0, 'diagnostic_raw_angle_rows': 0}`

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

- Rows: `1`
- MAE: `0`
- RMSE: `0`
- Max absolute error: `0`

### validation

- Rows: `1`
- MAE: `0.076728554`
- RMSE: `0.094277379`
- Max absolute error: `0.13597491`

### test

- Rows: `1`
- MAE: `0.16258977`
- RMSE: `0.2001587`
- Max absolute error: `0.29266713`

## Limitations

This checkpoint is trained on the tiny Task 8 directional smoke dataset and is intended only
to verify direction-aware feature intake, checkpointing, metrics, and dataset metadata plumbing.
The formal non-smoke Task 9 training expansion has not been run by this artifact.
