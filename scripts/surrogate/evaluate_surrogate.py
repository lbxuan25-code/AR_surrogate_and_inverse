"""Evaluate a direction-aware surrogate smoke checkpoint."""

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

from ar_inverse.surrogate.evaluate import DEFAULT_DIRECTIONAL_EVALUATION_CONFIG_PATH, evaluate_surrogate_from_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate the Task 9 directional surrogate smoke report.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_DIRECTIONAL_EVALUATION_CONFIG_PATH,
        help="JSON surrogate evaluation config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_path, markdown_path = evaluate_surrogate_from_config(args.config)
    print(report_path)
    print(markdown_path)


if __name__ == "__main__":
    main()
