# TODO

## Current Task

### Task S4 — Redefine joint sampling across pairing, nuisance, and TB spaces

#### Task type
Local Codex task only.

#### Goal
Define how the repository jointly samples:
- pairing structure,
- nuisance variables,
- and TB variables.

Current contracts freeze ranges and some tier fractions, but do not yet define a
sufficiently rigorous joint sampling strategy.

#### Required work
Codex must complete all of the following:

1. Decide whether nuisance variables are sampled independently or with explicit
   correlations.
2. Decide whether TB and nuisance variables are sampled independently or with
   structured coupling.
3. Specify how widened bias-window training affects where sampling density must
   increase in parameter space.
4. Specify whether `gamma` should use:
   - linear sampling,
   - piecewise sampling,
   - log-density weighting,
   - or another explicit density rule.

#### Fixed output files
Codex must create exactly:
- `docs/joint_sampling_contract.md`
- `tests/test_joint_sampling_contract.py`

#### Required local validation
Codex may run only:
- `pytest tests/test_joint_sampling_contract.py -q`

#### Acceptance checklist
- [ ] the repository has a written joint sampling contract
- [ ] nuisance / TB independence or coupling assumptions are explicit
- [ ] gamma sampling density policy is explicit
- [ ] widened bias-window implications are incorporated
- [ ] no heavy local outputs were created

#### Completion type
This task is directly completable.

#### Promotion rule
Only after Task S4 is complete may Task S5 move into Current Task.

---

## Backlog

### Task S5 — Build the training observability and diagnostics standard

#### Task type
Local Codex task only.

#### Goal
Upgrade the surrogate training pipeline from metrics-only output to a proper
industrial / academic observability standard.

The current training and evaluation outputs are not sufficient for diagnosing:
- underfitting,
- unstable optimization,
- gradient pathologies,
- input-block dominance,
- or regime-specific failure.

#### Required work
Codex must complete all of the following:

1. Freeze the required training curves:
   - train loss,
   - validation loss,
   - reconstruction loss,
   - shape loss,
   - learning-rate curve.

2. Freeze the required optimization diagnostics:
   - per-layer gradient norm summary,
   - parameter update magnitude summary,
   - gradient explosion / vanishing warning logic.

3. Freeze the required sensitivity diagnostics:
   - pairing-block sensitivity,
   - direction-block sensitivity,
   - nuisance-block sensitivity,
   - TB-block sensitivity.

4. Freeze the required prediction-review figures:
   - representative best rows,
   - representative median rows,
   - representative worst rows,
   each with direct-forward versus surrogate spectrum comparison.

5. Freeze the required grouped error outputs:
   - by bias sub-window,
   - by pairing-source role,
   - by nuisance sub-range,
   - by TB regime,
   - by direction regime.

#### Fixed output files
Codex must create exactly:
- `docs/training_observability_standard.md`
- `src/ar_inverse/training/monitoring.py`
- `src/ar_inverse/training/plots.py`
- `tests/test_training_observability_standard.py`

#### Required local validation
Codex may run only:
- `pytest tests/test_training_observability_standard.py -q`

#### Acceptance checklist
- [ ] the repository defines the full observability standard in writing
- [ ] the required curves and diagnostics are frozen
- [ ] grouped error reporting requirements are frozen
- [ ] no heavy local outputs were created

#### Completion type
This task is directly completable.

#### Promotion rule
Only after Task S5 is complete may Task S6 move into Current Task.

---

### Task S6 — Refactor repository layout and naming conventions

#### Task type
Local Codex task only.

#### Goal
Replace the current task-number-driven file sprawl with a stable repository
structure and naming convention that reflects actual content.

#### Required work
Codex must complete all of the following:

1. Define one stable repository layout standard for:
   - configs,
   - docs,
   - outputs,
   - figures,
   - audits,
   - runbooks,
   - and contracts.

2. Define one stable naming convention where file names are based on content and
   role, not primarily on task number.

3. Define one migration plan from the current task-number-heavy structure to the
   new structure.

4. Do not perform large destructive file moves yet unless they are needed for
   the standard itself. This task freezes the standard and migration plan first.

#### Fixed output files
Codex must create exactly:
- `docs/repository_layout_v2.md`
- `docs/naming_convention_v2.md`
- `docs/migration_from_task_named_layout.md`
- `tests/test_repository_layout_standard.py`

#### Required local validation
Codex may run only:
- `pytest tests/test_repository_layout_standard.py -q`

#### Acceptance checklist
- [ ] the repository layout standard exists
- [ ] the naming convention standard exists
- [ ] the migration plan exists
- [ ] no heavy local outputs were created

#### Completion type
This task is directly completable.

#### Promotion rule
Only after Task S6 is complete may Task S7 move into Current Task.

---

### Task S7 — Diagnose whether model capacity changes are actually needed

#### Task type
Observation-dependent local Codex task.

#### Goal
Do not change model depth or width by intuition alone.
Use the observability outputs from Task S5 to determine whether the current
residual MLP family is actually capacity-limited.

#### Required precondition
This task must not begin until Task S5 has completed and the observability
standard is available.

#### Required work
Codex must:

1. Define the explicit diagnostic criteria for:
   - likely underfitting,
   - likely overfitting,
   - likely optimization instability,
   - likely regime-specific failure.

2. Freeze the decision rules for whether a later model-capacity change is
   justified.

3. Explicitly state which observations would justify:
   - widening the model,
   - adding residual blocks,
   - leaving the architecture unchanged.

#### Fixed output files
Codex must create exactly:
- `docs/model_capacity_decision_rules.md`
- `tests/test_model_capacity_decision_rules.py`

#### Required local validation
Codex may run only:
- `pytest tests/test_model_capacity_decision_rules.py -q`

#### Acceptance checklist
- [ ] model-capacity decision rules are explicit
- [ ] widening / deepening conditions are explicit
- [ ] "change the model now" is not treated as an automatic conclusion
- [ ] no heavy local outputs were created

#### Completion type
This task is observation-dependent.
It can only be meaningfully completed after observability standards exist and
later real training observations are available.

#### Promotion rule
Only after Task S7 is complete may Task S8 move into Current Task.

---

### Task S8 — Add active learning to the surrogate roadmap

#### Task type
Local Codex planning task only.

#### Goal
Add active learning as an explicit future surrogate-training architecture plan.

This task does not execute active learning. It defines how the loop will work.

#### Required work
Codex must complete all of the following:

1. Define the initial surrogate-training stage.
2. Define the uncertainty / difficulty trigger for selecting new points.
3. Define how difficult points are sent back through the forward truth chain.
4. Define how new true-labeled points are merged back into the training set.
5. Define what returned compact artifacts must exist after each active-learning round.

#### Fixed output files
Codex must create exactly:
- `docs/active_learning_plan.md`
- `tests/test_active_learning_plan_contract.py`

#### Required local validation
Codex may run only:
- `pytest tests/test_active_learning_plan_contract.py -q`

#### Acceptance checklist
- [ ] the active-learning roadmap is frozen in writing
- [ ] the uncertainty / difficulty trigger is explicit
- [ ] the forward-relabel / retrain loop is explicit
- [ ] no heavy local outputs were created

#### Completion type
This task is directly completable as a planning task.

#### Promotion rule
Only after Task S8 is complete may any later server-side surrogate training task
be promoted.

---

## Archive

### Task S3 — Redesign the surrogate sampling strategy with sampling quality prioritized over fixed row counts

Completed previously.
The repository now freezes anchor coverage, neighborhood density, bridge
triggers, scrambled-Sobol continuous sampling, and
spectral-complexity-driven densification before any final row budget.

### Task S2 — Audit and redesign TB parameter representation

Completed previously.
The repository now treats the five-coordinate TB pilot as a draft exploratory
convenience rather than an automatically correct canonical representation, and
the frozen decision is a two-level structure:
original-parameter provenance plus grouped training-facing controls.

### Task S1 — Freeze the surrogate-rectification program and stop direct promotion to the current Task 15B server run

Completed previously.
The rectification-first roadmap is now the active progression, and Task 15A is
demoted to a draft reference contract rather than the immediate next server run.

### Task 15A — Freeze the inverse-ready medium-scale contract

Completed previously, but now treated as a draft reference contract pending the
surrogate-rectification program.

### Task 14E — Add a low-dimensional TB pilot contract without heavy hard constraints

Completed previously, but subject to re-evaluation by Task S2.

### Task 14D — Expand nuisance-domain sampling for Z, gamma, and temperature

Completed previously, but subject to re-interpretation by Tasks S3 and S4.

### Task 14C — Probe the expanded bias window contract at [-40, 40] meV

Completed previously.

### Task 14B — Build the RMFT-projected anchor dataset contract

Completed previously.

### Task 14A — Freeze the complete 7+1 pairing representation contract

Completed previously.

### Task 13B — Launch the first high-accuracy heavy surrogate campaign

Completed previously.

### Task 13A — Freeze the high-accuracy large-scale surrogate contract and upgrade the training stack

Completed previously.

### Earlier tasks

Completed previously.
