# Task 11 Production Server Handoff

Task 11A prepares the first production server contract only. Task 11B is the actual production server run.
Do not launch the production dataset generation, training, or evaluation in the local Codex workspace.

## Canonical Configs

- Dataset config: `configs/datasets/task11_directional_production_dataset.json`
- Training config: `configs/surrogate/task11_directional_surrogate_production.json`
- Evaluation config: `configs/surrogate/task11_directional_evaluation_production.json`

These configs define the first production truth-grade domain:

- `inplane_100`, no spread
- `inplane_110`, no spread
- narrow named-mode-centered spread around supported named modes only

They explicitly exclude:

- `c_axis`
- diagnostic raw in-plane angles
- arbitrary or wide multi-direction mixtures
- experiment-side direction mixtures in the surrogate truth dataset

## Frozen Forward Metadata Family

The first production contract freezes the forward metadata family validated by
Task 10B. The server-side production run should identify this family:

- `forward_interface_version`: `ar_forward_v1`
- `output_schema_version`: `ar_forward_output_v1`
- `pairing_convention_id`: `round2_physical_channels_task_h_fit_layer_v1`
- `formal_baseline_record`: `outputs/source/round2_baseline_selection.json`
- `formal_baseline_selection_rule`: `temperature sweep RMFT pairing data, charge-balanced p≈0 branch, temperature_eV <= 1.0e-3, first 8 samples sorted by temperature`
- `git_commit`: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`
- `git_dirty`: `false`

The production server run should be treated as out of contract if the returned
compact artifacts identify a different forward metadata family.

## Frozen Direction Contract

The production direction contract remains limited to the validated local and
forward-compatible interpretation:

- direction schema version: `ar_inverse_direction_v1`
- truth-grade named modes: `inplane_100`, `inplane_110`
- spread rule: narrow named-mode-centered spread only, `half_width <= pi/32`
- unsupported mode: `c_axis`
- diagnostic raw angles: excluded from this production contract

## Server Preconditions

Run from the repository root on the server after:

- the external forward repository is installed and importable as `forward`, or
  `LNO327_FORWARD_SRC` / `LNO327_FORWARD_REPO` points to it;
- the external forward repository working tree is clean enough that the emitted
  metadata should report `git_dirty: false`;
- this repository is on the exact Git commit that contains the Task 11A
  configs and this handoff note;
- the Python environment can run the existing CLI entry points.

Recommended install shape:

```bash
python -m pip install -e /path/to/forward-repo
python -m pip install -e ".[dev]"
```

## Exact Commands For Task 11B

### 1. Generate the production dataset

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task11_directional_production_dataset.json
```

Expected primary outputs:

- `outputs/datasets/task11_directional_production/dataset.json`
- `outputs/runs/task11_directional_dataset_run_metadata.json`

### 2. Train the production surrogate

```bash
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task11_directional_surrogate_production.json
```

Expected primary outputs:

- `outputs/checkpoints/task11_directional_surrogate_production/model.npz`
- `outputs/checkpoints/task11_directional_surrogate_production/metrics.json`
- `outputs/checkpoints/task11_directional_surrogate_production/model_card.md`
- `outputs/runs/task11_directional_surrogate_production_run_metadata.json`

### 3. Evaluate the production surrogate

```bash
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task11_directional_evaluation_production.json
```

Expected primary outputs:

- `outputs/runs/task11_directional_evaluation_production/evaluation_report.json`
- `outputs/runs/task11_directional_evaluation_production/evaluation_report.md`
- `outputs/runs/task11_directional_evaluation_production_run_metadata.json`

## Compact Artifacts To Return To GitHub

Return only compact review artifacts. At minimum, commit back:

- `configs/datasets/task11_directional_production_dataset.json`
- `configs/surrogate/task11_directional_surrogate_production.json`
- `configs/surrogate/task11_directional_evaluation_production.json`
- `outputs/runs/task11_directional_dataset_run_metadata.json`
- `outputs/checkpoints/task11_directional_surrogate_production/metrics.json`
- `outputs/checkpoints/task11_directional_surrogate_production/model_card.md`
- `outputs/runs/task11_directional_surrogate_production_run_metadata.json`
- `outputs/runs/task11_directional_evaluation_production/evaluation_report.json`
- `outputs/runs/task11_directional_evaluation_production/evaluation_report.md`
- `outputs/runs/task11_directional_evaluation_production_run_metadata.json`
- `outputs/runs/task11_production_server_run_note.md`
- compact dataset family metadata proving the frozen forward metadata family was used

The production dataset manifest may be returned directly if its size stays
reviewable; otherwise return a compact dataset family metadata artifact that
still proves:

- `ar_inverse_dataset_row_v2` row usage
- preserved direction blocks
- preserved forward provenance
- supported named modes plus narrow spread only
- the frozen forward metadata family

## Heavy Artifacts That Should Stay On The Server

Keep these on the server unless a later task explicitly promotes a compact
canonical sample:

- `outputs/datasets/task11_directional_production/forward_outputs/`
- `outputs/checkpoints/task11_directional_surrogate_production/model.npz`
- any copied forward-output directories
- any large raw spectra collections

## Required Server Run Note

Create `outputs/runs/task11_production_server_run_note.md` on the server and
return it to GitHub. It should record:

- forward repository commit used
- training repository commit used
- exact commands run
- output directories used
- whether the full dataset manifest or a compact family metadata artifact was returned

## Review Boundary

Task 11B is not complete when the server commands finish. It is complete only
after the compact returned artifacts are committed back to GitHub and reviewed
locally for frozen forward-family consistency, schema correctness, naming, and
direction-regime compliance.
