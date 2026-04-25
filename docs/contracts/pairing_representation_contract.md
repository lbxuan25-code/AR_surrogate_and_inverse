# Task 14 Pairing Representation Contract

Task 14A freezes the canonical future-facing pairing input contract for later
inverse-ready work.

## Canonical Representation

The canonical pairing representation is the full projected complex 7+1 channel
set:

- `delta_zz_s`
- `delta_zz_d`
- `delta_xx_s`
- `delta_xx_d`
- `delta_zx_d`
- `delta_perp_z`
- `delta_perp_x`
- `delta_zx_s`

No PCA, latent compression, or additional lossy reduction is allowed after
these projected channels have been formed.

## Gauge Fixing

Exactly one global-phase gauge-fixing step is applied:

1. Inspect the existing anchor priority in this order:
   `delta_zz_s`, `delta_zz_d`, `delta_xx_s`, `delta_xx_d`, `delta_zx_d`,
   `delta_perp_z`, `delta_perp_x`, `delta_zx_s`.
2. Choose the first channel whose absolute value exceeds the non-negligible
   threshold.
3. Rotate every channel by one common phase so the chosen anchor becomes real
   and non-negative.

This step removes only the physically redundant global phase.
All relative phase information between channels is preserved.

If every channel is negligible, the canonical payload records:

- `gauge_anchor_channel = null`
- `global_phase_rotation_rad = 0.0`

## Canonical Metadata

The serialized representation must record:

- `pairing_representation_version`
- `gauge_anchor_channel`
- `global_phase_rotation_rad`
- `weak_channel_active`

The fixed version string is:

- `projected_7plus1_gauge_fixed_v1`

`weak_channel_active` refers to the canonical weak channel `delta_zx_s`.

## Canonical Code Path

The canonical module is:

- `src/ar_inverse/pairing/representation.py`

The canonical function names are:

- `gauge_fix_pairing_channels`
- `serialize_gauge_fixed_pairing_channels`
- `deserialize_gauge_fixed_pairing_channels`

## Serialized Shape

The manifest-friendly serialized payload is:

```json
{
  "pairing_representation_version": "projected_7plus1_gauge_fixed_v1",
  "gauge_anchor_channel": "delta_zz_s",
  "global_phase_rotation_rad": -0.42,
  "weak_channel_active": false,
  "channels": {
    "delta_zz_s": {"re": 0.25, "im": 0.0},
    "delta_zz_d": {"re": 0.01, "im": -0.03},
    "delta_xx_s": {"re": -0.08, "im": 0.02},
    "delta_xx_d": {"re": 0.00, "im": 0.00},
    "delta_zx_d": {"re": 0.04, "im": 0.05},
    "delta_perp_z": {"re": 0.07, "im": -0.01},
    "delta_perp_x": {"re": -0.02, "im": 0.06},
    "delta_zx_s": {"re": 0.00, "im": 0.00}
  }
}
```

## Dataset Schema Storage

Later dataset rows may store this representation under:

- `row["controls"]["pairing_representation"]`

Rows that include this block use the pairing-aware dataset row schema version
`ar_inverse_dataset_row_v3`.

## Task 14A Boundaries

Task 14A does not generate heavy datasets, train a surrogate, or evaluate a
surrogate.
It only freezes the representation contract, code path, schema validation, and
lightweight tests needed before later Task 14 dataset work begins.
