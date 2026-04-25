# TODO

## Current Task

### Task S9 — Prepare the first formal rectified dataset-generation and training handoff

#### Task type
Local Codex preparation task only.

#### Goal
Prepare the first formal post-rectification dataset-generation and training
handoff so the next serious server run follows the frozen S1-S8 standards
rather than legacy task-number drift.

#### Required precondition
This task must not begin until:

- Task S7 has concluded whether immediate capacity change is justified;
- Task S8 has frozen the active-learning roadmap;
- and the repository has a content-based layout, observability standard, and
  local pre-S7 observation baseline.

#### Required work
Codex must:

1. Define the first formal rectified dataset-generation target after the local
   pre-S7 observation run.
2. Define the matching formal training target and evaluation target.
3. Freeze the exact config paths and exact handoff note for the server run.
4. Explicitly state which outputs must stay on the server and which compact
   artifacts must return to GitHub for review.
5. Ensure the formal handoff uses the frozen representation, sampling,
   observability, and decision-rule contracts already accepted in S1-S8.

#### Fixed output files
Codex must create exactly:
- `docs/formal_rectified_server_handoff.md`
- `tests/test_formal_rectified_server_handoff_contract.py`

#### Required local validation
Codex may run only:
- `pytest tests/test_formal_rectified_server_handoff_contract.py -q`

#### Acceptance checklist
- [ ] the first formal rectified dataset/training/evaluation handoff is frozen
- [ ] exact config paths and exact server commands are written down
- [ ] returned compact artifacts are explicit
- [ ] heavy outputs are explicitly kept on the server
- [ ] no heavy local outputs were created

#### Completion type
This task is directly completable as a preparation task.

#### Promotion rule
Only after Task S9 is complete may any later formal server-side rectified
dataset-generation and surrogate-training run be promoted.

---

## Backlog

---

## Archive

### Task S8 — Add active learning to the surrogate roadmap

Completed previously.
The repository now freezes the later active-learning loop in writing:
initial stage, uncertainty / difficulty trigger, forward relabel path,
merge-back rule, and required compact returned artifacts.

### Task S7 — Diagnose whether model capacity changes are actually needed

Completed previously.
Using the real pre-S7 local observation run, the current frozen conclusion is:
there is not yet sufficient evidence to justify immediate expansion of model
capacity, so the residual architecture remains unchanged for now.

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
