# Task 13 High-Accuracy Large-Scale Launch Addendum

This addendum is the Task 13B pre-launch gate for the first high-accuracy
heavy server run.

## Launch Hyperparameters

Task 13B launch hyperparameters remain unchanged from the current committed
training config at
`configs/surrogate/task13_directional_high_accuracy_large.json`:

- `model_type = neural_residual_mlp_spectrum_surrogate`
- `residual_hidden_width = 384`
- `residual_num_blocks = 5`
- `normalization = layernorm`
- `activation = gelu`
- `optimizer = adamw`
- `learning_rate = 0.0004`
- `weight_decay = 0.00005`
- `batch_size = 48`
- `max_epochs = 450`
- `early_stopping_patience = 40`
- `ensemble seeds = [1103, 2207, 3301]`

## Disagreement-Trigger Fallback

Task 13B disagreement-trigger fallback thresholds are fixed to:

- `mean_std = 0.005`
- `max_std = 0.025`

These thresholds are the Task 13B pre-launch gate used to mark held-out rows
with high ensemble disagreement as `direct-forward-required`.

Final inverse candidates still require direct forward recheck even when they
pass this disagreement gate.

## Contract Preservation

This addendum does not change the frozen direction contract.
It does not introduce `c_axis`.
It does not introduce diagnostic raw-angle primary rows.
