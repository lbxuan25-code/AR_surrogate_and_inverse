# Task 12 Neural Medium-Scale Server Handoff

Task 12A prepares the first neural surrogate stack only. Task 12B is the
actual medium-scale server validation run. Do not launch the medium-scale
dataset generation, neural training, or neural evaluation in the local Codex
workspace.

## Canonical Configs

- Dataset config: `configs/datasets/task12_directional_medium_dataset.json`
- Neural training config: `configs/surrogate/task12_directional_neural_medium.json`
- Neural evaluation config:
  `configs/surrogate/task12_directional_neural_evaluation_medium.json`

These configs define the first medium-scale neural validation contract:

- approximately medium scale through `352` total rows
- `train` / `validation` / `test` splits with explicit regime coverage
- supported named modes only: `inplane_100`, `inplane_110`
- narrow named-mode-centered spread only

They explicitly exclude:

- `c_axis`
- diagnostic raw-angle primary rows
- arbitrary or wide spread
- experiment-side direction mixtures in the surrogate truth dataset

## Frozen Forward Metadata Family

The Task 12 contract keeps the same frozen forward metadata family accepted in
Task 11B:

- `forward_interface_version`: `ar_forward_v1`
- `output_schema_version`: `ar_forward_output_v1`
- `pairing_convention_id`: `round2_physical_channels_task_h_fit_layer_v1`
- `formal_baseline_record`: `outputs/source/round2_baseline_selection.json`
- `formal_baseline_selection_rule`: `temperature sweep RMFT pairing data, charge-balanced p≈0 branch, temperature_eV <= 1.0e-3, first 8 samples sorted by temperature`
- `git_commit`: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`
- `git_dirty`: `false`

The Task 12B server run is out of contract if returned artifacts identify a
different forward metadata family.

## Frozen Direction Contract

The direction contract remains unchanged:

- direction schema version: `ar_inverse_direction_v1`
- truth-grade named modes: `inplane_100`, `inplane_110`
- spread rule: narrow named-mode-centered spread only, `half_width <= pi/32`
- unsupported mode: `c_axis`
- diagnostic raw angles: excluded from this Task 12 contract

## Neural Stack Contract

The first neural surrogate stack must preserve the current feature contract and
predict the full conductance spectrum on the fixed bias grid used by the Task
12 dataset config. The canonical neural validation config uses:

- model type: `neural_mlp_spectrum_surrogate`
- hidden layer widths: `[256, 256, 128]`
- activation: `gelu`
- optimizer: `adamw`
- learning rate: `5e-4`
- batch size: `32`
- epoch limit: `250`
- early-stopping patience: `25`
- random seed: `1201`
- device selection: `auto`

The ridge-linear path remains in the repository as a baseline comparator and
must not be removed during Task 12.

## Server Preconditions

Run from the repository root on the server after:

- the external forward repository is installed and importable as `forward`, or
  `LNO327_FORWARD_SRC` / `LNO327_FORWARD_REPO` points to it;
- the external forward repository working tree is clean enough that emitted
  metadata should report `git_dirty: false`;
- this repository is on the exact Git commit that contains the Task 12A
  configs and this handoff note;
- the Python environment can import both `numpy` and `torch`.

Recommended install shape:

```bash
python -m pip install -e /path/to/forward-repo
python -m pip install -e ".[dev]"
```

## Exact Commands For Task 12B

### 1. Generate the medium-scale dataset

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task12_directional_medium_dataset.json
```

Expected primary outputs:

- `outputs/datasets/task12_directional_medium_neural/dataset.json`
- `outputs/runs/task12_directional_medium_dataset_run_metadata.json`

### 2. Train the neural surrogate

```bash
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task12_directional_neural_medium.json
```

Expected primary outputs:

- `outputs/checkpoints/task12_directional_neural_medium/model.pt`
- `outputs/checkpoints/task12_directional_neural_medium/metrics.json`
- `outputs/checkpoints/task12_directional_neural_medium/model_card.md`
- `outputs/runs/task12_directional_neural_medium_run_metadata.json`

### 3. Evaluate the neural surrogate

```bash
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task12_directional_neural_evaluation_medium.json
```

Expected primary outputs:

- `outputs/runs/task12_directional_neural_evaluation_medium/evaluation_report.json`
- `outputs/runs/task12_directional_neural_evaluation_medium/evaluation_report.md`
- `outputs/runs/task12_directional_neural_evaluation_medium_run_metadata.json`

## Compact Artifacts To Return To GitHub

Return only compact review artifacts. At minimum, commit back:

- `configs/datasets/task12_directional_medium_dataset.json`
- `configs/surrogate/task12_directional_neural_medium.json`
- `configs/surrogate/task12_directional_neural_evaluation_medium.json`
- `outputs/runs/task12_directional_medium_dataset_run_metadata.json`
- `outputs/checkpoints/task12_directional_neural_medium/metrics.json`
- `outputs/checkpoints/task12_directional_neural_medium/model_card.md`
- `outputs/runs/task12_directional_neural_medium_run_metadata.json`
- `outputs/runs/task12_directional_neural_evaluation_medium/evaluation_report.json`
- `outputs/runs/task12_directional_neural_evaluation_medium/evaluation_report.md`
- `outputs/runs/task12_directional_neural_evaluation_medium_run_metadata.json`
- `outputs/runs/task12_neural_medium_server_run_note.md`
- compact dataset family metadata, or the full manifest if still reviewable

Returned Task 12B artifacts will be reviewed locally against the ridge baseline
on held-out RMSE, held-out max absolute error, unsafe fraction, and regime
reports before any later large-scale contract can be promoted.

## Heavy Artifacts That Should Stay On The Server

Keep these on the server unless a later task explicitly promotes a compact
canonical sample:

- `outputs/datasets/task12_directional_medium_neural/forward_outputs/`
- `outputs/checkpoints/task12_directional_neural_medium/model.pt`
- any copied forward-output directories
- any large raw spectra collections

## Required Server Run Note

Create `outputs/runs/task12_neural_medium_server_run_note.md` on the server and
return it to GitHub. It should record:

- forward repository commit used
- training repository commit used
- exact commands run
- output directories used
- whether the full dataset manifest or a compact family metadata artifact was returned

## Review Boundary

Task 12B is not complete when the server commands finish. It is complete only
after the compact returned artifacts are committed back to GitHub and reviewed
locally for frozen forward-family consistency, schema correctness, naming,
direction-regime compliance, and meaningful comparison against the ridge
baseline.
