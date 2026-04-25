# Experiment Report Template

Experiment-fitting reports must keep preprocessing, transport nuisance
controls, directional priors, feature-family compatibility, surrogate
uncertainty, and final direct-forward checks separate.

Reports should say:

```text
the AR data are compatible with these feature families
```

Reports must not claim a unique microscopic RMFT point.

## Required Sections

### Experiment

- experiment id;
- source path or acquisition reference;
- measurement metadata.

### Experimental Preprocessing

- schema version;
- ordered preprocessing operations;
- whether the data were normalized, smoothed, filtered, resampled, or left
  unchanged;
- confirmation that preprocessing is separated from physical inference claims.

### Transport Nuisance Controls

- candidate-family transport centers;
- uncertainty ranges;
- statement that these are nuisance controls, not order-parameter feature
  claims.

### Direction Priors And Regimes

- experiment direction prior, using `direction_resolved`, `direction_biased`,
  or `mixed_or_unknown`;
- candidate direction regimes used for direct-forward rechecks;
- explicit separation from pairing controls and transport nuisance controls.

### Candidate Feature Families

- compatible candidate-family ids;
- fit objective scores;
- fit-layer pairing controls and uncertainty ranges;
- no unique microscopic truth claim.

### Surrogate Uncertainty

- whether surrogate acceleration was used;
- relevant surrogate evaluation or fallback report;
- direct-forward fallback requirement when applicable.

### Final Forward Recheck Results

- direct-forward output references;
- forward metadata including `forward_interface_version`,
  `output_schema_version`, `pairing_convention_id`,
  `formal_baseline_record`, `formal_baseline_selection_rule`,
  `projection_config`, `git_commit`, and `git_dirty`.
