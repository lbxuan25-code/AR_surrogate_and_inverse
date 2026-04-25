# Repository Layout V2

Task S6 freezes the future content-based repository layout standard.

This task does not perform a large destructive reorganization.
It defines the stable target layout that later migrations must move toward.

## Layout Principle

The primary organizing key must be content and role, not task number.

Task numbers may still appear:

- in archived legacy files;
- in migration aliases;
- or in returned-artifact compatibility paths.

They must not remain the main long-term directory logic.

## Repository Root

The stable top-level layout is:

```text
repo/
  AGENTS.md
  TODO.md
  README.md
  pyproject.toml
  src/
  scripts/
  configs/
  docs/
  tests/
  outputs/
```

## Source Layout

The content-based source layout remains under:

```text
src/ar_inverse/
```

The long-term package areas are:

- `datasets/`
- `pairing/`
- `surrogate/`
- `training/`
- `inverse/`
- `experiments/`

Rule:
new code should land in the content area it belongs to, not in a task-numbered
module name.

## Config Layout

The stable config layout remains under:

```text
configs/
  datasets/
  surrogate/
  inverse/
  experiments/
```

Inside each content area, V2 standardizes a second level by role rather than
task number.

The target pattern is:

```text
configs/
  datasets/
    smoke/
    contracts/
    server/
  surrogate/
    smoke/
    training/
    evaluation/
    server/
  inverse/
    smoke/
    search/
  experiments/
    smoke/
    reports/
```

Rule:
new configs should be grouped first by domain and then by role.

## Documentation Layout

The stable documentation layout remains under:

```text
docs/
```

V2 standardizes the following content-based homes:

```text
docs/
  contracts/
  audits/
  runbooks/
  standards/
  templates/
  setup/
  archive/
```

Interpretation:

- `contracts/`: frozen dataset, representation, sampling, joint-sampling, and
  interface contracts;
- `audits/`: audit skeletons, audit reviews, and decision-support audits;
- `runbooks/`: server handoffs, launch notes, and review-return instructions;
- `standards/`: observability, naming, layout, and engineering standards;
- `templates/`: reusable model card, experiment report, and similar templates;
- `setup/`: dependency and environment setup notes;
- `archive/`: explicitly archived legacy task-number-led notes kept for
  compatibility.

## Outputs Layout

The stable generated-artifact layout remains under:

```text
outputs/
```

V2 standardizes the content-based subdirectories:

```text
outputs/
  datasets/
  checkpoints/
  runs/
  figures/
  audits/
  inverse/
  experiments/
```

Interpretation:

- `datasets/`: dataset manifests and compact dataset metadata;
- `checkpoints/`: model checkpoints, ensemble manifests, and model cards;
- `runs/`: run metadata, evaluation reports, and compact run notes;
- `figures/`: training curves, representative spectrum plots, and later
  reusable figure assets;
- `audits/`: compact audit JSON or compact audit summaries returned from server
  review flows;
- `inverse/`: inverse-search outputs;
- `experiments/`: experiment-facing outputs.

Rule:
figures and audits now have explicit homes instead of being mixed into
`outputs/runs/` by default.

## Contracts, Audits, And Runbooks

V2 requires a clean separation between three documentation roles:

- contracts define frozen rules;
- audits inspect evidence against those rules;
- runbooks tell the user what to run and what to return.

A single document should not silently mix all three roles unless the document
is explicitly marked as a small compatibility note.

## Legacy Boundary

Current task-number-heavy files remain valid as legacy references during the
migration period.

However, the target standard is:

- new standards go under `docs/standards/`;
- new contracts go under `docs/contracts/`;
- new audits go under `docs/audits/`;
- new runbooks go under `docs/runbooks/`;
- new figures go under `outputs/figures/`;
- new compact audit outputs go under `outputs/audits/`.

## Task S6 Boundary

Task S6 freezes the layout standard only.

It does not yet require:

- mass file moves;
- broad import rewrites;
- or retroactive renaming of every legacy task-numbered path.
