"""Dataset generation CLI for forward-backed datasets."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("MPLCONFIGDIR", "/tmp/ar_inverse_matplotlib")

LOCAL_SRC = REPO_ROOT / "src"
local_src_text = str(LOCAL_SRC)
if local_src_text not in sys.path:
    sys.path.insert(0, local_src_text)

from ar_inverse.datasets.build import (
    DEFAULT_TASK3_SMOKE_CONFIG_PATH,
    DEFAULT_TASK3_SMOKE_DATASET_DIR,
    DEFAULT_TASK3_SMOKE_RUN_METADATA_PATH,
    build_dataset_from_config,
)
from ar_inverse.forward_dependency import ForwardDependencyError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a dataset through the external forward interface.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_TASK3_SMOKE_CONFIG_PATH,
        help="JSON dataset generation config.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_TASK3_SMOKE_DATASET_DIR,
        help="Directory for the dataset manifest and forward-output payloads.",
    )
    parser.add_argument(
        "--run-metadata",
        type=Path,
        default=DEFAULT_TASK3_SMOKE_RUN_METADATA_PATH,
        help="Path for local run metadata.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate all rows instead of reusing completed manifest entries.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        manifest_path, run_metadata_path = build_dataset_from_config(
            args.config,
            output_dir=args.output_dir,
            run_metadata_path=args.run_metadata,
            force=args.force,
        )
    except ForwardDependencyError as exc:
        raise SystemExit(f"Forward dependency setup error: {exc}") from None
    print(manifest_path)
    print(run_metadata_path)


if __name__ == "__main__":
    main()
