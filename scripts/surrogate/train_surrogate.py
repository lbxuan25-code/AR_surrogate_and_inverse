"""Train the first surrogate baseline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_SRC = REPO_ROOT / "src"
local_src_text = str(LOCAL_SRC)
if local_src_text not in sys.path:
    sys.path.insert(0, local_src_text)

from ar_inverse.surrogate.train import DEFAULT_TASK4_CONFIG_PATH, train_surrogate_from_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the Task 4 surrogate baseline.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_TASK4_CONFIG_PATH,
        help="JSON surrogate training config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checkpoint_path, metrics_path, model_card_path = train_surrogate_from_config(args.config)
    print(checkpoint_path)
    print(metrics_path)
    print(model_card_path)


if __name__ == "__main__":
    main()
