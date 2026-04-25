# Task 14 Transport Domain Contract

Task 14D freezes the canonical nuisance-domain envelope for later
inverse-ready dataset contracts.

## Canonical Target Ranges

Later dataset contracts must use these exact initial nuisance ranges:

- `barrier_z` in `[0.10, 1.50]`
- `gamma` in `[0.40, 1.80]`
- `temperature_kelvin` in `[1.0, 15.0]`

This contract does not narrow those ranges for convenience sampling.
The full target envelope remains available to later dataset builders.

## Two-Tier Sampling Policy

The canonical Task 14 nuisance sampler uses two tiers:

- dense core region: target `80%` of rows
- sparse guard-band region: target `20%` of rows

The dense core region is:

- `barrier_z` in `[0.25, 1.20]`
- `gamma` in `[0.55, 1.55]`
- `temperature_kelvin` in `[1.5, 10.0]`

The sparse guard-band region is defined over the full canonical target ranges,
but a row belongs to the guard band only when at least one nuisance coordinate
lies outside the dense core region.

Equivalently, the guard-band slabs are:

- `barrier_z` in `[0.10, 0.25)` or `(1.20, 1.50]`
- `gamma` in `[0.40, 0.55)` or `(1.55, 1.80]`
- `temperature_kelvin` in `[1.0, 1.5)` or `(10.0, 15.0]`

The guard band is intentionally sparse. It exists to keep later inverse-ready
training and evaluation aware of edge-of-domain transport behavior without
letting those edge cases dominate the sample budget.

## Canonical Code Path

The canonical code path is:

- `src/ar_inverse/datasets/sampling.py`

Later dataset contracts should reuse:

- `task14_transport_domain_contract`
- `classify_task14_transport_region`

The fixed policy id is:

- `task14_transport_domain_v1`

The fixed transport grid resolution remains:

- `nk = 41`

## Task 14D Boundary

Task 14D does not generate a dataset and does not launch a server run.
It only freezes the nuisance-domain contract, the dense-core versus
guard-band split, and the lightweight validation needed before later dataset
contracts adopt this wider transport envelope.
