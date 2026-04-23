# Task 10 Pilot Server Run Note

- Date: 2026-04-23T11:33:04+00:00
- Forward repository commit used: b85a5cb304acbfd5d51133251ef57293bd0abd2b
- Training repository commit used: ffb0802a3d98cb3b1ec326d4ada4d6445c3b3049

## Exact Commands Run

python scripts/datasets/build_dataset.py --config configs/datasets/task10_directional_pilot_dataset.json --force
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task10_directional_surrogate_pilot.json
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task10_directional_evaluation_pilot.json
