# AR Surrogate And Inverse

Training, surrogate, inverse-search, and experiment-fitting orchestration for
LNO327 Andreev-reflection workflows.

This repository is not the forward-physics source of truth. It depends on the
external LNO327 AR forward truth chain through its stable `forward` interface.

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
