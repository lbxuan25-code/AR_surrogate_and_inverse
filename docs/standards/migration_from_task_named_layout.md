# Migration From Task-Named Layout

Task S6 freezes the migration plan from the current task-number-heavy layout to
the V2 content-based standard.

The plan is staged so the repository does not break existing references or
server handoff paths all at once.

## Migration Goals

The migration must achieve all of the following:

- preserve repository continuity;
- reduce future task-number sprawl;
- keep server handoffs reviewable;
- preserve compatibility with historical task-number paths during transition;
- and avoid large destructive moves before each target area is ready.

## Phase 1: Freeze Standards

This is the current S6 phase.

Actions:

- freeze `repository_layout_v2.md`;
- freeze `naming_convention_v2.md`;
- freeze this migration plan;
- stop creating new ad hoc task-number-only names when a content-based name is
  possible.

No large file moves occur in this phase.

## Phase 2: Dual-Path Introduction

Introduce content-based homes for new work while leaving legacy task-number
paths intact.

Actions:

- place new standards under `docs/standards/`;
- place new contracts under `docs/contracts/`;
- place new audits under `docs/audits/`;
- place new runbooks under `docs/runbooks/`;
- place new figures under `outputs/figures/`;
- place new compact audit artifacts under `outputs/audits/`.

Compatibility rule:

- legacy task-number files remain authoritative only where later contracts still
  point to them;
- new work should reference the content-based home first.

## Phase 3: Alias And Redirect Cleanup

After the new homes are in place, convert old task-number-led references into
explicit archive or compatibility aliases.

Actions:

- update README and contracts to point first to content-based names;
- mark old task-number files as `legacy`, `archive`, or `compatibility alias`;
- stop treating task-number names as the default examples in docs.

## Phase 4: Config And Output Harmonization

Once documentation has shifted, harmonize config and output naming.

Actions:

- introduce content-based config names by domain and stage;
- add compatibility loaders or documented aliases where needed;
- standardize `outputs/figures/` and `outputs/audits/` for new artifact
  families;
- migrate run metadata filenames toward role-based names where practical.

## Phase 5: Archive Reduction

Only after the content-based paths have been used successfully should the
repository reduce the visible prominence of task-number files.

Actions:

- move long-tail historical notes to `docs/archive/`;
- leave only clearly documented compatibility aliases at the top level;
- remove silent duplicate paths when downstream references are fully migrated.

## Safety Rules During Migration

The migration must not:

- break current lightweight tests without replacement;
- invalidate historical server returned-artifact references;
- silently rename files that current handoff notes still depend on;
- or mix content-based and task-based names without marking one of them as the
  compatibility path.

## First Migration Targets

The highest-value first targets are:

1. `docs/` because it currently mixes contracts, audits, runbooks, standards,
   and templates at one level;
2. `outputs/` because figures and audits do not yet have explicit homes;
3. `configs/` because current names still lead with task numbers even when the
   underlying stage meaning is already clear.

## Success Criteria

The migration is succeeding when:

- new files default to content-based names;
- old task-number names are clearly marked as legacy or compatibility aliases;
- the top-level docs/configs/outputs views are understandable without knowing
  the entire task history;
- and new contributors can find the right file family by role instead of by
  memorizing task numbers.
