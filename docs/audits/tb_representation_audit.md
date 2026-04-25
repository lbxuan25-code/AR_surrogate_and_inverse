# TB Representation Audit

Task S2 audits how normal-state / TB information should enter later surrogate
training.

This repository is not allowed to copy or silently reimplement the forward
repository's Hamiltonian internals. Any TB representation used here must stay
traceable to the external forward repository's stable public interface and
recorded baseline metadata.

## Audit Scope

This audit compares three representation families:

1. original forward-exposed normal-state parameter form;
2. physically grouped TB parameter form;
3. reduced TB coordinate form, including the current
   `task14_tb_pilot_latent_v1` five-coordinate pilot.

The comparison is made on the required Task S2 axes:

- physical interpretability;
- forward traceability;
- surrogate input dimensionality;
- sampling difficulty;
- expected degeneracy risk.

## Currently Relevant TB / Normal-State Control Quantities

The currently relevant TB / normal-state information exposed or implied by the
repository is:

1. forward-side baseline provenance:
   `formal_baseline_record`, `formal_baseline_selection_rule`,
   `git_commit`, and `git_dirty`;
2. the forward-side public normal-state control set anchored to that baseline;
3. grouped physical variation axes already implied by the current draft pilot:
   `mu_shift`, `bandwidth_scale`, `interlayer_scale`,
   `orbital_splitting_shift`, and `hybridization_scale`;
4. the current reduced-coordinate storage block:
   `controls.tb_pilot_coordinates`;
5. the current reduced-coordinate version id:
   `task14_tb_pilot_latent_v1`.

Important current limitation:
the local repository does not yet contain a committed enumeration of the full
original forward-exposed normal-state field list. That omission is itself part
of the audit result. It means the current five-coordinate pilot is easier to
store locally than the original form, but it is also less traceable and less
auditable.

## Representation Families

### Family A: Original Forward Parameter Form

Definition:
use the original normal-state controls exposed by the forward repository's
public interface, referenced against the formal baseline record.

Strengths:

- highest forward traceability;
- lowest ambiguity about what the forward engine actually consumed;
- best provenance for later dataset review and reproduction;
- lowest risk of silently hiding relevant degrees of freedom.

Weaknesses:

- potentially highest input dimensionality;
- hardest sampling problem if used directly as the only training-facing space;
- physical meaning may be scattered across many forward-native fields;
- local repository cannot safely freeze names that are not yet explicitly
  published through the public forward interface contract.

### Family B: Physically Grouped TB Parameter Form

Definition:
use a modest number of interpretable grouped controls derived from the original
forward normal-state parameters, with a deterministic mapping and provenance
back to the original form.

Natural grouped axes already implied by current repository language are:

- chemical-potential shift;
- overall bandwidth renormalization;
- interlayer coupling scale;
- orbital splitting shift;
- hybridization scale.

Strengths:

- strong physical interpretability;
- lower dimensionality than the original forward form;
- easier to sample jointly with pairing and nuisance variables;
- still auditable if every grouped control is tied to a deterministic
  derivation rule and original-parameter provenance.

Weaknesses:

- requires an explicit mapping contract;
- can still hide degeneracies if multiple original parameter combinations map
  to the same grouped control values;
- traceability is weaker than the original form unless provenance is kept.

### Family C: Reduced TB Coordinate Form

Definition:
use a compressed low-dimensional latent or quasi-latent coordinate system as
the primary training-facing representation.

The current example is the Task 14E five-coordinate pilot:

- `mu_shift`
- `bandwidth_scale`
- `interlayer_scale`
- `orbital_splitting_shift`
- `hybridization_scale`

Strengths:

- lowest input dimensionality;
- easiest short-term sampling;
- convenient for a first exploratory pilot.

Weaknesses:

- weakest forward traceability;
- highest risk that distinct original normal-state states collapse into the
  same reduced coordinates;
- easiest path for hidden degeneracy and hidden non-identifiability;
- easiest path for silently turning an engineering convenience into an
  unsupported scientific contract.

## Comparison

| Representation family | Physical interpretability | Forward traceability | Surrogate input dimensionality | Sampling difficulty | Expected degeneracy risk |
| --- | --- | --- | --- | --- | --- |
| Original forward parameter form | Medium | High | High | High | Low |
| Physically grouped form | High | Medium if used alone; High if paired with provenance | Medium | Medium | Medium |
| Reduced coordinate form | Medium for hand-picked axes, otherwise Low | Low | Low | Low | High |

## Audit Findings

1. The current five-coordinate pilot is useful as an exploratory engineering
   convenience, but it is not strong enough to serve as the sole canonical TB
   representation.
2. Original forward parameters are the best provenance layer, but they are not
   automatically the best direct training input layer because they may make the
   sampling problem unnecessarily hard.
3. A physically grouped representation offers the best compromise for surrogate
   training only if the grouped axes remain explicitly linked to original
   forward parameters.
4. Therefore the best overall structure is not a single-layer choice between
   the three families. The best structure is a two-level representation:
   original-parameter provenance plus grouped training-facing controls.
5. Under that structure, the current five-coordinate pilot should be demoted
   from canonical status and retained only as a draft exploratory convenience
   until a grouped mapping contract is frozen.

## Audit Conclusion

Task S2 does not justify retaining `task14_tb_pilot_latent_v1` as the
long-term canonical TB representation.

The audit supports:

- preserving original forward-exposed normal-state parameters as provenance;
- using a physically grouped TB representation as the canonical
  training-facing family;
- and treating reduced coordinates only as optional derived helpers, not as the
  sole canonical representation.
