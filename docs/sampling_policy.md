# Sampling Policy

This note defines the initial deterministic smoke sampling policy for Task 2.
It is a schema and metadata guardrail, not a production sampling strategy.

## Policy

- Policy id: `fit_layer_transport_smoke_v1`
- Policy kind: `deterministic_smoke`
- Number of rows: 3
- Splits: `train`, `validation`, `test`
- Forward request kind: `fit_layer`
- Pairing control mode: `delta_from_baseline_meV`
- Weak `delta_zx_s` branch: closed
- Bias grid: `[-20, 20]` meV with 41 points
- Transport grid: small fixed values with `nk = 11`

## Pairing Controls

The smoke policy touches only fit-layer controls exposed by the external
`forward` interface:

- `delta_zz_s`
- `delta_xx_s`
- `delta_zx_d`
- `delta_perp_z`
- `delta_perp_x`

It does not define normal-state Hamiltonian, pairing matrix, projection,
interface matching, or BTK internals.

## Rows

The deterministic smoke rows are:

- `smoke_train_000`: train split, adjusts `delta_zz_s` and `delta_perp_x`.
- `smoke_validation_000`: validation split, adjusts `delta_xx_s` and
  `delta_zx_d`.
- `smoke_test_000`: test split, adjusts `delta_perp_z` and `delta_perp_x`.

Each row records:

- forward request payload;
- forward output reference;
- split label;
- sampling policy id;
- full forward-interface metadata.

## Artifact

The canonical smoke dataset is written to:

```text
outputs/datasets/task2_smoke_fit_layer/dataset.json
```

Referenced forward outputs are written under:

```text
outputs/datasets/task2_smoke_fit_layer/forward_outputs/
```

Run metadata is written to:

```text
outputs/runs/task2_smoke_dataset_run_metadata.json
```

## Legacy Task 3 Orchestration Smoke Config

The archived Task 3 generator uses an explicit legacy JSON config at:

```text
configs/datasets/task3_smoke_dataset.json
```

It keeps the same fit-layer / transport smoke intent but exercises the
resumable dataset-generation CLI. The canonical output is:

```text
outputs/datasets/task3_orchestration_smoke/dataset.json
```

Run it with:

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task3_smoke_dataset.json
```

Rerunning the command reuses completed rows whose referenced forward-output
JSON files still match their recorded SHA-256 digests. Use `--force` to
regenerate every row. This path is retained as a legacy baseline; the current
directional contract entry is the Task 8 config below.

## Direction-Aware Policy

Task 8 adds `directional_fit_layer_transport_smoke_v1` for the forward
direction contract. Sampling is split into three regimes:

- Primary supported regime: `inplane_100` and `inplane_110`, no spread.
- Secondary supported regime: `inplane_100` and `inplane_110` with narrow
  named-mode-centered spread.
- Diagnostic-only regime: generic raw angles, excluded unless a config
  explicitly opts in with `allow_diagnostic_raw_angles`.

Unsupported direction modes, including `c_axis`, are rejected during config
validation. The primary training pool for the next surrogate stage must exclude
generic raw angles by default.

The Task 8 smoke config is:

```text
configs/datasets/task8_directional_smoke_dataset.json
```

It writes:

```text
outputs/datasets/task8_directional_smoke/dataset.json
```

The smoke rows exercise:

- `inplane_100`, no spread;
- `inplane_110`, no spread;
- `inplane_110`, narrow spread with `half_width <= pi/32`.
