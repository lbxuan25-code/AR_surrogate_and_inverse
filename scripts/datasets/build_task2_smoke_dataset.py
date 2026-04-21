"""Generate the Task 2 deterministic smoke dataset."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("MPLCONFIGDIR", "/tmp/ar_inverse_matplotlib")

LOCAL_SRC = REPO_ROOT / "src"
local_src_text = str(LOCAL_SRC)
if local_src_text not in sys.path:
    sys.path.insert(0, local_src_text)

from ar_inverse.datasets.build import build_task2_smoke_dataset
from ar_inverse.forward_dependency import ForwardDependencyError


def main() -> None:
    try:
        manifest_path, run_metadata_path = build_task2_smoke_dataset()
    except ForwardDependencyError as exc:
        raise SystemExit(f"Forward dependency setup error: {exc}") from None
    print(manifest_path)
    print(run_metadata_path)


if __name__ == "__main__":
    main()
