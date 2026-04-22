# Direction Contract

This repository consumes direction semantics only through the external
`forward` package. It does not copy or reinterpret forward-side directional
physics.

## Supported Named Modes

The current truth-grade named in-plane modes are:

- `inplane_100`
- `inplane_110`

Dataset generation and inverse candidate configs may use these modes as
supported direction targets.

## Unsupported Modes

`c_axis` is not supported by the current forward contract. This repository
rejects it during config validation and must not expose it as a valid training
mode or inverse target.

## Diagnostic Raw Angles

Generic raw `interface_angle` requests are diagnostic-only. They are excluded
from the primary training pool unless a generation config explicitly opts in
with `allow_diagnostic_raw_angles`.

When raw angles are present, they must be labeled as diagnostic and reported
separately from truth-grade named modes.

## Directional Spread

Directional spread is only the narrow, named-mode-centered approximation
validated by the forward repository. This repository accepts spread only for
supported named modes and enforces:

```text
half_width <= pi/32
```

Spread rows are reported as `named_mode_narrow_spread` and are distinct from
no-spread named-mode rows.

## Local Regime Labels

Direction-aware reports use these local buckets:

- `inplane_100_no_spread`
- `inplane_110_no_spread`
- `named_mode_narrow_spread`
- `diagnostic_raw_angle`
- `legacy_or_unknown_direction`

These labels are local bookkeeping for surrogate and inverse workflows. The
forward repository remains the authority for the physical direction metadata.
