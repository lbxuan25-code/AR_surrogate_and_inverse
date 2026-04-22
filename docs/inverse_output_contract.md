# Inverse Output Contract

Inverse-search outputs are candidate families, not unique microscopic truth
claims.

Reports should say:

```text
the AR data are compatible with these feature families
```

Reports must not say that the order parameter is uniquely determined by one
microscopic RMFT point.

## Candidate Family Schema

Schema version: `ar_inverse_candidate_family_v1`

Every candidate family must include:

- `candidate_family_id`
- `pairing_controls`
- `transport_nuisance_controls`
- `uncertainty_ranges`
- `objective`
- `surrogate_usage`
- `forward_recheck`

`pairing_controls` includes a center and uncertainty ranges for fit-layer
controls. `transport_nuisance_controls` includes a center and uncertainty ranges
for nuisance controls such as barrier strength, broadening, temperature, and
`nk`.

Direction semantics are reported separately through `direction` and
`direction_prior`. Inverse configs accept these direction-prior kinds:

- `direction_resolved`
- `direction_biased`
- `mixed_or_unknown`

When a config is `direction_resolved`, candidates must be restricted to the
allowed supported named modes. Unsupported modes such as `c_axis` are rejected
at config validation time.

`objective` records the score used for ranking. The Task 6 smoke prototype uses
`spectrum_rmse` against a target AR spectrum.

`forward_recheck` records the final direct-forward request, output reference,
objective, and complete forward metadata:

- `forward_interface_version`
- `output_schema_version`
- `pairing_convention_id`
- `formal_baseline_record`
- `formal_baseline_selection_rule`
- `projection_config`
- `git_commit`
- `git_dirty`

## Smoke Report

The Task 6 smoke report is written to:

```text
outputs/inverse/task6_smoke_inverse/inverse_report.json
```

It includes the target row, search policy, surrogate/fallback decision, and the
reported candidate families. Because Task 5 marks the current surrogate unsafe
for inverse acceleration, the smoke inverse search uses direct external-forward
rechecks for final scoring.
