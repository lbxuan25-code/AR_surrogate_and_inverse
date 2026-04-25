# TODO

## Current Task

### Task 15B — Manual server run: inverse-ready medium surrogate validation

#### Task type
Manual server task only. Codex must not execute it locally.

#### Goal
Execute the frozen Task 15A inverse-ready medium contract on the server and
return compact review artifacts to GitHub for local acceptance review.

#### Exact configs to run
The server run must use exactly:

- `configs/datasets/task15_inverse_ready_medium_dataset.json`
- `configs/surrogate/task15_inverse_ready_medium_training.json`
- `configs/surrogate/task15_inverse_ready_medium_evaluation.json`
- `docs/task15_inverse_ready_medium_handoff.md`

#### Required returned artifacts
The server run is not reviewable until GitHub contains:

- `outputs/datasets/task15_inverse_ready_medium/dataset.json`
- `outputs/runs/task15_inverse_ready_medium_dataset_run_metadata.json`
- `outputs/checkpoints/task15_inverse_ready_medium/ensemble_manifest.json`
- `outputs/checkpoints/task15_inverse_ready_medium/metrics.json`
- `outputs/checkpoints/task15_inverse_ready_medium/model_card.md`
- `outputs/runs/task15_inverse_ready_medium_training_run_metadata.json`
- `outputs/runs/task15_inverse_ready_medium_evaluation/evaluation_report.json`
- `outputs/runs/task15_inverse_ready_medium_evaluation/evaluation_report.md`
- `outputs/runs/task15_inverse_ready_medium_evaluation_run_metadata.json`
- `outputs/runs/task15_inverse_ready_medium_server_run_note.md`

#### Acceptance checklist
- [ ] server run completed with the exact frozen Task 15A contract
- [ ] compact returned artifacts are committed back to GitHub
- [ ] local review confirms the returned artifacts are internally consistent
- [ ] local review compares held-out results against the committed baseline families

#### Promotion rule
Only after Task 15B is accepted may later inverse or reporting tasks be promoted.

---

## Archive

### Task 15A — Freeze the inverse-ready medium-scale contract

Completed 2026-04-25.

#### Task type
Local Codex task only.

#### Goal
Freeze the first inverse-ready medium-scale contract by combining:
- full gauge-fixed 7+1 pairing representation,
- RMFT-anchor pairing source,
- bias40 probe range,
- expanded nuisance domain,
- TB pilot coordinates,
- and the unchanged current truth-grade direction contract.

#### Fixed target scale
Codex completed the canonical inverse-ready medium row budget:
- total rows: `9600`
- train rows: `7680`
- validation rows: `960`
- test rows: `960`

#### Fixed files
Codex completed the required fixed files:
- `configs/datasets/task15_inverse_ready_medium_dataset.json`
- `configs/surrogate/task15_inverse_ready_medium_training.json`
- `configs/surrogate/task15_inverse_ready_medium_evaluation.json`
- `docs/task15_inverse_ready_medium_handoff.md`
- `tests/test_task15_inverse_ready_medium_contract.py`

#### Required local validation
Allowed lightweight validation completed:
- `pytest tests/test_task15_inverse_ready_medium_contract.py -q`

#### Acceptance checklist
- [x] the inverse-ready medium contract is frozen
- [x] exact row budget is explicit
- [x] the current truth-grade direction contract remains explicit
- [x] no heavy local outputs were created

#### Verification
- The canonical medium dataset contract now exists at
  `configs/datasets/task15_inverse_ready_medium_dataset.json`.
- The canonical medium training contract now exists at
  `configs/surrogate/task15_inverse_ready_medium_training.json`.
- The canonical medium evaluation contract now exists at
  `configs/surrogate/task15_inverse_ready_medium_evaluation.json`.
- The canonical handoff note now exists at
  `docs/task15_inverse_ready_medium_handoff.md`.
- The lightweight contract test now exists at
  `tests/test_task15_inverse_ready_medium_contract.py`.
- The exact row budget is frozen as:
  `9600 total`,
  `7680 train`,
  `960 validation`,
  `960 test`.
- The medium contract explicitly preserves:
  the RMFT anchor / neighborhood / bridge pairing source,
  the projected 7+1 pairing representation,
  the `[-40, 40] meV` / `241`-point spectrum contract,
  the widened nuisance-domain contract,
  the five-coordinate TB pilot contract,
  and the supported truth-grade direction modes
  `inplane_100` / `inplane_110` plus narrow named-mode-centered spread.
- The handoff note records the exact server commands, expected output paths,
  returned review artifacts, and heavy-artifact boundary for Task 15B.
- Lightweight validation passed:
  `tests/test_task15_inverse_ready_medium_contract.py` (`3 passed`).

---

### Task 14E — Add a low-dimensional TB pilot contract without heavy hard constraints

Completed 2026-04-24.

#### Task type
Local Codex task only.

#### Goal
Prepare a first TB-variation contract that no longer freezes the normal state,
but also does not yet impose heavy hard-constraint screening.

#### Fixed TB latent coordinates
Codex completed the canonical five-coordinate TB pilot contract:

- `mu_shift`
- `bandwidth_scale`
- `interlayer_scale`
- `orbital_splitting_shift`
- `hybridization_scale`

No additional TB coordinates were introduced.
No strong band-topology or Fermi-surface hard filters were introduced.

#### Fixed files
Codex completed the required fixed files:
- `docs/task14_tb_pilot_contract.md`
- `configs/datasets/task14_tb_pilot_dataset.json`
- `tests/test_task14_tb_pilot_contract.py`

#### Required local validation
Allowed lightweight validation completed:
- `pytest tests/test_task14_tb_pilot_contract.py -q`

#### Acceptance checklist
- [x] the five TB pilot coordinates are explicit
- [x] no strong heavy hard constraints were introduced
- [x] no heavy local outputs were created

#### Verification
- The canonical TB pilot note now exists at
  `docs/task14_tb_pilot_contract.md`.
- The canonical TB pilot dataset contract now exists at
  `configs/datasets/task14_tb_pilot_dataset.json`.
- The lightweight TB pilot contract test now exists at
  `tests/test_task14_tb_pilot_contract.py`.
- The fixed TB coordinate-system version is
  `task14_tb_pilot_latent_v1`.
- The exact canonical coordinate set is frozen as:
  `mu_shift`,
  `bandwidth_scale`,
  `interlayer_scale`,
  `orbital_splitting_shift`,
  `hybridization_scale`.
- The canonical TB pilot envelope is frozen as:
  `mu_shift in [-0.35, 0.35]`,
  `bandwidth_scale in [-0.20, 0.20]`,
  `interlayer_scale in [-0.25, 0.25]`,
  `orbital_splitting_shift in [-0.30, 0.30]`,
  `hybridization_scale in [-0.25, 0.25]`.
- The canonical TB pilot split is frozen as:
  `70%` near-baseline band,
  `30%` edge-probe band.
- Only the basic guards
  `solver_stability`,
  `finite_forward_output`,
  and
  `schema_validity`
  are allowed.
- The strong constraints
  `band_topology_filter`,
  `fermi_surface_filter`,
  and
  `manual_phase_diagram_gate`
  are explicitly forbidden.
- Lightweight validation passed:
  `tests/test_task14_tb_pilot_contract.py` (`3 passed`).

---

### Task 14D — Expand nuisance-domain sampling for Z, gamma, and temperature

Completed 2026-04-24.

#### Task type
Local Codex task only.

#### Goal
Replace the old low/high structured nuisance sweep with one explicit continuous
experimental-generality nuisance contract.

#### Fixed target ranges
Codex completed the canonical initial nuisance ranges:

- `barrier_z`: continuous sampling in `[0.10, 1.50]`
- `gamma`: continuous sampling in `[0.40, 1.80]`
- `temperature_kelvin`: continuous sampling in `[1.0, 15.0]`

The completed contract also freezes the two-tier policy:
- dense core region;
- sparse guard-band region.

#### Fixed files
Codex completed the required fixed files:
- `docs/task14_transport_domain_contract.md`
- `tests/test_task14_transport_domain_contract.py`

Codex also updated the sampling code path in
`src/ar_inverse/datasets/sampling.py` so later dataset contracts can reuse the
canonical transport-domain descriptor and core-versus-guard-band classifier.

#### Required local validation
Allowed lightweight validation completed:
- `pytest tests/test_task14_transport_domain_contract.py -q`

#### Acceptance checklist
- [x] nuisance target ranges are explicit
- [x] core vs guard-band policy is explicit
- [x] no heavy local outputs were created

#### Verification
- The canonical transport-domain note now exists at
  `docs/task14_transport_domain_contract.md`.
- The lightweight contract test now exists at
  `tests/test_task14_transport_domain_contract.py`.
- The canonical policy id is fixed as `task14_transport_domain_v1`.
- The exact full nuisance ranges are frozen as:
  `barrier_z in [0.10, 1.50]`,
  `gamma in [0.40, 1.80]`,
  `temperature_kelvin in [1.0, 15.0]`.
- The exact dense-core ranges are frozen as:
  `barrier_z in [0.25, 1.20]`,
  `gamma in [0.55, 1.55]`,
  `temperature_kelvin in [1.5, 10.0]`.
- The exact two-tier split is frozen as:
  `80%` dense core,
  `20%` sparse guard band.
- The sampling helper now exposes
  `task14_transport_domain_contract`
  and
  `classify_task14_transport_region`
  for later dataset contracts.
- Lightweight validation passed:
  `tests/test_task14_transport_domain_contract.py` (`3 passed`).

---

### Task 14C — Probe the expanded bias window contract at [-40, 40] meV

Completed 2026-04-24.

#### Task type
Local Codex preparation first, then manual server run later.

#### Goal
Freeze one probe contract that expands the bias window from the old
`[-20, 20] meV` range to the new canonical probe range:

- `bias_min_mev = -40.0`
- `bias_max_mev = 40.0`
- `num_bias = 241`

This task prepares the probe only. The heavy or medium server run belongs to the
later promoted server task.

#### Fixed files
Codex completed the required local preparation files:
- `configs/datasets/task14_bias40_probe_dataset.json`
- `configs/surrogate/task14_bias40_probe_training.json`
- `configs/surrogate/task14_bias40_probe_evaluation.json`
- `docs/task14_bias40_probe_handoff.md`
- `tests/test_task14_bias40_probe_contract.py`

#### Required local validation
Allowed lightweight validation completed:
- `pytest tests/test_task14_bias40_probe_contract.py -q`

No local dataset generation, no local training, and no local evaluation were
run.

#### Acceptance checklist
- [x] canonical bias40 probe dataset config exists
- [x] canonical bias40 probe training config exists
- [x] canonical bias40 probe evaluation config exists
- [x] handoff note exists
- [x] no heavy local outputs were created

#### Verification
- The canonical probe dataset contract now exists at
  `configs/datasets/task14_bias40_probe_dataset.json`.
- The canonical probe training contract now exists at
  `configs/surrogate/task14_bias40_probe_training.json`.
- The canonical probe evaluation contract now exists at
  `configs/surrogate/task14_bias40_probe_evaluation.json`.
- The canonical handoff note now exists at
  `docs/task14_bias40_probe_handoff.md`.
- All three contracts freeze the widened bias window exactly as:
  `bias_min_mev = -40.0`,
  `bias_max_mev = 40.0`,
  `num_bias = 241`.
- The handoff note clearly records that Task 14C is a preparation-only step
  and that the later server task must execute the exact frozen files.
- Lightweight validation passed:
  `tests/test_task14_bias40_probe_contract.py` (`2 passed`).

---

### Task 14B — Build the RMFT-projected anchor dataset contract

Completed 2026-04-24.

#### Task type
Local Codex task only. Do not run server generation or training in this task.

#### Goal
Freeze one canonical dataset contract whose pairing samples come primarily from:
- original RMFT data points,
- projected into the full 7+1 pairing representation from Task 14A,
- with only global phase removed.

This task must replace the old baseline-neighborhood 5-parameter philosophy as
the canonical source of later inverse-ready training data.

#### Required local changes
Codex completed all required local changes:

1. Added the canonical RMFT-anchor contract config:
   `configs/datasets/task14_rmft_anchor_dataset.json`
2. Added the server-side audit document skeleton:
   `docs/task14_rmft_projection_audit.md`
3. Added the lightweight contract test:
   `tests/test_task14_rmft_anchor_contract.py`
4. Updated the dataset schema note so `ar_inverse_dataset_row_v3` and
   `controls.pairing_representation` are documented in
   `docs/dataset_schema.md`

#### Required local validation
Allowed lightweight checks completed:
- `pytest tests/test_task14_pairing_representation.py tests/test_task14_rmft_anchor_contract.py -q`

#### Acceptance checklist
- [x] one canonical RMFT-anchor dataset config exists
- [x] anchor / neighborhood / bridge sample roles are explicit
- [x] the old baseline-neighborhood path is no longer the canonical pairing source
- [x] full gauge-fixed 7+1 channels are recorded in the schema
- [x] no heavy local outputs were created

#### Verification
- The canonical contract config explicitly freezes `anchor`,
  `neighborhood`, and `bridge` sample roles under the RMFT-projected source
  family.
- The contract explicitly forbids `delta_from_baseline_meV` as the canonical
  main pairing source and forbids symmetry labels as training labels.
- The canonical audit output path is fixed as
  `outputs/runs/task14_rmft_projection_audit.json`.
- The audit skeleton records what the later server-side audit must report for
  representation version, anchor/neighborhood/bridge counts, weak-channel
  statistics, and legacy-path replacement checks.
- Lightweight validation passed:
  `tests/test_task14_pairing_representation.py tests/test_task14_rmft_anchor_contract.py`
  (`7 passed`).

---

### Task 14A — Freeze the complete 7+1 pairing representation contract

Completed 2026-04-24.

#### Task type
Local Codex task only. Do not run server generation or training in this task.

#### Goal
Replace the current baseline-neighborhood 5-parameter fit-layer input contract
with one fixed new pairing input contract for all later inverse-ready work:

- use the full projected complex 7+1 pairing channels;
- remove only the physically meaningless global phase redundancy;
- do not perform any further latent-space or PCA compression;
- do not reintroduce the old 5-parameter baseline-neighborhood control path as
  the canonical training input.

This task defines the new canonical pairing representation before any later
dataset expansion or server run is allowed.

#### Required local changes
Codex completed all required local changes:

1. Added the canonical representation module:
   `src/ar_inverse/pairing/representation.py`
2. Added the pairing contract document:
   `docs/task14_pairing_representation_contract.md`
3. Added the lightweight representation test:
   `tests/test_task14_pairing_representation.py`
4. Updated dataset schema helpers so later manifests can record full
   gauge-fixed 7+1 channels plus metadata under
   `controls.pairing_representation`.

#### Required local validation
Allowed lightweight checks completed:
- `pytest tests/test_task14_pairing_representation.py -q`
- `pytest tests/test_surrogate_training.py tests/test_surrogate_evaluation.py -q`

#### Acceptance checklist
- [x] full projected 7+1 channels are the canonical pairing input contract
- [x] only the global phase redundancy is removed
- [x] no PCA / latent compression is introduced
- [x] gauge-fixing is deterministic and documented
- [x] weak-channel status is preserved in metadata
- [x] representation version is recorded
- [x] local lightweight tests pass
- [x] no heavy local outputs were created

#### Verification
- Canonical representation helpers now exist at
  `src/ar_inverse/pairing/representation.py` with the fixed function names
  `gauge_fix_pairing_channels`,
  `serialize_gauge_fixed_pairing_channels`,
  `deserialize_gauge_fixed_pairing_channels`.
- The canonical version string is fixed as
  `projected_7plus1_gauge_fixed_v1`.
- Dataset rows can now record the serialized gauge-fixed representation under
  `controls.pairing_representation`.
- Pairing-aware dataset rows now use schema version
  `ar_inverse_dataset_row_v3`.
- The deterministic anchor-priority contract and serialized payload shape are
  documented in `docs/task14_pairing_representation_contract.md`.
- Lightweight validation passed:
  `tests/test_task14_pairing_representation.py` (`5 passed`)
  and
  `tests/test_surrogate_training.py tests/test_surrogate_evaluation.py`
  (`11 passed`).

### Task 16A — Manual server benchmark: synthetic inverse identifiability test set

#### Task type
Preparation locally by Codex, execution manually on the server.

#### Goal
Create and run one synthetic inverse benchmark that measures whether the new
inverse-ready surrogate remains identifiable under:
- full gauge-fixed 7+1 pairing inputs,
- TB pilot variation,
- expanded nuisance variation,
- expanded bias window.

#### Fixed local preparation files
Codex must create exactly:
- `configs/experiments/task16_synthetic_inverse_benchmark.json`
- `docs/task16_synthetic_inverse_benchmark_handoff.md`
- `tests/test_task16_synthetic_inverse_benchmark_contract.py`

#### Manual server execution
The user must manually run the benchmark on the server after this task is
promoted and locally prepared.

#### Acceptance checklist
- [ ] benchmark contract is frozen locally
- [ ] benchmark is run manually on the server
- [ ] compact benchmark artifacts are returned
- [ ] local review confirms identifiability diagnostics were produced

#### Promotion rule
Only after Task 16A is complete and reviewed may Task 16B move into Current Task.

---

### Task 16B — Experimental fitting interface under the inverse-ready contract

#### Task type
Local Codex preparation first; later manual server usage.

#### Goal
Prepare the experiment-side fitting interface so experimental spectra are
analyzed as external targets, not used as surrogate training data.

#### Fixed scope
Codex must prepare:
- experiment ingest schema,
- preprocessing metadata hooks,
- surrogate-search plus uncertainty-filter plus direct-forward-recheck workflow,
- but must not claim unsupported microscopic uniqueness.

#### Fixed files
Codex must create exactly:
- `docs/task16_experimental_fitting_interface.md`
- `tests/test_task16_experimental_fitting_interface_contract.py`

#### Acceptance checklist
- [ ] experiment-side interface contract exists
- [ ] no experimental spectra are silently used as training data
- [ ] direct-forward recheck remains mandatory for final candidate claims

---

## Archive

### Task 13B — Launch the first high-accuracy heavy surrogate campaign

Completed 2026-04-24.

See existing repository archive entries for full verification details.

### Task 13A — Freeze the high-accuracy large-scale surrogate contract and upgrade the training stack

Completed 2026-04-23.

See existing repository archive entries for full verification details.

### Task 12B — Run the first medium-scale neural surrogate validation job

Completed 2026-04-23.

See existing repository archive entries for full verification details.

### Task 12A — Prepare the neural surrogate training stack

Completed 2026-04-23.

See existing repository archive entries for full verification details.

### Task 11B — Run the first production server job and return compact review artifacts

Completed 2026-04-23.

### Task 11A — Prepare the production server contract

Completed 2026-04-23.

### Task 10B — Run the pilot on the server and validate the returned artifacts

Completed 2026-04-23.

### Task 10A — Prepare the small non-smoke pilot for server execution

Completed 2026-04-23.

### Task 9 — Complete the direction-aware surrogate smoke training loop

Completed 2026-04-23.

### Task 8 — Integrate the directional feature contract into the surrogate/inverse repository

Completed 2026-04-22.

### Task 7 — Experiment-fitting report workflow

Completed previously.

### Task 6 — Inverse search prototype

Completed previously.

### Task 5 — Surrogate evaluation and calibration

Completed previously.

### Task 4 — Train first surrogate baseline

Completed previously.

### Task 3 — Implement dataset generation orchestration

Completed previously.

### Task 2 — Define dataset schema and sampling policy

Completed previously.

### Task 1 — Bootstrap repository skeleton and forward dependency

Completed previously.
