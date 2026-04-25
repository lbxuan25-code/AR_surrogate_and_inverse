# Pre-S7 Local Observation Residual Checkpoint

## Purpose

Local pre-S7 residual surrogate run for collecting real optimization and held-out observability before writing model-capacity decision rules.
This run intentionally reuses the current residual MLP family without changing width or block count.

## Model

- Type: `neural_residual_mlp_spectrum_surrogate`
- Checkpoint: `outputs/checkpoints/pre_s7_local_observation/model.pt`
- Feature order: `delta_zz_s, delta_xx_s, delta_zx_d, delta_perp_z, delta_perp_x, delta_zz_d, delta_xx_d, delta_zx_s, direction_inplane_100, direction_inplane_110, direction_named_mode, direction_diagnostic_raw_angle, direction_has_spread, direction_spread_half_width, direction_spread_num_samples, direction_raw_interface_angle, barrier_z, gamma, temperature_kelvin, nk`
- Residual hidden width: `384`
- Residual blocks: `5`
- Normalization: `layernorm`
- Activation: `gelu`
- Optimizer: `adamw`
- Learning rate: `0.0004`
- Weight decay: `5e-05`
- Batch size: `24`
- Epoch limit: `120`
- Best epoch: `76`
- Early-stopping patience: `20`
- Random seed: `1403`
- Requested device: `auto`
- Resolved device: `cuda`
- Loss kind: `weighted_mse_plus_first_difference`
- Reconstruction weight: `1.0`
- Shape weight: `0.15`
- Bias weighting: `{'kind': 'center_window', 'outer_weight': 1.0, 'central_weight': 2.5, 'central_bias_half_width_mev': 6.0}`

## Dataset

- Dataset id: `pre_s7_local_observation_v1`
- Manifest: `outputs/datasets/pre_s7_local_observation/dataset.json`
- Sampling policy id: `pre_s7_local_observation_v1`
- Rows: `96`
- Splits: `test, train, validation`
- Direction regimes: `{'inplane_100_no_spread': 24, 'inplane_110_no_spread': 24, 'named_mode_narrow_spread': 48}`

## Direction Support

- Supported named modes: `inplane_100`, `inplane_110`.
- `c_axis` is unsupported and is not a valid inverse target.
- Generic raw angles are diagnostic-only and are not primary truth-grade training data.
- Directional spread is represented only as narrow named-mode-centered spread.
- Dataset direction support summary: `{'direction_regime_counts': {'inplane_100_no_spread': 24, 'inplane_110_no_spread': 24, 'named_mode_narrow_spread': 48}, 'direction_modes': ['inplane_100', 'inplane_110'], 'legacy_angle_only_rows': 0, 'diagnostic_raw_angle_rows': 0}`

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

- Rows: `72`
- MAE: `0.0070388884`
- RMSE: `0.011731444`
- Max absolute error: `0.063957137`

### validation

- Rows: `12`
- MAE: `0.0077249006`
- RMSE: `0.011652448`
- Max absolute error: `0.064271368`

### test

- Rows: `12`
- MAE: `0.010871623`
- RMSE: `0.016295039`
- Max absolute error: `0.072215043`

## Limitations

This is a local observation run, not a promotion-quality training campaign.
Its purpose is to expose optimization and grouped-error behavior before Task S7 decides whether capacity changes are justified.
TB variation is not yet implemented in the local forward/training path, so TB grouped reporting is intentionally marked as tb_unimplemented_local.
