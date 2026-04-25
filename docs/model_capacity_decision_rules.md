# Model Capacity Decision Rules

Task S7 freezes the model-capacity decision rule for the current surrogate
rectification stage.

Current conclusion:

> 现阶段无充分证据支持立即扩模，当前先维持架构不变。

In English:

> There is currently insufficient evidence to justify an immediate capacity
> increase, so the architecture remains unchanged for now.

## Evidence Base

This conclusion is based on the real pre-S7 local observation run:

- training config:
  `configs/surrogate/local/pre_s7_local_observation_training.json`
- evaluation config:
  `configs/surrogate/local/pre_s7_local_observation_evaluation.json`
- training metrics:
  `outputs/checkpoints/pre_s7_local_observation/metrics.json`
- training observability directory:
  `outputs/runs/pre_s7_local_observation/training_observability/`
- evaluation report:
  `outputs/runs/pre_s7_local_observation/evaluation/evaluation_report.json`
- grouped error report:
  `outputs/runs/pre_s7_local_observation/evaluation/grouped_error_report.json`

Observed facts from that run:

- the current residual MLP family trained stably on CUDA;
- `best_epoch = 76`, `epochs_completed = 96`;
- `best_train_loss = 0.0023382097327460847`;
- `best_validation_loss = 0.007727396208792925`;
- gradient warning flags were empty;
- `gradient_max = 1.232308268547058`, not an explosion-scale signal;
- held-out `mean_rmse = 0.012935445347415064`;
- held-out `max_rmse = 0.027339461812714145`;
- held-out `unsafe_fraction = 0.0`;
- grouped reports show some spread across regimes, but no axis emitted
  warning flags and no regime was marked unsafe.

## Current Decision

The current residual architecture is retained unchanged.

Task S7 does not authorize:

- widening the hidden width now;
- adding more residual blocks now;
- replacing the residual MLP family now.

The pre-S7 local run showed meaningful error to keep watching, especially in
`inplane_110_no_spread`, `bridge`, and `outer_shoulder_guard_band`, but those
signals are not yet strong enough to count as clear capacity failure.

## Widening Rule

Widening may be considered later only if later observations show clear
underfitting, meaning all of the following are true together:

1. train and validation losses both plateau at materially unsatisfactory levels;
2. the train-validation gap stays modest rather than showing classic overfit;
3. grouped error inflation is broad across multiple axes rather than isolated to
   one small subgroup;
4. best / median / worst spectrum plots all show the current model missing
   similar large-scale structure.

Without that pattern, widening is not justified.

## Add-Blocks Rule

Adding residual blocks may be considered later only if later observations show
persistent regime-specific structural failure, meaning all of the following are
documented across repeated observations:

1. one or more regimes keep failing after data / optimization settings remain
   otherwise stable;
2. the failure is shape- or structure-dominated rather than only a mild global
   amplitude miss;
3. the same regimes continue to dominate the worst-spectrum set;
4. the grouped error reports keep pointing to the same regimes as systematic
   outliers.

Without persistent repeated regime-specific failure, adding blocks is not
justified.

## Optimization-Instability Rule

Optimization instability is a gating warning, not an automatic instruction to
expand the model immediately.

Capacity change may be considered only if later runs show sustained instability
such as:

- repeated gradient warning flags;
- severe learning-curve oscillation;
- parameter-update magnitudes that stay abnormally large after ordinary
  optimizer or schedule checks;
- and evidence that the instability remains architecture-related after basic
  training hygiene has already been checked.

If instability appears, the first action is to diagnose optimization, not to
silently widen or deepen the model by intuition.

## Leave-Unchanged Rule

The architecture must stay unchanged when the latest accepted observations look
like the current pre-S7 run:

- training is stable;
- no gradient warning is present;
- held-out error is finite and not unsafe by the frozen review thresholds;
- grouped errors vary by regime but do not show a persistent warning-flagged
  collapse;
- representative worst spectra are imperfect but not catastrophic.

That is the current repository state.
