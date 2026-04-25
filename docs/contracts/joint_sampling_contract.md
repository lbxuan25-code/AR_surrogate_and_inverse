# Joint Sampling Contract

Task S4 freezes how later surrogate datasets jointly sample:

- pairing structure;
- nuisance variables;
- TB variables.

This contract builds on:

- the Task S2 two-level TB decision;
- the Task S3 quality-first pairing sampling policy;
- the existing widened nuisance envelope from Task 14D;
- and the widened `[-40, 40] meV` bias window from Task 14C.

## Canonical Joint-Sampling Principle

Joint sampling is not allowed to behave as if pairing, nuisance, and TB blocks
were unrelated independent boxes.

The repository must explicitly preserve:

- pairing-driven local densification from `sampling_policy_v2`;
- nuisance-domain structure inside the widened transport envelope;
- and TB-aware modulation of where nuisance coverage should concentrate.

## Decision 1: Nuisance Variables

Nuisance variables must not be sampled as fully independent draws.

The canonical nuisance rule is:

- use explicit structured correlations, not full independence.

The frozen structure is:

- `barrier_z` remains conditionally broad and is not tightly tied to the other
  nuisance variables;
- `gamma` and `temperature_kelvin` use positive correlation strata;
- low-`gamma` / low-temperature combinations are deliberately represented
  because they generate sharper spectra;
- high-`gamma` / high-temperature combinations are also represented because
  they generate broadened spectra;
- extreme anti-correlated combinations are allowed only as sparse guard-band
  diagnostics, not as the canonical bulk of the pool.

This means the repository rejects a naive Cartesian-product mindset where
`barrier_z`, `gamma`, and `temperature_kelvin` are all sampled independently
with uniform density.

## Decision 2: TB And Nuisance Coupling

TB variables and nuisance variables must use structured coupling rather than
strict independence.

The canonical coupling rule is:

- near-baseline TB regimes receive the widest nuisance coverage;
- edge-TB regimes still receive coverage across the nuisance envelope, but with
  increased emphasis on spectrally informative nuisance regions rather than on
  diffuse high-broadening combinations;
- grouped TB edge cases must be paired more often with low-to-mid `gamma` and
  low-to-mid temperature because those combinations expose shape differences
  that broad nuisance settings can hide.

Equivalently:

- near-baseline TB: broad nuisance sweep across core plus guard band;
- edge-TB: biased toward sharper-spectrum nuisance strata with some retained
  broad-spectrum coverage for robustness.

This keeps TB effects observable instead of washing them out under nuisance
settings that over-broaden the spectrum.

## Decision 3: Widened Bias-Window Implications

The widened `[-40, 40] meV` / `241`-point bias contract changes where
parameter-space density must increase.

Joint sampling must increase density in parameter regions that are likely to
produce structure in:

- the central window around zero bias;
- the inner shoulder region where coherence-like features emerge;
- the outer shoulder region that becomes visible only after widening the bias
  window.

The canonical bias sub-windows are:

- central window: `|bias| <= 6 meV`
- inner shoulder: `6 < |bias| <= 18 meV`
- outer shoulder: `18 < |bias| <= 32 meV`
- edge guard: `32 < |bias| <= 40 meV`

Density must increase when the pairing/TB/nuisance combination is likely to
create sharp or rapidly changing structure in the inner or outer shoulder
regions, not only near zero bias.

The minimum required densification regions are:

- low `gamma` with low-to-mid temperature;
- high-barrier regimes with low `gamma`;
- edge-TB regimes that shift or split spectral structure into the widened bias
  shoulders;
- pairing anchors or neighborhoods already flagged as high-complexity under
  the Task S3 spectral-complexity score.

This is the bias40 consequence:
the repository must no longer concentrate almost all density on zero-bias
behavior while under-sampling outer-window structure.

## Decision 4: Gamma Density Policy

`gamma` uses piecewise density sampling.

The canonical piecewise bands are:

- sharp-feature band: `gamma in [0.40, 0.75]`
- transition band: `gamma in (0.75, 1.20]`
- broad-feature band: `gamma in (1.20, 1.80]`

The canonical density weights are:

- sharp-feature band: `0.45`
- transition band: `0.35`
- broad-feature band: `0.20`

Interpretation:

- overweight low `gamma` because it exposes fine spectral structure;
- keep substantial mid-band coverage because many practical spectra remain in
  that regime;
- underweight high `gamma`, but do not eliminate it, because broadening
  robustness still matters.

This is intentionally piecewise rather than log-weighted in Task S4 because:

- the contract needs simple reviewable bins;
- the current nuisance envelope is moderate rather than many orders of
  magnitude wide;
- and later returned-artifact review can still decide whether another density
  law is warranted.

## Canonical Joint Regimes

The joint sampler should reason in the following regime language:

- pairing role:
  `anchor`, `neighborhood`, `bridge`
- nuisance regime:
  `core_sharp`, `core_transition`, `core_broad`, `guard_band_sharp`,
  `guard_band_transition`, `guard_band_broad`
- TB regime:
  `near_baseline`, `edge_probe`

The canonical interpretation is:

- `core_*` means the row lies inside the Task 14 dense core for
  `barrier_z`, `gamma`, and `temperature_kelvin`;
- `guard_band_*` means at least one nuisance variable lies outside that dense
  core while staying inside the canonical envelope;
- `*_sharp`, `*_transition`, and `*_broad` are determined by the piecewise
  `gamma` bands.

## What Is Still Deferred

Task S4 freezes the joint-sampling contract in writing, but it does not yet
freeze:

- the exact grouped TB mapping implementation;
- the exact dataset row schema extension for joint-regime metadata;
- the final row counts for any later server dataset.

Those remain downstream of this contract.
