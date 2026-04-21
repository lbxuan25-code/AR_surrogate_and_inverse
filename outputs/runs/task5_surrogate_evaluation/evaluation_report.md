# Task 5 Surrogate Evaluation And Calibration

## Summary

- Model: `outputs/checkpoints/task4_linear_surrogate/model.npz`
- Dataset: `outputs/datasets/task3_orchestration_smoke/dataset.json`
- Held-out splits: `validation, test`
- Safe RMSE threshold: `0.05`
- Safe max-error threshold: `0.1`
- Unsafe regimes: `2`

## Calibration Diagnostics

- Held-out rows: `2`
- Mean RMSE: `0.14575448`
- Max RMSE: `0.19309576`
- Mean max absolute error: `0.22867247`
- Unsafe fraction: `1`

## Transport Regimes

### high_barrier|high_gamma|high_temp

- Rows: `1`
- Mean RMSE: `0.098413207`
- Max RMSE: `0.098413207`
- Max absolute error: `0.14850668`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task3_smoke_validation_000`

### high_barrier|low_gamma|low_temp

- Rows: `1`
- Mean RMSE: `0.19309576`
- Max RMSE: `0.19309576`
- Max absolute error: `0.30883826`
- Safe for inverse acceleration: `False`
- Unsafe rows: `task3_smoke_test_000`

## Fallback Policy

Surrogate acceleration is disabled for unsafe transport regimes. Inverse workflows must use direct external forward calls there.

For unsafe regimes, inverse workflows must call the external forward
interface directly for candidate scoring or final rechecks.
