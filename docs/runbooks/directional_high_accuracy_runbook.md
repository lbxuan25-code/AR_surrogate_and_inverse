# Task 13 High-Accuracy Large-Scale Server Handoff

Task 13A completed on 2026-04-23 and this note is now the active canonical
runbook for Task 13B, the first high-accuracy heavy server run.
Do not launch the large-scale dataset generation, heavy training, or heavy
evaluation in the local Codex workspace.

## Canonical Configs

- Dataset config: `configs/datasets/task13_directional_large_accuracy_dataset.json`
- High-accuracy training config:
  `configs/surrogate/task13_directional_high_accuracy_large.json`
- High-accuracy evaluation config:
  `configs/surrogate/task13_directional_high_accuracy_evaluation_large.json`

These configs define the first large-scale accuracy-driven contract:

- exactly `4096` rows
- `3072 / 512 / 512` train / validation / test split
- supported named modes only: `inplane_100`, `inplane_110`
- narrow named-mode-centered spread only
- fixed bias grid: `[-20, 20] meV`, `121` points
- fixed `nk`: `41`
- explicit transport-regime quotas across all low/high barrier, gamma, and
  temperature bins

They explicitly exclude:

- `c_axis`
- diagnostic raw-angle primary rows
- arbitrary or wide spread
- experiment-side direction mixtures in the surrogate truth dataset

## Frozen Forward Metadata Family

The Task 13 contract keeps the same frozen forward metadata family accepted in
Task 12B:

- `forward_interface_version`: `ar_forward_v1`
- `output_schema_version`: `ar_forward_output_v1`
- `pairing_convention_id`: `round2_physical_channels_task_h_fit_layer_v1`
- `formal_baseline_record`: `outputs/source/round2_baseline_selection.json`
- `formal_baseline_selection_rule`: `temperature sweep RMFT pairing data, charge-balanced p≈0 branch, temperature_eV <= 1.0e-3, first 8 samples sorted by temperature`
- `git_commit`: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`
- `git_dirty`: `false`

The Task 13B server run is out of contract if returned artifacts identify a
different forward metadata family.

## Frozen Direction Contract

The direction contract remains unchanged:

- direction schema version: `ar_inverse_direction_v1`
- truth-grade named modes: `inplane_100`, `inplane_110`
- spread rule: narrow named-mode-centered spread only, `half_width <= pi/32`
- unsupported mode: `c_axis`
- diagnostic raw angles: excluded from this Task 13 contract

## High-Accuracy Neural Stack Contract

Task 13 upgrades the neural stack while preserving the current feature meaning
and full-spectrum output contract:

- plain Task 12 MLP path remains as a comparator path in the repository
- canonical heavy path uses
  `neural_residual_mlp_spectrum_surrogate`
- residual depth-stabilized feed-forward blocks
- `LayerNorm` support
- composite loss with weighted reconstruction and first-difference shape term
- ensemble-capable checkpoint/output wiring

The current committed Task 13A config freezes one pre-launch canonical contract
for code and wiring validation. Per the current project instruction, the final
launch-only heavy hyperparameter pinning and disagreement-trigger threshold
values may still receive a pre-Task-13B run-note addendum before the actual
server launch.

## Uncertainty Contract

The Task 13A evaluation path now supports:

- ensemble manifest checkpoints
- per-spectrum disagreement summaries
- row-level `mean_std` and `max_std` reporting
- uncertainty diagnostics in evaluation artifacts

Current Task 13B launch policy:

- disagreement summaries must be produced for every held-out spectrum
- the Task 13B launch addendum exists at
  `docs/runbooks/directional_high_accuracy_launch_addendum.md`
- disagreement-trigger thresholds are fixed to `mean_std = 0.005` and
  `max_std = 0.025`
- held-out rows above either disagreement threshold must be marked
  `direct-forward-required`
- error-based fallback remains active through the configured held-out error
  thresholds

## Task 13B Launch Addendum

The Task 13B pre-launch addendum is now committed:

- `docs/runbooks/directional_high_accuracy_launch_addendum.md`
- the evaluation config no longer uses a pending disagreement threshold state
- the fixed pre-launch disagreement thresholds are `mean_std = 0.005` and
  `max_std = 0.025`
- the server run must use
  `configs/surrogate/task13_directional_high_accuracy_evaluation_large.json`
  after this addendum

## Server Preconditions

Run from the repository root on the server after:

- the external forward repository is installed and importable as `forward`, or
  `LNO327_FORWARD_SRC` / `LNO327_FORWARD_REPO` points to it
- the external forward repository working tree is clean enough that emitted
  metadata should report `git_dirty: false`
- this repository is on the exact Git commit that contains the Task 13A
  configs and this handoff note
- the Python environment can import both `numpy` and `torch`

Recommended install shape:

```bash
python -m pip install -e /path/to/forward-repo
python -m pip install -e ".[dev]"
```

## Exact Commands For Task 13B

### 1. Generate the large-scale dataset

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task13_directional_large_accuracy_dataset.json
```

Expected primary outputs:

- `outputs/datasets/task13_directional_large_accuracy/dataset.json`
- `outputs/runs/task13_directional_large_accuracy_dataset_run_metadata.json`

### 2. Train the high-accuracy surrogate / ensemble

```bash
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task13_directional_high_accuracy_large.json
```

Expected primary outputs:

- `outputs/checkpoints/task13_directional_high_accuracy_large/ensemble_manifest.json`
- `outputs/checkpoints/task13_directional_high_accuracy_large/metrics.json`
- `outputs/checkpoints/task13_directional_high_accuracy_large/model_card.md`
- `outputs/runs/task13_directional_high_accuracy_large_run_metadata.json`

### 3. Evaluate the high-accuracy surrogate / ensemble

```bash
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task13_directional_high_accuracy_evaluation_large.json
```

Expected primary outputs:

- `outputs/runs/task13_directional_high_accuracy_evaluation_large/evaluation_report.json`
- `outputs/runs/task13_directional_high_accuracy_evaluation_large/evaluation_report.md`
- `outputs/runs/task13_directional_high_accuracy_evaluation_large_run_metadata.json`

## Compact Artifacts To Return To GitHub

Return only compact review artifacts. At minimum, commit back:

- `configs/datasets/task13_directional_large_accuracy_dataset.json`
- `configs/surrogate/task13_directional_high_accuracy_large.json`
- `configs/surrogate/task13_directional_high_accuracy_evaluation_large.json`
- `outputs/runs/task13_directional_large_accuracy_dataset_run_metadata.json`
- `outputs/checkpoints/task13_directional_high_accuracy_large/metrics.json`
- `outputs/checkpoints/task13_directional_high_accuracy_large/model_card.md`
- `outputs/runs/task13_directional_high_accuracy_large_run_metadata.json`
- `outputs/runs/task13_directional_high_accuracy_evaluation_large/evaluation_report.json`
- `outputs/runs/task13_directional_high_accuracy_evaluation_large/evaluation_report.md`
- `outputs/runs/task13_directional_high_accuracy_evaluation_large_run_metadata.json`
- `outputs/runs/task13_high_accuracy_large_server_run_note.md`
- compact dataset family metadata, or the full manifest if still reviewable

Returned Task 13B artifacts must still be reviewed locally against:

- the committed ridge baseline
- the committed Task 12 plain neural baseline
- the returned Task 13 heavy high-accuracy result

## Heavy Artifacts That Should Stay On The Server

Keep these on the server unless a later task explicitly promotes a compact
canonical sample:

- `outputs/datasets/task13_directional_large_accuracy/forward_outputs/`
- `outputs/checkpoints/task13_directional_high_accuracy_large/members/`
- any copied forward-output directories
- any large raw spectra collections

## Required Server Run Note

Create `outputs/runs/task13_high_accuracy_large_server_run_note.md` on the
server and return it to GitHub. It should record:

- forward repository commit used
- training repository commit used
- exact commands run
- output directories used
- whether the full dataset manifest or a compact family metadata artifact was returned
- confirmation that the committed Task 13B launch addendum was used for the
  evaluation config and disagreement-trigger thresholds

## Review Boundary

Task 13B is not complete when the server commands finish. It is complete only
after the compact returned artifacts are committed back to GitHub and reviewed
locally for frozen forward-family consistency, schema correctness, naming,
direction-regime compliance, uncertainty-aware reporting, and meaningful
comparison against the existing ridge and Task 12 plain-neural baselines.
