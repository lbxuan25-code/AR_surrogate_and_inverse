# TODO

## Current Task

### Task P1 — User-approved first production-scale surrogate run contract

#### Task type
Local preparation task only. Do not start heavy generation or training in this task.

#### Why this task exists
The repository completed the surrogate-rectification sequence S1-S8. Those tasks fixed or clarified:

- full projected 7+1 pairing representation with only global-phase redundancy removed;
- TB representation caution and two-level provenance/training-facing thinking;
- sampling-quality-first policy;
- joint sampling policy;
- training observability standard;
- repository layout and naming standards;
- model-capacity decision rule: do not expand the residual MLP architecture yet;
- active-learning roadmap as a future extension.

After S8, Codex introduced S9/S10 by itself. Those tasks are not user-owned task definitions and are superseded by this TODO. The next step is not to keep following Codex-invented S-number tasks. The next step is to prepare a user-approved production-scale surrogate run contract.

#### Goal
Prepare the first user-approved production-scale dataset-generation, training, and evaluation contract for the rectified surrogate pipeline.

This task must produce a production-ready handoff, but it must not execute the heavy run.

#### Required decisions to freeze
Codex must freeze all of the following in one coherent production contract:

1. dataset generation target:
   - row budget;
   - train / validation / test split;
   - pairing source composition;
   - sampling-policy-v2 usage;
   - joint sampling usage;
   - CPU worker recommendation for local execution.

2. training target:
   - model family;
   - residual width and depth;
   - loss contract;
   - optimizer;
   - batch size;
   - device policy;
   - ensemble policy, if used.

3. evaluation target:
   - held-out metrics;
   - grouped error axes;
   - observability artifact set;
   - acceptance / rejection criteria.

4. local execution target:
   - exact dataset command;
   - exact training command;
   - exact evaluation command;
   - expected output directories;
   - compact artifacts to keep under version control;
   - heavy artifacts that must stay local and uncommitted.

#### Fixed user decisions
Use these decisions unless the user explicitly changes them:

- All training is intended to run on the user's local machine unless a later user-approved task says otherwise.
- Do not revive the old Task 15A medium contract as canonical.
- Do not use Codex-invented S9/S10 as canonical tasks.
- Do not change model capacity yet; S7 concluded there is no sufficient evidence for immediate expansion.
- Active learning remains a future roadmap item and is not part of the first production run.
- Do not use feature engineering as a main strategy.
- Sampling quality is more important than preserving any old fixed row budget.

#### Fixed output files
Create or update exactly these user-approved production files:

- `docs/runbooks/production_surrogate_v1_handoff.md`
- `configs/datasets/production_surrogate_v1.dataset.json`
- `configs/training/production_surrogate_v1.training.json`
- `configs/evaluation/production_surrogate_v1.evaluation.json`
- `tests/test_production_surrogate_v1_contract.py`

If the repository does not yet fully use these content-based directories, create them and avoid adding new task-number-first files.

#### Required local validation
Run only lightweight checks:

- `pytest tests/test_production_surrogate_v1_contract.py -q`

Do not run dataset generation, training, or evaluation in this task.

#### Acceptance checklist
- [ ] production dataset contract is frozen
- [ ] production training contract is frozen
- [ ] production evaluation contract is frozen
- [ ] local execution commands are written down
- [ ] compact vs heavy artifact boundary is written down
- [ ] old S9/S10 path is clearly superseded
- [ ] no heavy outputs were created

#### Promotion rule
Only after P1 is accepted may P2 begin.

---

## Backlog

### Task P2 — Execute the first production-scale surrogate run locally

#### Task type
Manual local execution plus local review. Heavy task.

#### Goal
Run the first user-approved production-scale rectified surrogate pipeline on the user's local machine.

#### Required precondition
P1 must be accepted. Use only the committed P1 configs and runbook.

#### Required work
Execute in order:

1. dataset generation;
2. surrogate training;
3. surrogate evaluation;
4. observability artifact generation;
5. compact artifact review.

#### Local execution constraints
Use local resources deliberately:

- start with 8 CPU workers for forward/data generation unless P1 specifies otherwise;
- use CUDA GPU if available;
- do not silently fall back to CPU for training;
- do not run multiple ensemble members concurrently unless memory has been checked;
- keep heavy forward outputs and bulky intermediate spectra uncommitted.

#### Required returned / reviewed compact artifacts
At minimum, P2 must produce reviewable compact artifacts covering:

- dataset manifest and metadata;
- training metrics;
- training history;
- loss curves;
- gradient summary;
- parameter update summary;
- evaluation report;
- grouped error report;
- best / median / worst spectrum comparison plots;
- model card or run summary.

#### Acceptance checklist
- [ ] dataset generation completed under P1 contract
- [ ] training completed under P1 contract
- [ ] evaluation completed under P1 contract
- [ ] observability artifacts exist
- [ ] compact artifacts are reviewable
- [ ] heavy outputs remain local and uncommitted
- [ ] run is explicitly accepted or rejected

#### Promotion rule
Only after P2 review may any scaling, architecture change, or active-learning task be promoted.

---

### Task P3 — Review production run and decide next action

#### Task type
Observation-dependent review task.

#### Goal
Use P2 outputs to decide what to do next.

#### Possible outcomes
Exactly one primary outcome should be chosen:

1. accept production surrogate v1 as the current baseline;
2. revise sampling and rerun;
3. revise training settings and rerun;
4. scale dataset size;
5. start an active-learning round;
6. revisit model capacity only if S7 decision rules are triggered.

#### Required evidence
The decision must be based on:

- train / validation curves;
- reconstruction / shape loss curves;
- grouped error report;
- worst spectrum comparisons;
- gradient and parameter update summaries;
- held-out metrics;
- uncertainty / ensemble diagnostics if available.

#### Fixed output file
- `docs/reviews/production_surrogate_v1_review.md`

#### Acceptance checklist
- [ ] P2 artifacts were reviewed
- [ ] decision is evidence-based
- [ ] next task is explicitly user-approved
- [ ] no Codex-invented task is promoted automatically

---

## Archive

### Tasks S1-S8 — Surrogate rectification sequence

Completed previously.

Summary:
- S1 stopped direct promotion of the old Task 15B route.
- S2 audited TB representation and demoted the five-coordinate TB pilot from automatic canonical status.
- S3 froze sampling-quality-first policy.
- S4 froze joint sampling policy.
- S5 froze training observability standards.
- S6 froze repository layout and naming standards.
- S7 concluded that current evidence does not justify immediate model expansion.
- S8 froze active learning as a future roadmap item.

### Codex-proposed S9/S10

Superseded.

S9/S10 were introduced by Codex after S8 and are not user-owned canonical task definitions. They must not be treated as the active execution path. This TODO replaces them with the user-approved P1/P2/P3 production sequence.

### Earlier historical tasks

Task 13B, Task 14A-14E, Task 15A, and earlier tasks remain historical references. Task 15A is a draft reference contract only and is not the active production contract.
