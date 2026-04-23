# AGENTS.md

## Purpose

This repository hosts AR surrogate training, inverse search, experiment-fitting,
and experiment-side data handling.

It is not the source of truth for forward physics.
The forward truth chain lives in the external LNO327 AR forward repository and
must be consumed only through its stable public `forward` interface.

The current development cycle has moved past workflow validation and compact
production-style ridge baselines. The new priority is to introduce a first
neural surrogate training stack under the same frozen direction and forward
contracts.

Current stage note:
- Task 9 completed the canonical direction-aware smoke loop.
- Task 10A/10B completed the pilot preparation and pilot server validation.
- Task 11A/11B completed the compact production-contract validation run.
- Task 12A completed: the first neural surrogate stack, medium-scale canonical
  configs, handoff note, and lightweight wiring tests are now in the
  repository.
- The current `TODO.md` task is Task 12B: run the first medium-scale neural
  surrogate validation job on the server and return compact artifacts.
- Large-scale heavy surrogate campaigns belong to later tasks only after Task
  12B review is accepted.

## Source Of Truth

Priority order:

1. this repository's `TODO.md`
2. committed configs, docs, and lightweight validation tests in this repository
3. dataset metadata, run metadata, checkpoint metadata, and forward-interface
   version metadata
4. the external forward repository's public `forward` API contract
5. the external forward repository's published directional capability contract
6. local code and tests
7. returned server artifacts committed back to GitHub for review

If local assumptions conflict with forward-interface metadata or the external
direction contract, the external forward metadata and contract win.

## Workflow Model

This repository uses a split execution workflow.

### Local Codex workspace responsibilities
Local Codex may:
- edit source code;
- edit configs;
- edit docs and runbooks;
- add or update lightweight validation tests;
- add new model implementations and training/evaluation wiring;
- prepare server commands and output expectations;
- review compact server-returned artifacts after they are committed back.

Local Codex must not:
- silently run medium-scale or large-scale dataset generation;
- silently run medium-scale or large-scale neural training;
- silently run medium-scale or large-scale evaluation;
- pretend a server-run task completed before returned artifacts are reviewed.

### GitHub handoff responsibilities
GitHub is the handoff boundary between:
- local Codex preparation, and
- manual server execution.

Committed configs and runbooks are the authoritative instructions for the
server-side run.

### Server responsibilities
The server is where heavy execution happens:
- dataset generation
- neural or baseline surrogate training
- evaluation
- large output creation

The server may keep heavyweight artifacts locally. Only compact review artifacts
should normally be brought back to GitHub.

## Repository Boundary

This repository owns:
- dataset orchestration;
- sampling policies for fit-layer, transport, and supported directional regimes;
- surrogate model training code;
- surrogate evaluation and calibration code;
- inverse search;
- experiment-fitting reports;
- experiment-side ingest and preprocessing metadata;
- checkpoint and run metadata schema management;
- server handoff notes and returned-artifact review logic.

This repository must not copy, fork, or silently reimplement:
- normal-state Hamiltonian code;
- round-2 pairing matrix code;
- RMFT source projection code;
- interface matching code;
- BTK transport solver code;
- authoritative formal baseline files;
- forward-side directional truth logic.

Use the external forward repository as the forward engine and as the authority
for what directional modes are physically supported.

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
- any other forward-side provenance fields required to reproduce the spectrum

Datasets generated under different forward metadata or different direction
contracts must be treated as distinct dataset families.

## Direction Contract Rules

This repository must follow the forward repository's current directional rules.

### Supported truth-grade directional regimes
- `inplane_100`
- `inplane_110`

### Supported spread regime
- narrow directional spread centered on supported named in-plane modes only
- spread settings must stay within the forward contract
- do not invent wider or arbitrary spread semantics

### Unsupported regime
- `c_axis` is not currently supported
- do not train on it
- do not expose it as a valid inverse target
- do not silently map any 2D in-plane angle to `c_axis`

### Diagnostic-only regime
- generic raw in-plane angles are caution-only / diagnostic-only
- they must not be silently promoted into the primary truth-grade training pool
- if included, they must be explicitly labeled, documented, and separated or
  down-weighted

## Model-Stack Rules

The repository now has two distinct surrogate phases.

### Baseline phase
The ridge-linear surrogate remains:
- a baseline comparator,
- a compatibility path for older tasks,
- a simple calibration reference.

Do not remove it unless a later task explicitly authorizes retirement.

### Neural phase
The first neural surrogate stack must:
- preserve the current feature contract unless a task explicitly changes it;
- support full-spectrum prediction on a fixed bias grid;
- record full training metadata in run artifacts;
- produce checkpoint formats that evaluation/report code can read without
  ambiguity.

Do not introduce a neural architecture that silently changes the meaning of the
input feature contract or the output spectrum contract.

## Execution Protocol

At any moment, only the single task in `TODO.md -> Current Task` may be
executed.

Do not start backlog tasks early.
Do not combine dataset generation, surrogate training, inverse search,
experiment preprocessing, and reporting into one unverified mega-step.

### For local Codex tasks
Before marking a preparation task complete:
- run only the lightweight tests or checks explicitly allowed by the task;
- verify config paths and docs are consistent;
- verify no heavy output has been fabricated;
- verify checkpoint/readback/report code is wired consistently across supported
  `model_type` options;
- update `TODO.md` only after the preparation stage is genuinely complete.

### For server-run tasks
A server-run task must not be marked complete until compact returned artifacts
have been committed back to GitHub and reviewed locally.

Returned artifacts should include only compact validation evidence unless the
task explicitly requests a larger canonical artifact.

## Dataset And Sampling Rules

Primary training datasets must be built from supported truth-grade directional
regimes first.

Use this hierarchy unless the current task explicitly changes it:
1. supported named in-plane modes without spread
2. supported named in-plane modes with narrow spread
3. diagnostic-only raw-angle extensions, if explicitly enabled

Do not mix all regimes into one undifferentiated pool by default.

Sampling policy documents, configs, and returned manifests must make it clear:
- which regimes are primary
- which are secondary
- which are diagnostic-only
- which are unsupported and therefore rejected

## Feature Intake Rules

Direction must not be represented only as a raw continuous `interface_angle`.

When direction-aware training is implemented, feature intake must distinguish:
- discrete directional semantics
- continuous transport controls
- continuous spread controls
- raw angle as auxiliary metadata when applicable

Do not let model code collapse supported named modes, diagnostic-only angles,
and unsupported modes into one ambiguous feature path.

## Evaluation Rules

Neural-stack promotion should be judged against the ridge baseline, not only by
whether the code runs.

When Task 12B or later medium/large neural runs are reviewed, compare against
the ridge baseline on at least:
- held-out RMSE
- held-out max absolute error
- unsafe fraction
- direction-regime report
- transport-regime report

Do not claim the neural stack is validated merely because it trained
successfully. It must show meaningful improvement on at least one held-out
metric or regime.

## Scientific Reporting Rules

Inverse outputs must be candidate families, not unique microscopic truth claims.

Reports should say:
- "the AR data are compatible with these feature families"

They should not say:
- "the order parameter is uniquely this RMFT point"

Always separate:
- fit-layer pairing controls;
- transport nuisance controls;
- experimental preprocessing;
- directional priors or directional regime assumptions;
- surrogate uncertainty;
- final forward recheck results.

Do not present unsupported directional interpretations as established physical
results.

## Server Handoff Rules

Every server-run task should have a committed runbook note that states:
- exact commands to run;
- exact config files to use;
- expected output directories;
- which artifacts must be returned to GitHub for review;
- which heavy artifacts should stay only on the server.

Heavy outputs such as:
- full forward-output directories
- large raw pilot, medium-scale, or large-scale datasets
- large checkpoints
- bulky spectrum collections

should stay on the server unless the task explicitly promotes a small canonical
example into the repository.

## Storage Rules

Large artifacts belong in explicit output directories, not in source code paths:
- datasets under `outputs/datasets/`
- checkpoints under `outputs/checkpoints/`
- training logs under `outputs/runs/`
- inverse results under `outputs/inverse/`
- experiment fits under `outputs/experiments/`

Do not commit heavyweight generated artifacts unless the project explicitly
decides they are small canonical examples.

## Cleanliness Rules

Do not leave behind obsolete configs, stale manifests, legacy angle-only
assumptions, or ambiguous baseline-vs-neural code paths that can contaminate
later tasks.

When replacing or extending an old training path:
- update the docs;
- update the config examples;
- update tests;
- remove or clearly deprecate the obsolete path.

No silent dual-standard behavior is allowed for direction semantics, and no
silent dual-standard behavior is allowed for ridge-vs-neural checkpoint/report
semantics.
