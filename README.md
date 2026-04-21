# AR Surrogate And Inverse

Training, surrogate, inverse-search, and experiment-fitting orchestration for
LNO327 Andreev-reflection workflows.

This repository is not the forward-physics source of truth. It depends on the
external LNO327 AR forward truth chain through its stable `forward` interface.
It does not copy or reimplement forward physics code.

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

You can also set `LNO327_FORWARD_REPO=/path/to/forward-repo`; the loader will
use its `src` directory. The normal package import is tried first, and source
paths are added only when one of these environment variables is explicitly set.

If the forward interface is unavailable, commands fail with an actionable
`ForwardDependencyError` explaining that you must install the forward repository
or set `LNO327_FORWARD_SRC` / `LNO327_FORWARD_REPO`. See
[docs/forward_dependency_setup.md](docs/forward_dependency_setup.md) for the
full setup note.

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
