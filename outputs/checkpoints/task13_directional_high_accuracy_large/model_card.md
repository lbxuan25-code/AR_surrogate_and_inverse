# Task 13 Directional High-Accuracy Large-Scale Checkpoint

## Purpose

Large-scale direction-aware high-accuracy residual surrogate mapping fit-layer, direction, and transport controls to full AR conductance spectra.
This Task 13 contract upgrades the neural stack beyond the Task 12 plain-MLP comparator while preserving the same feature and output spectrum meanings.

## Model

- Type: `neural_residual_mlp_spectrum_surrogate`
- Checkpoint: `outputs/checkpoints/task13_directional_high_accuracy_large/ensemble_manifest.json`
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
- Best epoch: `96`
- Early-stopping patience: `40`
- Random seed: `1103`
- Requested device: `auto`
- Resolved device: `cuda`
- Loss kind: `weighted_mse_plus_first_difference`
- Reconstruction weight: `1.0`
- Shape weight: `0.15`
- Bias weighting: `{'kind': 'center_window', 'outer_weight': 1.0, 'central_weight': 2.5, 'central_bias_half_width_mev': 4.0}`
- Ensemble enabled: `True`
- Ensemble seeds: `[1103, 2207, 3301]`
- Ensemble aggregation: `mean`
- Ensemble disagreement summary: `per_spectrum_mean_std_and_max_std`

## Dataset

- Dataset id: `task13_directional_large_accuracy_v1`
- Manifest: `outputs/datasets/task13_directional_large_accuracy/dataset.json`
- Sampling policy id: `task13_directional_large_accuracy_v1`
- Rows: `4096`
- Splits: `test, train, validation`
- Direction regimes: `{'inplane_100_no_spread': 1024, 'inplane_110_no_spread': 1024, 'named_mode_narrow_spread': 2048}`

## Direction Support

- Supported named modes: `inplane_100`, `inplane_110`.
- `c_axis` is unsupported and is not a valid inverse target.
- Generic raw angles are diagnostic-only and are not primary truth-grade training data.
- Directional spread is represented only as narrow named-mode-centered spread.
- Dataset direction support summary: `{'direction_regime_counts': {'inplane_100_no_spread': 1024, 'inplane_110_no_spread': 1024, 'named_mode_narrow_spread': 2048}, 'direction_modes': ['inplane_100', 'inplane_110'], 'legacy_angle_only_rows': 0, 'diagnostic_raw_angle_rows': 0}`

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

- Rows: `3072`
- MAE: `0.0005759212`
- RMSE: `0.00087138841`
- Max absolute error: `0.0053436289`

### validation

- Rows: `512`
- MAE: `0.0007032051`
- RMSE: `0.0011869951`
- Max absolute error: `0.0079531448`

### test

- Rows: `512`
- MAE: `0.00067934207`
- RMSE: `0.0010833164`
- Max absolute error: `0.0058160014`

## Limitations

This Task 13 high-accuracy checkpoint must be generated on the server from the frozen Task 13 large-scale dataset contract.
It remains limited to supported named in-plane modes and narrow named-mode-centered spread only under the frozen forward metadata family.
Task 13B accepted fixed disagreement-trigger fallback thresholds of `mean_std = 0.005` and `max_std = 0.025`; held-out rows above either threshold require direct forward scoring.
Final inverse candidates still require direct forward recheck even when surrogate error and ensemble disagreement stay below these thresholds.
