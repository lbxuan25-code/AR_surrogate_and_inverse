# Production Surrogate V1 Review

## Status

P3 reviewed the completed `production_surrogate_v1` P2 outputs.

Primary outcome:

**Revise sampling implementation / metadata before accepting
`production_surrogate_v1` as the current baseline.**

This is not a model-capacity failure. Training and held-out evaluation quality
are strong under the materialized dataset, but P3 found two sampling-review
blockers:

- the P2 dataset composition does not match the P1 sampling targets;
- the original Luo RMFT point cloud is not present in P2 artifacts, so coverage
  of the original Luo RMFT distribution cannot be proven.

No new training, evaluation, active learning, or model-capacity change was
started during P3.

## Reviewed Artifacts

- dataset manifest:
  `outputs/datasets/production_surrogate_v1/dataset.json`
- dataset run metadata:
  `outputs/runs/production_surrogate_v1/dataset_run_metadata.json`
- training metrics:
  `outputs/checkpoints/production_surrogate_v1/metrics.json`
- training history:
  `outputs/runs/production_surrogate_v1/training_observability/training_history.json`
- gradient summary:
  `outputs/runs/production_surrogate_v1/training_observability/gradient_norm_summary.json`
- parameter update summary:
  `outputs/runs/production_surrogate_v1/training_observability/parameter_update_summary.json`
- grouped error report:
  `outputs/runs/production_surrogate_v1/evaluation/grouped_error_report.json`
- evaluation report:
  `outputs/runs/production_surrogate_v1/evaluation/evaluation_report.json`
- representative comparison plots:
  `outputs/runs/production_surrogate_v1/evaluation/figures/best_spectrum_comparison.png`,
  `outputs/runs/production_surrogate_v1/evaluation/figures/median_spectrum_comparison.png`,
  `outputs/runs/production_surrogate_v1/evaluation/figures/worst_spectrum_comparison.png`
- RMFT coverage audit:
  `outputs/audits/production_surrogate_v1/rmft_source_coverage_audit.json`

## Training And Evaluation Review

Training completed cleanly:

- completed epochs: `166`
- best epoch: `126`
- best validation loss: `2.5881134206429124e-05`
- best train loss: `2.10377059346456e-05`
- best reconstruction loss: `1.9910908193310206e-05`
- best shape loss: `7.5119844993309925e-06`
- gradient warning flags: `[]`
- maximum gradient norm: `1.205239176750183`
- median gradient norm: `0.000458901675301604`
- maximum parameter update ratio: `7.838175632059574`
- median parameter update ratio: `0.0006563036475833114`

Held-out quality is well inside the P1 review gate:

- validation RMSE: `0.0008666712076327098`
- test RMSE: `0.0008666712076327097`
- validation / test max absolute error: `0.006040759875568735`
- evaluation mean RMSE across held-out rows: `0.0008077252602247273`
- evaluation worst-row RMSE: `0.002416150475494303`
- evaluation worst-row max absolute error: `0.006040920385119941`
- unsafe fraction: `0.0`

Representative spectra:

- best row: `production_v1_validation_00507`, RMSE
  `0.0003505829604444738`
- median row: `production_v1_validation_00720`, RMSE
  `0.0007380585637926197`
- worst row: `production_v1_test_00738`, RMSE
  `0.002416150475494303`

Grouped errors do not show an obvious model-capacity trigger:

- pairing source role mean RMSEs:
  `anchor = 0.0008002562967252991`,
  `neighborhood = 0.0007570763101097827`,
  `bridge = 0.0008658650769578668`
- direction regime mean RMSEs:
  `inplane_100_no_spread = 0.0008056124137861482`,
  `inplane_110_no_spread = 0.0007333510288724499`,
  `named_mode_narrow_spread = 0.0008846622620025887`
- TB regime mean RMSEs:
  `edge_probe = 0.0008025273737962973`,
  `near_baseline = 0.0008124207487084019`

Conclusion: the current residual MLP architecture should remain unchanged.
S7's "do not expand without evidence" rule is not triggered.

## Sampling Contract Review

The generated dataset has the correct total row count and split count:

- total rows: `8192`
- train / validation / test: `6144 / 1024 / 1024`
- dataset generation workers: `8`

However, P3 found that materialized sampling composition does not match the P1
contract.

Pairing source role target versus actual:

- target: `anchor = 3072`, `neighborhood = 3072`, `bridge = 2048`
- actual: `anchor = 2732`, `neighborhood = 2730`, `bridge = 2730`
- judgment: **mismatch**

Direction regime target versus actual:

- target:
  `inplane_100_no_spread = 2048`,
  `inplane_110_no_spread = 2048`,
  `named_mode_narrow_spread = 4096`
- actual:
  `inplane_100_no_spread = 2736`,
  `inplane_110_no_spread = 2736`,
  `named_mode_narrow_spread = 2720`
- judgment: **mismatch**

TB regime target versus actual:

- target: `near_baseline = 6144`, `edge_probe = 2048`
- actual: `near_baseline = 4154`, `edge_probe = 4038`
- judgment: **mismatch**

This means P2 is a useful training observation, but it should not be accepted
as the frozen P1 sampling baseline until the materializer is fixed or the P1
contract is explicitly revised and re-approved.

## RMFT Source Coverage Audit

P3 generated:

- `outputs/figures/production_surrogate_v1/luo_rmft_sampling_2d.png`
- `outputs/figures/production_surrogate_v1/luo_rmft_sampling_density_2d.png`
- `outputs/figures/production_surrogate_v1/luo_rmft_nearest_neighbor_distance.png`
- `outputs/figures/production_surrogate_v1/luo_rmft_channel_marginal_coverage.png`
- `outputs/audits/production_surrogate_v1/rmft_source_coverage_audit.json`

Coverage judgment: **warning**.

Reason:

- P2 artifacts do not include the original Luo RMFT parameter point cloud.
- P2 artifacts do not include a source-to-anchor mapping from original Luo RMFT
  rows to production anchors.
- Therefore P3 cannot report a true original-Luo-point count, anchor fraction,
  missing-cluster result, or true Luo-to-production nearest-neighbor statistics.

The 2D figure uses PCA over the available 8-channel
`controls.fit_layer_pairing_controls` vectors, with absent channels filled as
zero. This is only a visualization aid:

- PC1 explained variance ratio: `0.4718601120432901`
- PC2 explained variance ratio: `0.2986823791353314`
- this PCA projection is **not** a replacement for the full high-dimensional
  Luo RMFT source coverage audit.

Proxy marginal coverage also shows that roles occupy different narrow channel
subspaces:

- anchor rows use nonzero `delta_zz_s` and `delta_perp_x`;
- neighborhood rows use nonzero `delta_xx_s` and `delta_zx_d`;
- bridge rows use nonzero `delta_perp_x`, `delta_perp_z`, and `delta_zx_d`;
- several canonical 7+1 channels remain zero in the available production
  control vectors.

This reinforces that production v1 cannot yet be claimed to cover most of the
original Luo RMFT parameter distribution.

## P3 Decision

Primary outcome selected:

**Revise sampling and metadata before acceptance.**

Recommended next user-approved action:

Fix or explain the P1-vs-actual sampling composition mismatch, and attach a
compact original Luo RMFT source coverage artifact containing:

- original Luo RMFT source vectors or a compact projection suitable for audit;
- source-to-anchor mapping;
- counts and fractions of original Luo points used as anchors;
- true nearest-neighbor distances from original Luo RMFT points to production
  samples;
- high-density body, sparse edge, and missing-cluster coverage judgment.

Do not widen or deepen the model based on current evidence. Do not start active
learning before the sampling / source-coverage issue is resolved.

## Post-P3 Repair Status

After this review, the repository was repaired before rerunning heavy work:

- production v1 materialization now enforces the P1 global role, direction, and
  TB quotas exactly;
- production v1 materialization now reads the external forward repository's
  compact `outputs/source/round2_projection_examples.csv` RMFT projection
  artifact instead of using synthetic role-only control boxes;
- dataset rows now carry `controls.pairing_representation` and source
  provenance for anchors, neighborhoods, and bridges;
- production training now uses `feature_spec_id =
  projected_7plus1_complex_v1`, which includes real and imaginary parts of all
  projected 7+1 channels;
- evaluation now loads the feature spec from the checkpoint before constructing
  dataset features.

The old P2 review remains valid for the already-generated run. A fresh heavy
dataset generation, training, and evaluation pass is required before accepting
or rejecting the repaired production v1 baseline.
