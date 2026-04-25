# Sampling Policy V2

Task S3 freezes the first quality-first sampling policy for later surrogate
rectification work.

This document replaces the old quota-first mindset in which the row budget was
treated as the first design choice and anchor / neighborhood / bridge coverage
was fitted around it afterward.

## Canonical Principle

Sampling-policy design comes before final row-budget freezing.

The row budget is now a downstream consequence of:

- anchor coverage requirements;
- neighborhood density rules;
- bridge triggering rules;
- continuous-subspace sampler choice;
- and spectral-complexity-driven densification.

## Policy Id

- `quality_first_rmft_sampling_v2`

## Pairing Source Structure

The canonical pairing source family remains:

- projected RMFT anchor points;
- local neighborhoods around projected anchors;
- sparse bridges between nearby projected anchors.

What changes in V2 is the decision logic:
the repository no longer starts from fixed counts such as
`anchor = ...`, `neighborhood = ...`, `bridge = ...`.
Instead it starts from quality rules for when each role must expand.

## Anchor Coverage Rules

Anchor coverage is primary.

The fixed rule is:

- every accepted RMFT anchor family must receive at least one direct anchor
  representative before any neighborhood-heavy or bridge-heavy rebalancing is
  allowed.

Sensitive anchors receive one extra direct replicate when they show any of:

- weak-channel activation;
- high anchor-local spectral complexity;
- phase-turning behavior under the projected 7+1 representation.

This means anchor coverage is a gating requirement, not a leftover quota.

## Neighborhood Density Rules

Neighborhood density is defined per anchor instead of by one global role quota.

The frozen base rule is:

- base samples per anchor: `6`
- dense samples per anchor: `12`
- maximum samples per anchor in this first policy: `18`

The local-core radius is:

- normalized anchor-local radius fraction `<= 0.12`

Neighborhood density must increase whenever any of the following is true:

- spectral complexity score `>= 0.58`
- the row lies in a physically sensitive region
- the candidate lies inside the local-core radius fraction `<= 0.12`

In V2, this is the clear rule for neighborhood densification.

## Continuous-Subspace Sampler

The canonical continuous-subspace sampler is:

- scrambled Sobol

More precisely:

- sampler id: `scrambled_sobol_v1`
- sampler kind: `scrambled_sobol`
- scrambling: Owen scrambling
- batch rule: power-of-two prefixes

This sampler is frozen explicitly so the repository no longer says only
"continuous sampling" without naming the actual sampler family.

## Spectral Complexity Score

V2 freezes the first explicit complexity score used for densification.

The score uses four compact inputs:

- prominent extrema count
- zero-bias curvature magnitude
- mean absolute first difference
- disagreement proxy

The score is normalized to `[0, 1]`.

Its first dense-resampling trigger is:

- dense resampling when score `>= 0.58`

This is intentionally simple and reviewable. It is a first explicit importance
rule, not a claim that the score is already optimal.

## Bridge Triggering Rules

Bridge samples are no longer allocated by a fixed global role share.
They are triggered only for eligible nearby anchor pairs.

The frozen eligibility window is:

- normalized anchor distance in `[0.18, 0.65]`

Inside that window, a bridge is triggered when any of the following is true:

- weak-channel activation flips across the anchor pair
- phase regime changes across the anchor pair
- complexity gap across the pair is `>= 0.20`

This keeps bridge samples sparse and purpose-driven instead of quota-driven.

## Row-Budget Rule

V2 explicitly rejects the old design order:

- first pick total rows;
- then force anchor / neighborhood / bridge counts to fit that number.

Instead, a row budget may be frozen only after:

- every accepted RMFT anchor family is covered;
- neighborhood density rules are fixed and reviewable;
- bridge-trigger frequency can be estimated from pilot audit statistics;
- dense-resampling behavior is stable under the canonical scrambled-Sobol
  sampler.

Until those quality gates are satisfied, fixed row count is not a first-class
design input.

## Task Boundary

Task S3 freezes the quality-first pairing sampling policy only.

It does not yet freeze:

- full joint sampling across pairing, nuisance, and TB spaces;
- nuisance/TB coupling rules;
- final gamma density rules.

Those belong to Task S4.
