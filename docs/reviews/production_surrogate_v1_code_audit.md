# Production Surrogate V1 Code Audit

## Fixed

- Training config explicitly uses `feature_spec_id =
  projected_7plus1_complex_v1`.
- Training feature extraction now reads
  `controls.pairing_representation.channels[*].re/im` and fails if the
  projected complex representation is missing.
- Production materialization enforces exact P1 quotas for split, role,
  direction regime, and TB regime.
- Evaluation checkpoint path matches the training output filename:
  `outputs/checkpoints/production_surrogate_v1/model.pt`.
- Grouped error labels are unified on `nuisance_regime`; evaluation config and
  actual grouped report axes now match.
- Luo/RMFT source lookup no longer falls back to a hidden personal path. It
  requires `LNO327_FORWARD_REPO`, `LNO327_FORWARD_SRC`, or an explicit
  `rmft_source_projection.forward_repo_root`.
- Production rows carry RMFT source provenance, source indices, bridge endpoint
  identifiers where applicable, and the projected 7+1 gauge-fixed
  representation.
- Runbook/config now state that the forward request is real-valued
  `absolute_meV`; the complex 7+1 representation is provenance and training
  input, not a complex forward truth input.

## Still Limited

- The repaired materializer is deterministic quota materialization from compact
  RMFT projection records.
- It does not yet implement scrambled Sobol continuous sampling,
  sensitive-region densification scoring, or quality-triggered bridge
  selection.
- Therefore the next repaired P2 run can validate representation, quota, and
  training behavior, but must not be described as a full implementation of the
  ideal sampling-policy-v2 algorithm.

## Blocking P2

No code-level blocker remains for rerunning the repaired P2 pipeline.

The user must set either `LNO327_FORWARD_REPO` or `LNO327_FORWARD_SRC` before
data generation so the RMFT projection CSV is resolved explicitly.

## Ready For P2

Yes, for the repaired deterministic RMFT-projection quota materialization path.

No model-capacity change, active-learning step, or heavy run was started during
this audit.
