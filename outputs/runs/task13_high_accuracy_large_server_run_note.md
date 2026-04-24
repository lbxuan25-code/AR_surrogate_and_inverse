# Task 13 High-Accuracy Large Server Run Note

- Date: 2026-04-24T10:01:49+00:00
- Forward repository commit used: b85a5cb304acbfd5d51133251ef57293bd0abd2b
- Training repository commit used: 7f05597fbbbfce61f071ce3219ec60118e4dd0b2

## Exact Commands Run

python scripts/datasets/build_dataset.py --config configs/datasets/task13_directional_large_accuracy_dataset.json
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task13_directional_high_accuracy_large.json
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task13_directional_high_accuracy_evaluation_large.json

## Dataset Generation

- outputs/datasets/task13_directional_large_accuracy/dataset.json
- outputs/runs/task13_directional_large_accuracy_dataset_run_metadata.json
- generated_rows = 4096
- reused_rows = 0
- split = 3072 train / 512 validation / 512 test

## Launch Addendum Used

- docs/task13_high_accuracy_large_launch_addendum.md
- mean_std = 0.005
- max_std = 0.025

## Output Directories Used

- outputs/datasets/task13_directional_large_accuracy
- outputs/checkpoints/task13_directional_high_accuracy_large
- outputs/runs/task13_directional_high_accuracy_evaluation_large

## Returned Artifact Repair

The Task 13B evaluation JSON was checked after repair and is non-empty valid
JSON:

- outputs/runs/task13_directional_high_accuracy_evaluation_large/evaluation_report.json
- size = 4153997 bytes
- held_out_rows = 1024
- unsafe_fraction = 0.0
- high_disagreement_fraction = 0.0

## Heavy Artifacts Kept On Server

- outputs/datasets/task13_directional_large_accuracy/forward_outputs/
- outputs/checkpoints/task13_directional_high_accuracy_large/members/
