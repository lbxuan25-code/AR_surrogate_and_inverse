# Forward Dependency Setup

This repository consumes the external LNO327 AR forward truth chain only
through its stable Python `forward` interface. It does not vendor, copy, or
reimplement forward physics code.

## Recommended Setup

Install the forward truth-chain repository into the same Python environment in
editable mode:

```bash
python -m pip install -e /path/to/forward-repo
python -m pip install -e ".[dev]"
```

With that setup, this repository can simply import `forward`.

## Environment Variable Setup

If you do not want to install the forward repository, explicitly point this
repository at the forward source tree:

```bash
export LNO327_FORWARD_SRC=/path/to/forward-repo/src
```

Alternatively, point at the forward repository root:

```bash
export LNO327_FORWARD_REPO=/path/to/forward-repo
```

`LNO327_FORWARD_SRC` takes precedence. In both cases, the path must contain the
external `forward` package. The loader never guesses a sibling directory.

## Smoke Test

After either setup, run:

```bash
python scripts/datasets/build_forward_smoke_payload.py
pytest
```

The script should write:

- `outputs/datasets/fit_layer_forward_smoke_payload.json`
- `outputs/runs/task1_forward_smoke_run_metadata.json`

The generated payload must include the forward-interface metadata required by
`AGENTS.md`, including `forward_interface_version`, `output_schema_version`,
`pairing_convention_id`, `formal_baseline_record`,
`formal_baseline_selection_rule`, `projection_config`, `git_commit`, and
`git_dirty`.

## Failure Mode

If the forward interface is not installed and no environment variable is set,
the repository raises `ForwardDependencyError`. The error states that the
external `forward` package is missing, tells you to install the forward
truth-chain repository or set `LNO327_FORWARD_SRC` / `LNO327_FORWARD_REPO`, and
reminds you that this repository will not copy or reimplement forward physics
code.
