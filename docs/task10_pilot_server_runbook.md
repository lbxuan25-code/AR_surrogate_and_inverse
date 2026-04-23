# Task 10 Pilot Server Runbook

Task 10A prepares the canonical pilot configs and the server handoff only.
Task 10B is the actual server run. Do not generate the pilot dataset, train the
pilot surrogate, or run pilot evaluation in the local Codex workspace.

## Canonical Configs

- Dataset config: `configs/datasets/task10_directional_pilot_dataset.json`
- Training config: `configs/surrogate/task10_directional_surrogate_pilot.json`
- Evaluation config: `configs/surrogate/task10_directional_evaluation_pilot.json`

These configs define one small non-smoke pilot family that includes only:

- `inplane_100`, no spread
- `inplane_110`, no spread
- narrow named-mode-centered spread around supported named modes

They explicitly exclude:

- `c_axis`
- generic raw-angle primary training data
- experiment-side direction mixtures

## Split Workflow

- Local Codex prepares configs, docs, and lightweight validation only.
- GitHub is the handoff boundary.
- The server performs dataset generation, training, and evaluation.
- Only compact review artifacts should return to GitHub.
- Heavy artifacts should stay on the server unless a later task explicitly asks
  for a compact canonical sample.

## Server Preconditions

Run from the repository root on the server after:

- the external forward repository is installed and importable as `forward`, or
  `LNO327_FORWARD_SRC` / `LNO327_FORWARD_REPO` points to it;
- this repository is on the exact Git commit that contains the Task 10A configs
  and this runbook;
- the Python environment can run the existing CLI entry points.

Recommended install shape:

```bash
python -m pip install -e /path/to/forward-repo
python -m pip install -e ".[dev]"
```

## Exact Commands

### 1. Generate the pilot dataset

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task10_directional_pilot_dataset.json
```

Expected primary outputs:

- `outputs/datasets/task10_directional_pilot/dataset.json`
- `outputs/runs/task10_directional_dataset_run_metadata.json`

### 2. Train the pilot surrogate

```bash
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task10_directional_surrogate_pilot.json
```

Expected primary outputs:

- `outputs/checkpoints/task10_directional_surrogate_pilot/model.npz`
- `outputs/checkpoints/task10_directional_surrogate_pilot/metrics.json`
- `outputs/checkpoints/task10_directional_surrogate_pilot/model_card.md`
- `outputs/runs/task10_directional_surrogate_pilot_run_metadata.json`

### 3. Evaluate the pilot surrogate

```bash
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task10_directional_evaluation_pilot.json
```

Expected primary outputs:

- `outputs/runs/task10_directional_evaluation_pilot/evaluation_report.json`
- `outputs/runs/task10_directional_evaluation_pilot/evaluation_report.md`
- `outputs/runs/task10_directional_evaluation_pilot_run_metadata.json`

## Compact Artifacts To Return To GitHub

Return only compact review artifacts. At minimum, commit back:

- `configs/datasets/task10_directional_pilot_dataset.json`
- `configs/surrogate/task10_directional_surrogate_pilot.json`
- `configs/surrogate/task10_directional_evaluation_pilot.json`
- `outputs/datasets/task10_directional_pilot/dataset.json`
- `outputs/runs/task10_directional_dataset_run_metadata.json`
- `outputs/checkpoints/task10_directional_surrogate_pilot/metrics.json`
- `outputs/checkpoints/task10_directional_surrogate_pilot/model_card.md`
- `outputs/runs/task10_directional_surrogate_pilot_run_metadata.json`
- `outputs/runs/task10_directional_evaluation_pilot/evaluation_report.json`
- `outputs/runs/task10_directional_evaluation_pilot/evaluation_report.md`
- `outputs/runs/task10_directional_evaluation_pilot_run_metadata.json`
- `outputs/runs/task10_pilot_server_run_note.md`

If `outputs/datasets/task10_directional_pilot/dataset.json` is unexpectedly too
large for the review flow, return a compact manifest substitute that still
proves:

- `ar_inverse_dataset_row_v2` row usage
- preserved direction blocks
- preserved forward provenance
- supported named modes plus narrow spread only

## Heavy Artifacts That Should Stay On The Server

Keep these on the server unless a later task explicitly promotes a compact
canonical sample:

- `outputs/datasets/task10_directional_pilot/forward_outputs/`
- `outputs/checkpoints/task10_directional_surrogate_pilot/model.npz`
- any copied forward-output directories
- any large raw spectra collections

## Required Server Run Note

Create `outputs/runs/task10_pilot_server_run_note.md` on the server and return
it to GitHub. It should record:

- forward repository commit used
- training repository commit used
- exact commands run
- output directories used
- whether the dataset manifest or a compact substitute was returned

## Review Boundary

Task 10B is not complete when the server commands finish. It is complete only
after the compact returned artifacts are committed back to GitHub and reviewed
locally for schema, naming, forward-metadata-family, and direction-regime
consistency.
