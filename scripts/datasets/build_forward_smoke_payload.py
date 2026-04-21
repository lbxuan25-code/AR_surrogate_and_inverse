"""Generate the Task 1 forward-interface smoke payload."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("MPLCONFIGDIR", "/tmp/ar_inverse_matplotlib")

FORWARD_REPO_SRC = REPO_ROOT.parent / "AR" / "src"
for path in (REPO_ROOT / "src", FORWARD_REPO_SRC):
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)

from ar_inverse.forward_client import (
    DEFAULT_SMOKE_PAYLOAD_PATH,
    DEFAULT_SMOKE_RUN_METADATA_PATH,
    write_task1_smoke_artifacts,
)


def main() -> None:
    payload_path, run_metadata_path = write_task1_smoke_artifacts(
        DEFAULT_SMOKE_PAYLOAD_PATH,
        DEFAULT_SMOKE_RUN_METADATA_PATH,
    )
    print(payload_path)
    print(run_metadata_path)


if __name__ == "__main__":
    main()
