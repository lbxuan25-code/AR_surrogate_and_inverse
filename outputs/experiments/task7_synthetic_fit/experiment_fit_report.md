# Task 7 Synthetic Experiment Fit Report

The AR data are compatible with these feature families. This report does not
claim a unique microscopic RMFT point.

## Experiment

- Experiment id: `synthetic_task7_forward_perturbation_v1`
- Source: `outputs/experiments/task7_synthetic_fit/synthetic_experiment_spectrum.json`

## Experimental Preprocessing

- `identity`: Synthetic smoke data are already on the forward bias grid and conductance scale.

## Transport Nuisance Controls

Transport controls are nuisance parameters and are reported separately from pairing controls.

## Candidate Feature Families

### compatible_train_like_000

- Fit score: `0.0035651158`
- Pairing controls: `{'delta_perp_x': -0.08, 'delta_zz_s': 0.18}`
- Transport nuisance controls: `{'barrier_z': 0.5, 'gamma': 1.0, 'interface_angle': 0.0, 'nk': 11, 'temperature_kelvin': 3.0}`
- Forward metadata commit: `4e4c935d1f123c03ee2250f8624d5df3c2c7ebe3`

### nearby_barrier_shift_001

- Fit score: `0.036384252`
- Pairing controls: `{'delta_perp_x': -0.06, 'delta_zz_s': 0.16}`
- Transport nuisance controls: `{'barrier_z': 0.55, 'gamma': 1.0, 'interface_angle': 0.02, 'nk': 11, 'temperature_kelvin': 3.0}`
- Forward metadata commit: `4e4c935d1f123c03ee2250f8624d5df3c2c7ebe3`

## Surrogate Uncertainty

No surrogate-only claim is made; candidate scores use direct-forward recheck payloads.

## Final Forward Recheck Results

Candidate scores above are based on direct-forward recheck spectra from the
external forward interface.
