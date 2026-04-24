# Task 13 Directional High-Accuracy Large-Scale Evaluation

## Summary

- Model: `outputs/checkpoints/task13_directional_high_accuracy_large/ensemble_manifest.json`
- Model type: `neural_residual_mlp_spectrum_surrogate`
- Dataset: `outputs/datasets/task13_directional_large_accuracy/dataset.json`
- Held-out splits: `validation, test`
- Safe RMSE threshold: `0.03`
- Safe max-error threshold: `0.075`
- Unsafe regimes: `0`

## Calibration Diagnostics

- Held-out rows: `1024`
- Mean RMSE: `0.00091152993`
- Max RMSE: `0.0045115779`
- Mean max absolute error: `0.002247659`
- Unsafe fraction: `0`

## Uncertainty Diagnostics

- Mean member std: `0.00075271399`
- Max member std: `0.004732158`
- Mean-std threshold: `0.005`
- Max-std threshold: `0.025`
- High disagreement fraction: `0`

## Transport Regimes

### low_barrier|low_gamma|low_temp

- Rows: `128`
- Mean RMSE: `0.0010473952`
- Max RMSE: `0.0037832523`
- Max absolute error: `0.0065050515`
- Mean disagreement std: `0.00075194558`
- Max disagreement std: `0.0047185767`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### low_barrier|high_gamma|low_temp

- Rows: `128`
- Mean RMSE: `0.0010971185`
- Max RMSE: `0.0045115779`
- Max absolute error: `0.0079531531`
- Mean disagreement std: `0.00073706985`
- Max disagreement std: `0.004732158`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|low_gamma|low_temp

- Rows: `128`
- Mean RMSE: `0.00070274555`
- Max RMSE: `0.0029268091`
- Max absolute error: `0.0052582497`
- Mean disagreement std: `0.00083461011`
- Max disagreement std: `0.0044909211`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|high_gamma|low_temp

- Rows: `128`
- Mean RMSE: `0.00053673432`
- Max RMSE: `0.0026695032`
- Max absolute error: `0.004900332`
- Mean disagreement std: `0.00073633783`
- Max disagreement std: `0.0036495761`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### low_barrier|low_gamma|high_temp

- Rows: `128`
- Mean RMSE: `0.001290348`
- Max RMSE: `0.0032907671`
- Max absolute error: `0.0061731156`
- Mean disagreement std: `0.0007523504`
- Max disagreement std: `0.0041750797`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### low_barrier|high_gamma|high_temp

- Rows: `128`
- Mean RMSE: `0.00079542352`
- Max RMSE: `0.0027639978`
- Max absolute error: `0.0054509723`
- Mean disagreement std: `0.00067640298`
- Max disagreement std: `0.0038991836`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|low_gamma|high_temp

- Rows: `128`
- Mean RMSE: `0.0008108797`
- Max RMSE: `0.0029456861`
- Max absolute error: `0.0053387426`
- Mean disagreement std: `0.00078940214`
- Max disagreement std: `0.0035776326`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### high_barrier|high_gamma|high_temp

- Rows: `128`
- Mean RMSE: `0.0010115946`
- Max RMSE: `0.0029710095`
- Max absolute error: `0.0051907107`
- Mean disagreement std: `0.00074359304`
- Max disagreement std: `0.0039946611`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

## Direction Regimes

### inplane_100_no_spread

- Rows: `256`
- Mean RMSE: `0.00082359079`
- Max RMSE: `0.0027522082`
- Max absolute error: `0.0049379317`
- Mean disagreement std: `0.0006974344`
- Max disagreement std: `0.0036078848`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### inplane_110_no_spread

- Rows: `256`
- Mean RMSE: `0.00083477779`
- Max RMSE: `0.0029710095`
- Max absolute error: `0.0056041284`
- Mean disagreement std: `0.00066015017`
- Max disagreement std: `0.0039946611`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

### named_mode_narrow_spread

- Rows: `512`
- Mean RMSE: `0.00099387558`
- Max RMSE: `0.0045115779`
- Max absolute error: `0.0079531531`
- Mean disagreement std: `0.00082663569`
- Max disagreement std: `0.004732158`
- Safe for inverse acceleration: `True`
- Unsafe rows: `none`

## Fallback Policy

All evaluated held-out transport regimes met the configured thresholds. Direct forward rechecks are still required for final inverse candidates. Rows that exceed the ensemble disagreement thresholds also require direct forward rechecks.

For unsafe regimes, inverse workflows must call the external forward
interface directly for candidate scoring or final rechecks.
