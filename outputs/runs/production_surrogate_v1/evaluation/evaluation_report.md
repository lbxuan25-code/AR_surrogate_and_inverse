# Production Surrogate V1 Evaluation

## Summary

- Model: `outputs/checkpoints/production_surrogate_v1/model.pt`
- Model type: `neural_residual_mlp_spectrum_surrogate`
- Dataset: `outputs/datasets/production_surrogate_v1/dataset.json`
- Held-out splits: `validation, test`
- Safe RMSE threshold: `0.03`
- Safe max-error threshold: `0.075`
- Unsafe regimes: `0`

## Calibration Diagnostics

- Held-out rows: `2048`
- Mean RMSE: `0.00080772526`
- Max RMSE: `0.0024161505`
- Mean max absolute error: `0.0025717807`
- Unsafe fraction: `0`

## Uncertainty Diagnostics

- Mean member std: `0`
- Max member std: `0`
- Mean-std threshold: `0`
- Max-std threshold: `0`
- High disagreement fraction: `0`

## Transport Regimes

### low_barrier|low_gamma|low_temp

- Rows: `392`
- Mean RMSE: `0.00085670491`
- Max RMSE: `0.0024161505`
- Max absolute error: `0.0060409204`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### low_barrier|low_gamma|high_temp

- Rows: `134`
- Mean RMSE: `0.00071329793`
- Max RMSE: `0.0017005322`
- Max absolute error: `0.0041500877`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### low_barrier|high_gamma|high_temp

- Rows: `230`
- Mean RMSE: `0.00076697782`
- Max RMSE: `0.0018891257`
- Max absolute error: `0.0051883313`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|low_gamma|high_temp

- Rows: `268`
- Mean RMSE: `0.00074037552`
- Max RMSE: `0.0013733453`
- Max absolute error: `0.0044278428`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|high_gamma|high_temp

- Rows: `828`
- Mean RMSE: `0.00083693159`
- Max RMSE: `0.0018515894`
- Max absolute error: `0.0044123086`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|low_gamma|low_temp

- Rows: `162`
- Mean RMSE: `0.00079632357`
- Max RMSE: `0.001613398`
- Max absolute error: `0.0055969865`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### low_barrier|high_gamma|low_temp

- Rows: `24`
- Mean RMSE: `0.00082940039`
- Max RMSE: `0.0020429651`
- Max absolute error: `0.0049238157`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|high_gamma|low_temp

- Rows: `10`
- Mean RMSE: `0.0006096163`
- Max RMSE: `0.0010198521`
- Max absolute error: `0.0031627744`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

## Direction Regimes

### inplane_100_no_spread

- Rows: `684`
- Mean RMSE: `0.00080561241`
- Max RMSE: `0.0021773492`
- Max absolute error: `0.0052404847`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### inplane_110_no_spread

- Rows: `684`
- Mean RMSE: `0.00073335103`
- Max RMSE: `0.0017005322`
- Max absolute error: `0.0055969865`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### named_mode_narrow_spread

- Rows: `680`
- Mean RMSE: `0.00088466226`
- Max RMSE: `0.0024161505`
- Max absolute error: `0.0060409204`
- Mean disagreement std: `0`
- Max disagreement std: `0`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

## Fallback Policy

All evaluated held-out transport regimes met the configured thresholds. Direct forward rechecks are still required for final inverse candidates.

## Observability Artifacts

- Grouped error report: `outputs/runs/production_surrogate_v1/evaluation/grouped_error_report.json`
- Best spectrum comparison: `outputs/runs/production_surrogate_v1/evaluation/figures/best_spectrum_comparison.png`
- Median spectrum comparison: `outputs/runs/production_surrogate_v1/evaluation/figures/median_spectrum_comparison.png`
- Worst spectrum comparison: `outputs/runs/production_surrogate_v1/evaluation/figures/worst_spectrum_comparison.png`

For unsafe regimes, inverse workflows must call the external forward
interface directly for candidate scoring or final rechecks.
