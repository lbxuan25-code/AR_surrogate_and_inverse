# TODO

## Current Task

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

## Backlog

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

### Task S6 — Refactor repository layout and naming conventions

Completed previously.
The repository now freezes a content-based layout standard, a role-first naming
convention, and a staged migration plan away from task-number-led file sprawl.

### Task S5 — Build the training observability and diagnostics standard

Completed previously.
The repository now freezes mandatory curves, optimization diagnostics,
block-level sensitivity diagnostics, representative direct-forward versus
surrogate plots, and grouped error outputs as the minimum observability
standard.

### Task S4 — Redefine joint sampling across pairing, nuisance, and TB spaces

Completed previously.
The repository now freezes structured nuisance correlations, TB/nuisance
coupling, widened-bias densification implications, and a piecewise `gamma`
density policy.

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
