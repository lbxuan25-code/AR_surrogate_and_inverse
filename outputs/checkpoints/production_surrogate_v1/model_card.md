# Production Surrogate V1 Residual Checkpoint

## Purpose

First user-approved production-scale rectified residual surrogate run.
This run uses the frozen S1-S8 representation, sampling, observability, and model-capacity decisions.

## Model

- Type: `neural_residual_mlp_spectrum_surrogate`
- Checkpoint: `outputs/checkpoints/production_surrogate_v1/model.pt`
- Feature order: `delta_zz_s, delta_xx_s, delta_zx_d, delta_perp_z, delta_perp_x, delta_zz_d, delta_xx_d, delta_zx_s, direction_inplane_100, direction_inplane_110, direction_named_mode, direction_diagnostic_raw_angle, direction_has_spread, direction_spread_half_width, direction_spread_num_samples, direction_raw_interface_angle, barrier_z, gamma, temperature_kelvin, nk`
- Residual hidden width: `384`
- Residual blocks: `5`
- Normalization: `layernorm`
- Activation: `gelu`
- Optimizer: `adamw`
- Learning rate: `0.0004`
- Weight decay: `5e-05`
- Batch size: `48`
- Epoch limit: `450`
- Best epoch: `126`
- Early-stopping patience: `40`
- Random seed: `1103`
- Requested device: `auto`
- Resolved device: `cuda`
- Loss kind: `weighted_mse_plus_first_difference`
- Reconstruction weight: `1.0`
- Shape weight: `0.15`
- Bias weighting: `{'kind': 'center_window', 'outer_weight': 1.0, 'central_weight': 2.5, 'central_bias_half_width_mev': 6.0}`

## Dataset

- Dataset id: `production_surrogate_v1`
- Manifest: `outputs/datasets/production_surrogate_v1/dataset.json`
- Sampling policy id: `quality_first_rmft_sampling_v2`
- Rows: `8192`
- Splits: `test, train, validation`
- Direction regimes: `{'inplane_100_no_spread': 2736, 'inplane_110_no_spread': 2736, 'named_mode_narrow_spread': 2720}`

## Direction Support

- Supported named modes: `inplane_100`, `inplane_110`.
- `c_axis` is unsupported and is not a valid inverse target.
- Generic raw angles are diagnostic-only and are not primary truth-grade training data.
- Directional spread is represented only as narrow named-mode-centered spread.
- Dataset direction support summary: `{'direction_regime_counts': {'inplane_100_no_spread': 2736, 'inplane_110_no_spread': 2736, 'named_mode_narrow_spread': 2720}, 'direction_modes': ['inplane_100', 'inplane_110'], 'legacy_angle_only_rows': 0, 'diagnostic_raw_angle_rows': 0}`

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

- Rows: `6144`
- MAE: `0.00057395447`
- RMSE: `0.00085369156`
- Max absolute error: `0.0068760258`

### validation

- Rows: `1024`
- MAE: `0.00058209424`
- RMSE: `0.00086667121`
- Max absolute error: `0.0060407599`

### test

- Rows: `1024`
- MAE: `0.00058209424`
- RMSE: `0.00086667121`
- Max absolute error: `0.0060407599`

## Limitations

Prepared by P1 and executed only in P2 after user acceptance.
The architecture is intentionally unchanged under the S7 decision rule.
Active learning is deferred until after production v1 review.
