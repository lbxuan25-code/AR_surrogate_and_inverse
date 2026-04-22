# Task 5 Surrogate Evaluation And Calibration

## Summary

- Model: `outputs/checkpoints/task4_linear_surrogate/model.npz`
- Dataset: `outputs/datasets/task8_directional_smoke/dataset.json`
- Held-out splits: `validation, test`
- Safe RMSE threshold: `0.05`
- Safe max-error threshold: `0.1`
- Unsafe regimes: `2`

## Calibration Diagnostics

- Held-out rows: `2`
- Mean RMSE: `0.14721804`
- Max RMSE: `0.2001587`
- Mean max absolute error: `0.21432102`
- Unsafe fraction: `1`

## Transport Regimes

### high_barrier|high_gamma|high_temp

- Rows: `1`
- Mean RMSE: `0.094277379`
- Max RMSE: `0.094277379`
- Max absolute error: `0.13597491`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task8_direction_validation_inplane_110`

### high_barrier|low_gamma|low_temp

- Rows: `1`
- Mean RMSE: `0.2001587`
- Max RMSE: `0.2001587`
- Max absolute error: `0.29266713`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task8_direction_test_inplane_110_spread`

## Direction Regimes

### inplane_110_no_spread

- Rows: `1`
- Mean RMSE: `0.094277379`
- Max RMSE: `0.094277379`
- Max absolute error: `0.13597491`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task8_direction_validation_inplane_110`

### named_mode_narrow_spread

- Rows: `1`
- Mean RMSE: `0.2001587`
- Max RMSE: `0.2001587`
- Max absolute error: `0.29266713`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task8_direction_test_inplane_110_spread`

## Fallback Policy

Surrogate acceleration is disabled for unsafe transport regimes. Inverse workflows must use direct external forward calls there.

For unsafe regimes, inverse workflows must call the external forward
interface directly for candidate scoring or final rechecks.
