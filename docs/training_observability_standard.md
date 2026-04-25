# Training Observability Standard

Task S5 freezes the minimum observability standard for any later serious
surrogate training run.

The repository no longer accepts the combination

- one `metrics.json`
- plus one `evaluation_report.json`

as sufficient industrial or academic observability.

## Standard Purpose

The standard must make it possible to diagnose:

- underfitting;
- overfitting;
- unstable optimization;
- gradient pathologies;
- feature-block dominance;
- and regime-specific failure.

The standard applies to later serious training runs, not only to smoke-scale
validation.

## Required Training Curves

Every accepted later training run must produce the following curves:

- train loss versus epoch;
- validation loss versus epoch;
- reconstruction loss versus epoch;
- shape loss versus epoch;
- learning-rate curve versus epoch.

These curves are mandatory because:

- train versus validation separation is needed to detect underfitting and
  overfitting;
- reconstruction versus shape terms are needed to see whether one objective is
  dominating the composite loss;
- the learning-rate curve is needed to interpret optimizer behavior and early
  stopping.

## Required Optimization Diagnostics

Every accepted later training run must produce optimization diagnostics for:

- per-layer gradient norm summary;
- parameter update magnitude summary;
- gradient explosion warning logic;
- gradient vanishing warning logic.

The minimum optimization summary must include:

- median gradient norm by layer group;
- maximum gradient norm by layer group;
- parameter update ratio relative to parameter norm;
- warning thresholds and warning counts.

The minimum warning logic is:

- gradient explosion warning when a layer-group gradient norm exceeds the
  configured explosion threshold for multiple consecutive checkpoints;
- gradient vanishing warning when a layer-group gradient norm remains below the
  configured vanishing threshold for multiple consecutive checkpoints.

## Required Sensitivity Diagnostics

Every accepted later training run must report block-level sensitivity for:

- pairing block;
- direction block;
- nuisance block;
- TB block.

The sensitivity report must make it possible to answer:

- whether one input block dominates the learned mapping;
- whether a nominally important block is effectively ignored;
- whether later architecture changes should be motivated by block imbalance
  rather than intuition.

The minimum sensitivity outputs are:

- relative sensitivity score by block;
- rank ordering of blocks by influence;
- imbalance warning when one block dominates beyond the configured ratio limit.

## Required Prediction-Review Figures

Every accepted later training run must produce direct-forward versus surrogate
comparison plots for representative rows in each held-out pool:

- representative best rows;
- representative median rows;
- representative worst rows.

Each representative plot must show:

- direct forward conductance;
- surrogate prediction;
- absolute error curve;
- identifying metadata for bias sub-window, pairing role, nuisance regime,
  TB regime, and direction regime.

This requirement exists because aggregate scalar errors alone are not enough to
show whether the surrogate misses narrow peaks, broad shoulders, or
regime-specific shape changes.

## Required Grouped Error Outputs

Every accepted later training run must produce grouped error reports on the
held-out data by:

- bias sub-window;
- pairing-source role;
- nuisance sub-range;
- TB regime;
- direction regime.

The minimum bias sub-window groups are:

- central window;
- inner shoulder;
- outer shoulder;
- edge guard.

The minimum grouped report must include:

- row count;
- mean RMSE;
- max RMSE;
- mean max absolute error;
- worst-case row ids or representative row ids;
- and unsafe or warning flags when thresholds are exceeded.

## Minimum Artifact Families

The observability standard expects later serious runs to emit artifact families
for:

- scalar summaries in machine-readable JSON;
- curve-ready tabular or series data;
- figure files for training curves;
- figure files for representative spectrum comparisons;
- grouped error tables or reports.

Task S5 freezes the standard, not the final on-disk naming scheme for every
artifact family.

## Decision Boundary For Later Model Changes

No later model-capacity change should be justified without this observability
standard.

In particular, the repository must not widen or deepen the model based only on:

- one final held-out metric;
- one `metrics.json` snapshot;
- or one aggregate evaluation markdown report.

## Task Boundary

Task S5 freezes the observability standard in writing and in lightweight code
helpers.

It does not yet require:

- a completed integration of the standard into every training entry point;
- a heavy local training run;
- or a final architecture decision.
