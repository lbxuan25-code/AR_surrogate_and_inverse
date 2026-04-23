# Task 10 Directional Surrogate Pilot Evaluation

## Summary

- Model: `outputs/checkpoints/task10_directional_surrogate_pilot/model.npz`
- Dataset: `outputs/datasets/task10_directional_pilot/dataset.json`
- Held-out splits: `validation, test`
- Safe RMSE threshold: `0.05`
- Safe max-error threshold: `0.1`
- Unsafe regimes: `3`

## Calibration Diagnostics

- Held-out rows: `4`
- Mean RMSE: `0.097481697`
- Max RMSE: `0.2071187`
- Mean max absolute error: `0.14963053`
- Unsafe fraction: `0.75`

## Transport Regimes

### high_barrier|low_gamma|high_temp

- Rows: `1`
- Mean RMSE: `0.08465175`
- Max RMSE: `0.08465175`
- Max absolute error: `0.13352574`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task10_pilot_validation_inplane_100_core`

### high_barrier|high_gamma|low_temp

- Rows: `1`
- Mean RMSE: `0.0182967`
- Max RMSE: `0.0182967`
- Max absolute error: `0.027860884`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### low_barrier|low_gamma|high_temp

- Rows: `1`
- Mean RMSE: `0.2071187`
- Max RMSE: `0.2071187`
- Max absolute error: `0.30716892`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task10_pilot_test_inplane_110_core`

### high_barrier|high_gamma|high_temp

- Rows: `1`
- Mean RMSE: `0.079859634`
- Max RMSE: `0.079859634`
- Max absolute error: `0.12996659`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task10_pilot_test_inplane_100_spread`

## Direction Regimes

### inplane_100_no_spread

- Rows: `1`
- Mean RMSE: `0.08465175`
- Max RMSE: `0.08465175`
- Max absolute error: `0.13352574`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task10_pilot_validation_inplane_100_core`

### named_mode_narrow_spread

- Rows: `2`
- Mean RMSE: `0.049078167`
- Max RMSE: `0.079859634`
- Max absolute error: `0.12996659`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task10_pilot_test_inplane_100_spread`

### inplane_110_no_spread

- Rows: `1`
- Mean RMSE: `0.2071187`
- Max RMSE: `0.2071187`
- Max absolute error: `0.30716892`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task10_pilot_test_inplane_110_core`

## Fallback Policy

Surrogate acceleration is disabled for unsafe transport regimes. Inverse workflows must use direct external forward calls there.

For unsafe regimes, inverse workflows must call the external forward
interface directly for candidate scoring or final rechecks.
