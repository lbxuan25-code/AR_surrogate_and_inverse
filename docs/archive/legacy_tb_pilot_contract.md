# Task 14 TB Pilot Contract

Legacy status:
this draft pilot contract is retained only as archived reference material after
the S2 TB decision. It is not the canonical long-term TB representation.

Task 14E freezes the first low-dimensional normal-state variation contract for
later inverse-ready datasets.

## Fixed TB Pilot Coordinates

The canonical Task 14E TB pilot uses exactly these five coordinates:

- `mu_shift`
- `bandwidth_scale`
- `interlayer_scale`
- `orbital_splitting_shift`
- `hybridization_scale`

No additional TB pilot coordinates are allowed in Task 14E.

## Coordinate Semantics

These coordinates are low-dimensional pilot controls around the current forward
baseline normal state. They are not a full replacement for the forward
repository's normal-state Hamiltonian.

The Task 14E pilot contract records these controls as normalized latent offsets
or scales in a manifest-friendly block:

- `row["controls"]["tb_pilot_coordinates"]`

The fixed coordinate-system version is:

- `task14_tb_pilot_latent_v1`

## Canonical Pilot Envelope

The initial Task 14E TB pilot envelope is:

- `mu_shift` in `[-0.35, 0.35]`
- `bandwidth_scale` in `[-0.20, 0.20]`
- `interlayer_scale` in `[-0.25, 0.25]`
- `orbital_splitting_shift` in `[-0.30, 0.30]`
- `hybridization_scale` in `[-0.25, 0.25]`

These are deliberately modest pilot variations. Task 14E widens the normal
state beyond the fully frozen baseline, but it does not jump immediately to a
large unconstrained TB search box.

## Sampling Shape

The canonical Task 14E TB pilot uses a two-band exploratory split:

- near-baseline band: target `70%` of TB-varied rows
- edge-probe band: target `30%` of TB-varied rows

The near-baseline band keeps every TB pilot coordinate within `0.15` of zero.
The edge-probe band stays within the full canonical pilot envelope, but a row
belongs to the edge-probe band when at least one coordinate lies outside the
near-baseline band.

## Allowed Guards

Task 14E explicitly allows only lightweight forward-safety guards:

- `solver_stability`
- `finite_forward_output`
- `schema_validity`

Task 14E explicitly forbids strong heavy hard constraints such as:

- band-topology filters
- Fermi-surface hard filters
- manual phase-diagram gates

## Contract Dependencies

This TB pilot contract is layered on top of the already frozen Task 14 inputs:

- RMFT-projected pairing source:
  `configs/datasets/contracts/rmft_anchor_dataset_contract.json`
- widened bias-window probe family:
  `configs/datasets/contracts/bias40_probe_dataset_contract.json`
- widened nuisance-domain contract:
  `docs/contracts/transport_domain_contract.md`

The truth-grade direction contract remains unchanged:

- supported modes: `inplane_100`, `inplane_110`
- narrow named-mode-centered spread only
- `c_axis` remains unsupported

## Task 14E Boundary

Task 14E does not generate a dataset and does not launch a server run.
It only freezes the first low-dimensional TB pilot contract and the lightweight
validation needed before Task 15A combines pairing, bias, nuisance, direction,
and TB pilot variation into one inverse-ready medium-scale contract.
