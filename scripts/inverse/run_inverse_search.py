"""Run the Task 6 smoke inverse-search prototype."""

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

from ar_inverse.forward_dependency import ForwardDependencyError
from ar_inverse.inverse.search import DEFAULT_TASK6_CONFIG_PATH, run_inverse_search_from_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Task 6 smoke inverse-search prototype.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_TASK6_CONFIG_PATH,
        help="JSON inverse-search config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        report_path, markdown_path = run_inverse_search_from_config(args.config)
    except ForwardDependencyError as exc:
        raise SystemExit(f"Forward dependency setup error: {exc}") from None
    print(report_path)
    print(markdown_path)


if __name__ == "__main__":
    main()
