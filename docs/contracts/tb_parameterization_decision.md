# TB Parameterization Decision

Task S2 decision date:
2026-04-25

## Decision

The repository will use a two-level TB representation.

Level 1:
preserve the original forward-exposed normal-state parameter form, or an exact
baseline-referenced equivalent emitted through the forward public interface, as
dataset provenance.

Level 2:
use a physically grouped TB parameter form as the canonical training-facing
surrogate input family.

The current reduced five-coordinate pilot
`task14_tb_pilot_latent_v1` is not retained as the canonical long-term
representation.

## Explicit Answer To The Task S2 Question

The repository should not choose only one of the three families as an exclusive
representation.

Instead it should use:

1. original forward parameter form for provenance and exact traceability;
2. physically grouped parameter form for canonical surrogate intake;
3. reduced coordinates only as optional exploratory helpers after they are
   explicitly derived from and checked against the grouped/original layers.

This means the current low-dimensional TB pilot should be:

- split into a two-level representation structure;
- demoted from canonical status;
- and treated as a draft engineering convenience rather than an automatically
  correct parameterization.

## Why This Decision Wins

Physical interpretability:
the grouped form is the strongest training-facing option because the surrogate
can learn along controls that still correspond to understandable physical
changes.

Forward traceability:
the original form must remain preserved so later review can recover what the
forward engine actually saw. Grouped controls alone are not sufficient.

Surrogate input dimensionality:
the grouped form is smaller than the original form without making the same
aggressive compression move as a reduced latent representation.

Sampling difficulty:
the grouped form is materially easier to sample than the full original form,
which matters because Task S3 and Task S4 will redesign sampling quality and
joint sampling.

Expected degeneracy risk:
the reduced form has the highest hidden-degeneracy risk. Keeping original
provenance plus grouped controls lowers that risk and makes later audits
possible.

## Resulting Repository Rule

Until a later contract freezes the exact grouped mapping:

- do not promote `task14_tb_pilot_latent_v1` into the canonical long-term TB
  representation;
- do not assume reduced coordinates are better than original or grouped forms;
- do not build a future serious surrogate contract that stores only reduced TB
  coordinates with no original-parameter provenance.

## Immediate Consequences

1. Future TB-aware dataset contracts should preserve original forward-side
   normal-state provenance rather than only `controls.tb_pilot_coordinates`.
2. The next TB contract should freeze explicit grouped controls and their
   deterministic mapping to forward-exposed original parameters.
3. The current five-coordinate pilot may remain as a labeled draft sampling or
   proposal layer, but not as the sole canonical surrogate input definition.

## Status Of The Current Five-Coordinate Pilot

Current status:
draft exploratory convenience only.

Not allowed status:

- sole canonical TB representation;
- automatically correct reduced basis;
- scientifically privileged long-term parameterization.
