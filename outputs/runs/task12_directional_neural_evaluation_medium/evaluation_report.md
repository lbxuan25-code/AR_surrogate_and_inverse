# Task 12 Directional Neural Medium-Scale Evaluation

## Summary

- Model: `outputs/checkpoints/task12_directional_neural_medium/model.pt`
- Model type: `neural_mlp_spectrum_surrogate`
- Dataset: `outputs/datasets/task12_directional_medium_neural/dataset.json`
- Held-out splits: `validation, test`
- Safe RMSE threshold: `0.05`
- Safe max-error threshold: `0.1`
- Unsafe regimes: `0`

## Calibration Diagnostics

- Held-out rows: `96`
- Mean RMSE: `0.0024540644`
- Max RMSE: `0.0075590854`
- Mean max absolute error: `0.0056677393`
- Unsafe fraction: `0`

## Transport Regimes

### low_barrier|low_gamma|low_temp

- Rows: `36`
- Mean RMSE: `0.0023537648`
- Max RMSE: `0.0075590854`
- Max absolute error: `0.014530823`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|high_gamma|high_temp

- Rows: `36`
- Mean RMSE: `0.0023941447`
- Max RMSE: `0.0071390409`
- Max absolute error: `0.013563659`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|low_gamma|high_temp

- Rows: `24`
- Mean RMSE: `0.0026943934`
- Max RMSE: `0.0072793364`
- Max absolute error: `0.014320115`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

## Direction Regimes

### inplane_100_no_spread

- Rows: `24`
- Mean RMSE: `0.0026390508`
- Max RMSE: `0.0072793364`
- Max absolute error: `0.014320115`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### inplane_110_no_spread

- Rows: `24`
- Mean RMSE: `0.0024594608`
- Max RMSE: `0.0071390409`
- Max absolute error: `0.013563659`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### named_mode_narrow_spread

- Rows: `48`
- Mean RMSE: `0.002358873`
- Max RMSE: `0.0075590854`
- Max absolute error: `0.014530823`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

## Fallback Policy

All evaluated held-out transport regimes met the configured thresholds. Direct forward rechecks are still required for final inverse candidates.

For unsafe regimes, inverse workflows must call the external forward
interface directly for candidate scoring or final rechecks.
