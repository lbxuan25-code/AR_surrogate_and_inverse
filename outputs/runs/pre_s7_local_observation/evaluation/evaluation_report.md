# Pre-S7 Local Observation Evaluation

## Summary

- Model: `outputs/checkpoints/pre_s7_local_observation/model.pt`
- Model type: `neural_residual_mlp_spectrum_surrogate`
- Dataset: `outputs/datasets/pre_s7_local_observation/dataset.json`
- Held-out splits: `validation, test`
- Safe RMSE threshold: `0.06`
- Safe max-error threshold: `0.12`
- Unsafe regimes: `0`

## Calibration Diagnostics

- Held-out rows: `24`
- Mean RMSE: `0.012935445`
- Max RMSE: `0.027339462`
- Mean max absolute error: `0.043274524`
- Unsafe fraction: `0`

## Uncertainty Diagnostics

- Mean member std: `0`
- Max member std: `0`
- Mean-std threshold: `0`
- Max-std threshold: `0`
- High disagreement fraction: `0`

## Transport Regimes

### low_barrier|low_gamma|low_temp

- Rows: `8`
- Mean RMSE: `0.01346812`
- Max RMSE: `0.027339462`
- Max absolute error: `0.057350447`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|high_gamma|high_temp

- Rows: `16`
- Mean RMSE: `0.012669108`
- Max RMSE: `0.018958088`
- Max absolute error: `0.07221501`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

## Direction Regimes

### inplane_100_no_spread

- Rows: `6`
- Mean RMSE: `0.012104392`
- Max RMSE: `0.025939756`
- Max absolute error: `0.061843818`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### inplane_110_no_spread

- Rows: `6`
- Mean RMSE: `0.014994104`
- Max RMSE: `0.027339462`
- Max absolute error: `0.07221501`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### named_mode_narrow_spread

- Rows: `12`
- Mean RMSE: `0.012321643`
- Max RMSE: `0.018958088`
- Max absolute error: `0.066874533`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

## Fallback Policy

All evaluated held-out transport regimes met the configured thresholds. Direct forward rechecks are still required for final inverse candidates.

## Observability Artifacts

- Grouped error report: `outputs/runs/pre_s7_local_observation/evaluation/grouped_error_report.json`
- Best spectrum comparison: `outputs/runs/pre_s7_local_observation/evaluation/figures/best_spectrum_comparison.png`
- Median spectrum comparison: `outputs/runs/pre_s7_local_observation/evaluation/figures/median_spectrum_comparison.png`
- Worst spectrum comparison: `outputs/runs/pre_s7_local_observation/evaluation/figures/worst_spectrum_comparison.png`

For unsafe regimes, inverse workflows must call the external forward
interface directly for candidate scoring or final rechecks.
