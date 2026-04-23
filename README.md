# AR Surrogate And Inverse

Training, surrogate, inverse-search, and experiment-fitting orchestration for
LNO327 Andreev-reflection workflows.

This repository is not the forward-physics source of truth. It depends on the
external LNO327 AR forward truth chain through its stable `forward` interface.
It does not copy or reimplement forward physics code.

## Current Stage

- Current TODO task: Task 13B, launch the first high-accuracy heavy surrogate
  campaign on the server using the frozen Task 13 contract.
- Task 13A is complete: the canonical large-scale dataset, training, and
  evaluation contracts are prepared; the residual high-accuracy path, composite
  loss, and ensemble-capable evaluation wiring are now in the repository.
- Task 12B is complete: the first medium-scale neural server validation run
  returned compact review artifacts, preserved the frozen forward and direction
  contracts, and passed local review.
- Task 12A is complete: the first neural surrogate stack, dual-path ridge and
  neural checkpoint wiring, canonical medium-scale dataset config, neural
  training/evaluation configs, and Task 12 handoff note are prepared.
- Task 11B is complete: the first production server-scale dataset generation,
  surrogate training, and evaluation run returned compact review artifacts and
  passed local review under the frozen forward metadata family.
- Task 11A is complete: the canonical production dataset config, training
  config, evaluation config, frozen forward-family contract, and production
  server handoff note are prepared for manual server execution.
- Task 10B is complete: the prepared small non-smoke pilot was run on the
  server, compact review artifacts were returned to GitHub, and local review
  accepted the result.
- Task 10A is complete: the canonical pilot dataset config, training config,
  evaluation config, and server runbook were prepared for manual server
  execution.
- Task 8 is complete: the forward direction contract is integrated into
  dataset rows, feature intake, evaluation reports, inverse configs, and
  experiment reports.
- Task 9 is complete: the direction-aware surrogate smoke training loop runs
  end to end under canonical naming.
- The canonical smoke entry points retained for verification are:
  `configs/datasets/task8_directional_smoke_dataset.json`,
  `configs/surrogate/task9_directional_surrogate_smoke.json`, and
  `configs/surrogate/task9_directional_evaluation_smoke.json`.
- The canonical non-smoke pilot handoff entry points are:
  `configs/datasets/task10_directional_pilot_dataset.json`,
  `configs/surrogate/task10_directional_surrogate_pilot.json`,
  `configs/surrogate/task10_directional_evaluation_pilot.json`, and
  `docs/task10_pilot_server_runbook.md`.
- The canonical production contract entry points are:
  `configs/datasets/task11_directional_production_dataset.json`,
  `configs/surrogate/task11_directional_surrogate_production.json`,
  `configs/surrogate/task11_directional_evaluation_production.json`, and
  `docs/task11_production_server_handoff.md`.
- The canonical Task 12 neural validation entry points are:
  `configs/datasets/task12_directional_medium_dataset.json`,
  `configs/surrogate/task12_directional_neural_medium.json`,
  `configs/surrogate/task12_directional_neural_evaluation_medium.json`, and
  `docs/task12_neural_medium_server_handoff.md`.
- The canonical Task 13 high-accuracy large-scale entry points are:
  `configs/datasets/task13_directional_large_accuracy_dataset.json`,
  `configs/surrogate/task13_directional_high_accuracy_large.json`,
  `configs/surrogate/task13_directional_high_accuracy_evaluation_large.json`,
  and `docs/task13_high_accuracy_large_server_handoff.md`.
- Historical `task3`, `task4`, and `task5` paths are legacy / archived
  baseline names. They remain loadable for compatibility but are not the current
  canonical stage names.

## Forward Dependency Setup

Recommended development setup:

```bash
python -m pip install -e /path/to/forward-repo
python -m pip install -e ".[dev]"
```

After that, this repository imports `forward` as a normal Python package.

Portable environment-variable setup:

```bash
export LNO327_FORWARD_SRC=/path/to/forward-repo/src
python scripts/datasets/build_forward_smoke_payload.py
pytest
```

## Task 2 Smoke Dataset

After configuring the forward dependency, generate the canonical schema smoke
dataset with:

```bash
python scripts/datasets/build_task2_smoke_dataset.py
pytest
```

This writes a tiny deterministic manifest to
`outputs/datasets/task2_smoke_fit_layer/dataset.json`. The rows point to local
forward-output JSON files and record complete forward-interface metadata.

## Legacy Task 3 Dataset CLI

The historical Task 3 dataset config is retained as a legacy orchestration
baseline:

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task3_smoke_dataset.json
```

It writes a resumable manifest to
`outputs/datasets/task3_orchestration_smoke/dataset.json` and run metadata to
`outputs/runs/task3_dataset_generation_run_metadata.json`. Re-running the same
command reuses completed rows when the referenced forward-output file still
matches its recorded SHA-256 digest. Pass `--force` to regenerate all rows.
Use the Task 8 directional config as the current canonical dataset entry.

## Legacy Task 4 Surrogate Baseline

The historical Task 4 filename is retained as a legacy alias. It is superseded
by the Task 9 directional smoke config.

```bash
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task4_linear_surrogate.json
```

This trains a ridge-linear spectrum surrogate from Task 3 fit-layer and
transport controls to conductance spectra. It writes:

- `outputs/checkpoints/task4_linear_surrogate/model.npz`
- `outputs/checkpoints/task4_linear_surrogate/metrics.json`
- `outputs/checkpoints/task4_linear_surrogate/model_card.md`
- `outputs/runs/task4_linear_surrogate_run_metadata.json`

Validation and test metrics are computed on held-out spectra generated by the
external `forward` interface and stored in the Task 3 dataset.

## Legacy Task 5 Surrogate Evaluation

The historical Task 5 filename is retained as a legacy alias. It is superseded
by the Task 9 directional evaluation smoke config.

```bash
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task5_evaluate_linear_surrogate.json
```

This writes:

- `outputs/runs/task5_surrogate_evaluation/evaluation_report.json`
- `outputs/runs/task5_surrogate_evaluation/evaluation_report.md`
- `outputs/runs/task5_surrogate_evaluation_run_metadata.json`

The report groups held-out errors by coarse transport regime and marks regimes
that are unsafe for inverse acceleration. Unsafe or unseen regimes must fall
back to direct calls through the external `forward` interface.

## Task 6 Smoke Inverse Search

Run the smoke inverse-search prototype with:

```bash
python scripts/inverse/run_inverse_search.py --config configs/inverse/task6_smoke_inverse.json
```

This returns candidate families, not a unique microscopic truth claim. Final
candidate scoring is rechecked by direct calls through the external `forward`
interface. Outputs are written to:

- `outputs/inverse/task6_smoke_inverse/inverse_report.json`
- `outputs/inverse/task6_smoke_inverse/inverse_report.md`
- `outputs/inverse/task6_smoke_inverse/forward_rechecks/`
- `outputs/runs/task6_smoke_inverse_run_metadata.json`

## Task 7 Synthetic Experiment Fit

Build the synthetic experiment-fitting smoke report with:

```bash
python scripts/experiments/fit_experiment.py --config configs/experiments/task7_synthetic_experiment.json
```

The report separates experimental preprocessing, transport nuisance controls,
candidate feature-family compatibility, surrogate uncertainty, and final
direct-forward recheck results. It writes:

- `outputs/experiments/task7_synthetic_fit/experiment_fit_report.json`
- `outputs/experiments/task7_synthetic_fit/experiment_fit_report.md`
- `outputs/runs/task7_experiment_fit_run_metadata.json`

You can also set `LNO327_FORWARD_REPO=/path/to/forward-repo`; the loader will
use its `src` directory. The normal package import is tried first, and source
paths are added only when one of these environment variables is explicitly set.

If the forward interface is unavailable, commands fail with an actionable
`ForwardDependencyError` explaining that you must install the forward repository
or set `LNO327_FORWARD_SRC` / `LNO327_FORWARD_REPO`. See
[docs/forward_dependency_setup.md](docs/forward_dependency_setup.md) for the
full setup note.

## Direction Contract

This repository follows the external forward package's directional capability
contract. Supported truth-grade named modes are `inplane_100` and
`inplane_110`. `c_axis` is unsupported and is rejected as a training or inverse
target.

Generic raw `interface_angle` values are caution-only / diagnostic-only. They
are not included in the primary training pool unless a dataset config
explicitly opts in and keeps them separated. Directional spread is supported
only as narrow named-mode-centered spread with `half_width <= pi/32`.

See [docs/direction_contract.md](docs/direction_contract.md) for the local
schema and reporting interpretation.

## Task 8 Direction-Aware Smoke Dataset

Generate the direction-aware smoke manifest with:

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task8_directional_smoke_dataset.json
```

This writes:

- `outputs/datasets/task8_directional_smoke/dataset.json`
- `outputs/runs/task8_directional_dataset_run_metadata.json`

The smoke config exercises `inplane_100` without spread, `inplane_110` without
spread, and one narrow-spread `inplane_110` case. Surrogate training and
evaluation configs now ingest this manifest and use explicit direction
features: named-mode identity, spread controls, and raw angle only as auxiliary
metadata.

## Task 9 Directional Surrogate Smoke Entry

The current naming-clean smoke checkpoint entry is:

```bash
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task9_directional_surrogate_smoke.json
```

It writes:

- `outputs/checkpoints/task9_directional_surrogate_smoke/model.npz`
- `outputs/checkpoints/task9_directional_surrogate_smoke/metrics.json`
- `outputs/checkpoints/task9_directional_surrogate_smoke/model_card.md`
- `outputs/runs/task9_directional_surrogate_smoke_run_metadata.json`

This remains a smoke-scale artifact over the Task 8 directional dataset. It is
not the Task 10 non-smoke pilot dataset/training run and not a server-scale
training expansion.

Evaluate it with:

```bash
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task9_directional_evaluation_smoke.json
```

This writes:

- `outputs/runs/task9_directional_evaluation_smoke/evaluation_report.json`
- `outputs/runs/task9_directional_evaluation_smoke/evaluation_report.md`
- `outputs/runs/task9_directional_evaluation_smoke_run_metadata.json`

## Task 10 Pilot Server Handoff

Task 10A prepared the canonical non-smoke pilot for server execution without
running the pilot locally. Use these committed configs:

- `configs/datasets/task10_directional_pilot_dataset.json`
- `configs/surrogate/task10_directional_surrogate_pilot.json`
- `configs/surrogate/task10_directional_evaluation_pilot.json`

The server handoff note is:

- `docs/task10_pilot_server_runbook.md`

The pilot remains limited to `inplane_100`, `inplane_110`, and narrow
named-mode-centered spread. It excludes `c_axis`, generic raw-angle primary
data, and experiment-side direction mixtures. Dataset generation, training, and
evaluation for this pilot are server-only Task 10B steps; only compact review
artifacts should return to GitHub.

## Task 11 Production Server Handoff

Task 11A prepared the canonical first production contract without launching the
production run locally. Task 11B is the server-run and returned-artifact review
phase. Use these committed configs:

- `configs/datasets/task11_directional_production_dataset.json`
- `configs/surrogate/task11_directional_surrogate_production.json`
- `configs/surrogate/task11_directional_evaluation_production.json`

The production server handoff note is:

- `docs/task11_production_server_handoff.md`

The production contract remains limited to `inplane_100`, `inplane_110`, and
narrow named-mode-centered spread. It explicitly excludes `c_axis`, diagnostic
raw angles, arbitrary or wide mixtures, and experiment-side direction mixtures
in the surrogate truth dataset. It also freezes the forward metadata family
validated in Task 10B; any later server run must return compact artifacts that
identify that same family for local review.

Task 11B completed the first server production run using this contract and
returned compact review artifacts that passed local validation. The returned
manifest kept `ar_inverse_dataset_row_v2`, the supported named modes plus
narrow spread only, and the frozen clean forward metadata family.

## Task 12 Neural Medium-Scale Handoff

Task 12A prepared the first neural surrogate stack and the canonical
medium-scale validation contract without launching the medium-scale run
locally. Task 12B completed the server run and returned-artifact review phase
under this same contract. The canonical configs remain:

- `configs/datasets/task12_directional_medium_dataset.json`
- `configs/surrogate/task12_directional_neural_medium.json`
- `configs/surrogate/task12_directional_neural_evaluation_medium.json`

The neural server handoff note is:

- `docs/task12_neural_medium_server_handoff.md`

The Task 12 neural stack keeps the same structured feature contract as the
ridge baseline, preserves the same frozen direction domain, and adds a simple
feed-forward checkpoint path with explicit optimizer, epoch, batch-size, seed,
and device metadata. The medium-scale dataset contract targets `352` rows and
still excludes `c_axis`, diagnostic raw-angle primary rows, arbitrary wide
spread, and experiment-side direction mixtures.

Task 12B returned compact review artifacts under this contract and passed local
review. The returned neural evaluation reported held-out mean RMSE
`0.0024540644`, max RMSE `0.0075590854`, mean max absolute error
`0.0056677393`, and unsafe fraction `0.0`, while preserving only
`inplane_100`, `inplane_110`, and narrow named-mode-centered spread under the
frozen clean forward metadata family. The handoff note remains the archival
runbook for that completed server task.

## Task 1 Smoke Path

The current bootstrap smoke path:

1. imports the external `forward` package;
2. builds a small fit-layer spectrum request;
3. calls the forward engine through `ar_inverse.forward_client`;
4. verifies finite conductance values and required forward metadata;
5. writes a small example payload under `outputs/datasets/`.

Run it with:

```bash
python scripts/datasets/build_forward_smoke_payload.py
pytest
```
