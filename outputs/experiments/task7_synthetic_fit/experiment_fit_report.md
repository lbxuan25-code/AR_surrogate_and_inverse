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

## Direction Priors And Regimes

Direction priors and candidate direction regimes are reported separately from pairing controls and transport nuisance controls.

- Experiment direction prior: `direction_biased`

## Candidate Feature Families

### compatible_train_like_000

- Fit score: `0.0035651158`
- Pairing controls: `{'delta_perp_x': -0.08, 'delta_zz_s': 0.18}`
- Transport nuisance controls: `{'barrier_z': 0.5, 'gamma': 1.0, 'nk': 11, 'temperature_kelvin': 3.0}`
- Direction regime: `inplane_100_no_spread`
- Forward metadata commit: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`

### nearby_barrier_shift_001

- Fit score: `0.035887345`
- Pairing controls: `{'delta_perp_x': -0.06, 'delta_zz_s': 0.16}`
- Transport nuisance controls: `{'barrier_z': 0.55, 'gamma': 1.0, 'nk': 11, 'temperature_kelvin': 3.0}`
- Direction regime: `inplane_100_no_spread`
- Forward metadata commit: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`

## Surrogate Uncertainty

No surrogate-only claim is made; candidate scores use direct-forward recheck payloads.

## Final Forward Recheck Results

Candidate scores above are based on direct-forward recheck spectra from the
external forward interface.
