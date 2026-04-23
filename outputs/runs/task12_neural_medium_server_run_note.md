# Task 12 Neural Medium Server Run Note

- Date: 2026-04-23T14:48:50+00:00
- Forward repository commit used: b85a5cb304acbfd5d51133251ef57293bd0abd2b
- Training repository commit used: faf28fe8f6e709843d5ea4d2e273f44b271fe8f9

## Exact Commands Run

python scripts/datasets/build_dataset.py --config configs/datasets/task12_directional_medium_dataset.json
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task12_directional_neural_medium.json
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task12_directional_neural_evaluation_medium.json

## Output Directories Used

- outputs/datasets/task12_directional_medium_neural
- outputs/checkpoints/task12_directional_neural_medium
- outputs/runs/task12_directional_neural_evaluation_medium

## Returned Artifact Choice

- Returned full dataset manifest: outputs/datasets/task12_directional_medium_neural/dataset.json
- Heavy artifacts kept on server:
  - outputs/datasets/task12_directional_medium_neural/forward_outputs/
  - outputs/checkpoints/task12_directional_neural_medium/model.pt
