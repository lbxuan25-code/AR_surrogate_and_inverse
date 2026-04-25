# TODO

## Current Task

### Task S10 — Execute and review the first formal large-scale rectified production run

#### Task type
Manual server task plus local review.

#### Goal
Run the first formal large-scale post-rectification production draft on the
server and review the returned compact artifacts locally before any later
promotion.

#### Required precondition
Task S9 must already be complete.
The committed handoff note and committed production-draft config trio must be
accepted before the heavy run is launched.

#### Required work
Codex must:

1. Use the committed S9 handoff note and committed production-draft configs on
   the server.
2. Complete dataset generation, training, and evaluation on the server.
3. Commit the required compact returned artifacts back to GitHub.
4. Review those returned artifacts locally against the frozen observability and
   contract standards.
5. Accept or reject the run explicitly rather than silently treating it as
   canonical.

#### Fixed output files
This manual server task does not define new fixed local-doc output files in
advance.
Its required outputs are the compact returned artifacts frozen by S9.

#### Required local validation
Local validation happens by review of the returned compact artifacts after the
server run.

#### Acceptance checklist
- [ ] the server run used the committed S9 production-draft handoff
- [ ] required compact artifacts were returned to GitHub
- [ ] local review accepted or rejected the run explicitly
- [ ] heavy outputs stayed on the server

#### Completion type
This task is observation-dependent and server-executed.

#### Promotion rule
Only after Task S10 is reviewed may any later larger production task,
architecture revision, or active-learning stage be promoted.

---

## Backlog

---

## Archive

### Task S9 — Prepare the first formal rectified dataset-generation and training handoff

Completed previously.
The repository now freezes the first formal large-scale post-rectification
production draft, including the exact config trio, exact launch commands,
recommended row budget, and the compact-artifact return contract.

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
