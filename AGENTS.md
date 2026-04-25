# AGENTS.md

## Purpose

This repository hosts AR surrogate training, dataset orchestration, sampling
policy development, surrogate evaluation, training diagnostics, and
experiment-side preparation.

It is not the source of truth for forward physics.
The forward truth chain lives in the external LNO327 AR forward repository and
must be consumed only through its stable public `forward` interface.

The repository is currently in a surrogate-rectification phase.
Direct continuation of the previously frozen Task 15 medium server run is paused
until representation, sampling, observability, and engineering-standard issues
are corrected.
The existing Task 15A handoff remains in the repository only as a draft
reference contract. It must not be treated as an active server execution target
unless a later `TODO.md` task explicitly re-promotes or replaces it.

## Start Here For A Fresh Codex Conversation

A fresh Codex conversation must assume the following current state:

1. The repository already completed:
   - Task 13B high-accuracy heavy surrogate under the older local-box contract;
   - Task 14A–14E preparation work for:
     - full projected 7+1 pairing representation with global-phase gauge fixing,
     - RMFT anchor / neighborhood / bridge source concepts,
     - widened bias40 contract,
     - widened nuisance ranges,
     - and a first draft TB pilot representation;
   - Task 15A draft medium contract.

2. The user has explicitly decided that the repository must **not** continue
   directly into the old Task 15B server run.

3. The active mission is now surrogate rectification, not inverse execution.

4. The top rectification priorities are:
   - reassess TB parameter representation;
   - redesign sampling with quality prioritized over fixed row counts;
   - define rigorous joint sampling;
   - build proper training observability;
   - fix repository layout and naming conventions;
   - add active learning as a later roadmap item.

If you are a fresh Codex agent, do not assume the current Task 15A draft is the
next server command target. It is a draft reference contract pending
rectification.

## Current Development Priorities

The active development cycle is centered on five rectification priorities:

1. reassessing TB parameter representation instead of assuming the current
   low-dimensional latent pilot is correct;
2. redesigning sampling so sampling quality is prioritized over pre-fixed row budgets;
3. defining rigorous joint sampling across pairing, nuisance, and TB spaces;
4. upgrading training observability to industrial / academic diagnostic quality;
5. fixing repository layout and naming conventions.

Active learning is a planned later addition, but it is not a substitute for
these rectification tasks.

## Source Of Truth

Priority order:

1. `TODO.md`
2. committed contract docs, configs, and lightweight tests in this repository
3. dataset metadata, run metadata, checkpoint metadata, and forward-interface
   metadata
4. the external forward repository's public `forward` API contract
5. the external forward repository's directional capability contract
6. local code and tests
7. compact returned server artifacts committed back to GitHub for review

If local assumptions conflict with forward-interface metadata or external
direction-contract metadata, the forward repository wins.

## Split Workflow Model

This repository uses a strict split workflow.

### Local Codex responsibilities
Local Codex may:
- edit source code;
- edit configs;
- edit docs, contracts, audits, and runbooks;
- add or update lightweight validation tests;
- define representation rules, sampling rules, and observability rules;
- prepare exact server commands and returned-artifact expectations;
- review compact returned artifacts after the user has run a server task.

Local Codex must not:
- run medium-scale or large-scale dataset generation;
- run medium-scale or large-scale surrogate training;
- run medium-scale or large-scale surrogate evaluation;
- fabricate heavy outputs under `outputs/`;
- mark any server-run task complete before returned artifacts are reviewed.

### Manual server responsibilities
The user manually executes all heavy tasks on the server.

Heavy tasks include:
- dataset generation;
- surrogate training;
- surrogate evaluation;
- large benchmark runs;
- any run that produces large datasets, large checkpoints, or bulky spectrum collections.

### GitHub handoff boundary
GitHub is the handoff boundary between:
- local Codex preparation;
- and the user's manual server execution.

Committed configs and handoff notes are authoritative server instructions.

## Repository Boundary

This repository owns:
- dataset orchestration;
- sampling policy definitions;
- surrogate model training code;
- surrogate evaluation and calibration code;
- training diagnostics and observability tooling;
- checkpoint and run metadata schema management;
- server handoff notes and returned-artifact review logic;
- repository layout, naming, and engineering standards.

This repository must not copy, fork, or silently reimplement:
- the authoritative normal-state Hamiltonian code;
- the authoritative pairing-matrix code;
- RMFT source projection code;
- interface matching code;
- BTK solver code;
- authoritative formal baseline files;
- forward-side directional truth logic.

Use the external forward repository as the forward engine and as the authority
for directional support and forward metadata.

## Required Forward Dependency

All generated data must record the forward metadata emitted by the external
forward repository, including:
- `forward_interface_version`
- `output_schema_version`
- `pairing_convention_id`
- `formal_baseline_record`
- `formal_baseline_selection_rule`
- `projection_config`
- `git_commit`
- `git_dirty`

Direction-aware datasets must additionally preserve forward-emitted directional
metadata whenever available, including:
- `direction_mode`
- `interface_angle`
- `direction_support_tier`
- `direction_crystal_label`
- `direction_dimensionality`
- `directional_spread`
- any other forward-side provenance fields needed to reproduce the spectrum

Datasets generated under different forward metadata or different direction
contracts must be treated as distinct dataset families.

## Direction Contract Rules

This repository must follow the forward repository's current directional rules.

### Supported truth-grade regimes
- `inplane_100`
- `inplane_110`

### Supported spread regime
- narrow directional spread centered on supported named in-plane modes only
- spread must stay within the forward contract

### Unsupported regime
- `c_axis` is not currently supported
- do not train on it
- do not expose it as a valid target
- do not silently map 2D in-plane angle semantics to `c_axis`

### Diagnostic-only regime
- generic raw in-plane angles are diagnostic-only
- they must not be silently promoted into the primary truth-grade pool
- if included, they must be explicitly labeled and separated

## Pairing Representation Rules

The canonical future-facing pairing representation remains:

- the full projected complex 7+1 pairing channels;
- gauge-fixed only to remove the single globally redundant global phase;
- otherwise left uncompressed.

### Explicit prohibition
Do not introduce:
- PCA compression;
- latent manifold compression;
- learned low-dimensional pairing coordinates;
- any further lossy compression after the projected 7+1 pairing representation
  has already been formed.

### Gauge-fixing rule
Gauge-fixing is allowed only for the physically redundant global phase.
It must:
- use a deterministic anchor selection policy;
- rotate all channels by one common phase only;
- preserve all relative phase information.

Do not remove relative phase information.

## TB Representation Rules

The repository must no longer assume that the current low-dimensional TB pilot
coordinate system is automatically correct.

Until Task S2 completes:
- treat the current TB pilot as a draft engineering convenience only;
- do not expand that pilot into a long-term canonical TB representation;
- do not silently assume reduced TB coordinates are better than original or
  grouped TB parameters.

TB representation decisions must be justified by audit and documented comparison.

## Sampling Rules

The repository must not treat fixed row budgets as more important than sampling
quality.

### Canonical principle
Sampling-policy design comes before final row-budget freezing.

### Required sampling concepts
Future sampling design must explicitly define:
- RMFT anchor coverage rules;
- neighborhood density rules;
- bridge triggering rules;
- continuous-subspace sampler type;
- physically sensitive-region densification rules;
- and joint sampling rules across pairing, nuisance, and TB spaces.

### Explicit prohibition
Do not leave continuous-subspace sampling as vague "continuous sampling".
Do not treat pre-fixed role quotas as a substitute for a real sampling design.

## Nuisance-Domain Rules

The repository currently has widened nuisance ranges, but future work must not
stop at freezing envelopes only.

Future contracts must explicitly define:
- whether nuisance variables are sampled independently or with structured coupling;
- how density varies across the nuisance domain;
- and whether gamma or other coordinates use non-uniform density rules.

## Observability Rules

No future serious surrogate training run should be considered acceptable unless
it produces the required observability outputs.

At minimum, later accepted training standards must include:
- train and validation loss curves;
- reconstruction and shape loss curves;
- learning-rate curves;
- gradient norm summaries;
- parameter update summaries;
- grouped error reports;
- representative direct-forward versus surrogate spectrum plots.

Do not treat a single `metrics.json` plus a single `evaluation_report.json` as
sufficient industrial or academic observability.

## Model-Capacity Rules

Do not widen or deepen the model by intuition alone.

Model-capacity changes are allowed only after:
- observability standards exist,
- real training observations are available,
- and a written decision rule shows why the architecture should change.

Until then:
- do not silently add depth;
- do not silently widen the model;
- do not silently replace the residual MLP family.

## Repository Layout And Naming Rules

The current task-number-heavy layout is no longer considered a satisfactory
long-term structure.

Future repository standards must move toward:
- content-based directory organization;
- content-based naming conventions;
- and a migration plan away from task-number-led file sprawl.

Until Task S6 completes:
- do not expand the current disorder further than necessary;
- avoid introducing more ad hoc task-number-only file names when a content-based
  name is possible.

## Execution Protocol

At any moment, only the single task in `TODO.md -> Current Task` may be
executed.

Do not start backlog tasks early.
Do not merge multiple tasks into one unverified mega-step.

### For directly completable local tasks
Before marking a task complete:
- run only the lightweight tests explicitly allowed by `TODO.md`;
- verify docs, configs, and tests are mutually consistent;
- verify no heavy local outputs were fabricated;
- record the resulting contract or audit in the specified files.

### For observation-dependent tasks
A task marked observation-dependent must not be declared complete merely because
a document skeleton exists.
It requires the relevant prior observations, diagnostics, or returned server
artifacts before its decision can be finalized.

### For manual server tasks
A server-run task must not be marked complete until:
- the user has executed the run on the server,
- compact returned artifacts are committed back to GitHub,
- and local review has accepted those artifacts.

## Evaluation Rules

Future surrogate promotion must be judged not only by successful training but by:
- held-out error,
- grouped regime stability,
- observability outputs,
- and consistency with the frozen forward / direction contracts.

Do not claim a later surrogate is validated merely because it trained
successfully.

## Scientific Reporting Rules

This repository is currently focused on surrogate rectification, not inverse
claims.

Any scientific report must clearly separate:
- projected pairing structure;
- transport nuisance controls;
- TB parameterization or TB pilot controls;
- directional regime assumptions;
- surrogate uncertainty;
- and final forward recheck results when relevant.

Do not present unsupported interpretations as established physical results.

## Server Handoff Rules

Every later server-run task should have a committed handoff note that states:
- exact commands;
- exact config files;
- expected output paths;
- compact artifacts that must be returned for review;
- heavy artifacts that must remain only on the server.

Heavy outputs such as:
- full forward-output directories;
- large datasets;
- large checkpoints;
- bulky spectrum collections

should remain on the server unless explicitly promoted.

## Storage Rules

Large artifacts belong only in explicit output directories:
- datasets under `outputs/datasets/`
- checkpoints under `outputs/checkpoints/`
- run metadata and reports under `outputs/runs/`
- figures under an explicit figure/output path once Task S5 or S6 defines it

Do not commit heavyweight generated artifacts unless explicitly requested.

## Cleanliness Rules

Do not leave behind obsolete configs, stale manifests, or ambiguous dual paths
that can contaminate later rectification tasks.

When a prior contract is demoted to draft status:
- say so explicitly;
- avoid silently continuing to treat it as canonical;
- update docs, tests, and handoff notes accordingly.

No silent dual-standard behavior is allowed for:
- direction semantics;
- pairing representation semantics;
- TB representation semantics;
- baseline-vs-neural checkpoint semantics;
- local Codex vs manual server execution responsibilities.
