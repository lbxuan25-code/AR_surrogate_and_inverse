"""Build the Task 7 experiment-fitting report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_SRC = REPO_ROOT / "src"
local_src_text = str(LOCAL_SRC)
if local_src_text not in sys.path:
    sys.path.insert(0, local_src_text)

from ar_inverse.experiments.report import DEFAULT_TASK7_CONFIG_PATH, build_experiment_fit_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a synthetic experiment-fitting report.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_TASK7_CONFIG_PATH,
        help="JSON experiment-fitting config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_path, markdown_path = build_experiment_fit_report(args.config)
    print(report_path)
    print(markdown_path)


if __name__ == "__main__":
    main()
