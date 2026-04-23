# Task 11 Directional Surrogate Production Evaluation

## Summary

- Model: `outputs/checkpoints/task11_directional_surrogate_production/model.npz`
- Dataset: `outputs/datasets/task11_directional_production/dataset.json`
- Held-out splits: `validation, test`
- Safe RMSE threshold: `0.05`
- Safe max-error threshold: `0.1`
- Unsafe regimes: `2`

## Calibration Diagnostics

- Held-out rows: `8`
- Mean RMSE: `0.064617814`
- Max RMSE: `0.14304342`
- Mean max absolute error: `0.12422916`
- Unsafe fraction: `0.625`

## Transport Regimes

### low_barrier|low_gamma|high_temp

- Rows: `2`
- Mean RMSE: `0.10415659`
- Max RMSE: `0.14304342`
- Max absolute error: `0.27724792`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task11_prod_validation_inplane_100_core, task11_prod_test_inplane_100_core`

### high_barrier|high_gamma|high_temp

- Rows: `4`
- Mean RMSE: `0.072472844`
- Max RMSE: `0.10042079`
- Max absolute error: `0.19370092`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task11_prod_validation_inplane_110_core, task11_prod_validation_inplane_100_spread, task11_prod_test_inplane_110_core`

### high_barrier|low_gamma|high_temp

- Rows: `2`
- Mean RMSE: `0.0093689736`
- Max RMSE: `0.013375228`
- Max absolute error: `0.025926136`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

## Direction Regimes

### inplane_100_no_spread

- Rows: `2`
- Mean RMSE: `0.10415659`
- Max RMSE: `0.14304342`
- Max absolute error: `0.27724792`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task11_prod_validation_inplane_100_core, task11_prod_test_inplane_100_core`

### inplane_110_no_spread

- Rows: `2`
- Mean RMSE: `0.093870261`
- Max RMSE: `0.10042079`
- Max absolute error: `0.19370092`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task11_prod_validation_inplane_110_core, task11_prod_test_inplane_110_core`

### named_mode_narrow_spread

- Rows: `4`
- Mean RMSE: `0.030222201`
- Max RMSE: `0.071653958`
- Max absolute error: `0.13769295`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task11_prod_validation_inplane_100_spread`

## Fallback Policy

Surrogate acceleration is disabled for unsafe transport regimes. Inverse workflows must use direct external forward calls there.

For unsafe regimes, inverse workflows must call the external forward
interface directly for candidate scoring or final rechecks.
