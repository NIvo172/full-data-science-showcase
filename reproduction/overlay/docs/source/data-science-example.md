# Data-science example

The full example contains a deterministic CSV pipeline, fixture-based tests, DVC parameters and experiment outputs, notebook tooling, generated UML diagrams, and an executable Sphinx Gallery example.

The reusable implementation lives in `src/full_data_science_example/`; repository scripts and notebooks import the installed package rather than duplicating pipeline logic.

The DVC file imports `configs/models/baseline.yaml` through its `vars` context, and the stage consumes `summary.round_digits` from that context before writing:

- `data/processed/summary.json`, including the input SHA-256 digest and selected precision;
- `data/processed/metrics.json`, exposed as DVC scalar metrics; and
- `reports/figures/cumulative_mean.csv`, exposed as DVC plot data.

Use `uv run dvc metrics show`, `uv run dvc plots show`, and `uv run dvc exp run` to inspect or reproduce experiments.

The {doc}`showcase workflow guide <showcase-workflows>` turns these commands into complete walkthroughs and records the fixture-specific values and files that successful runs produce. The {doc}`project command reference <command-reference>` remains the concise source for every command enabled by the selected template options.

## Validate the complete generated project

After the one-time setup has completed, run:

```bash
uv run --locked python scripts/validate_full_project.py
```

This fixture-specific driver cleans generated output and exercises the complete Python matrix, repository hooks, every documentation target, UML, DVC status/metrics/plots/experiments, package validation, the standalone build task, and the pipeline command-line interface. It verifies the resulting test, coverage, documentation, package, metric, plot, and provenance artefacts and fails if validation changes tracked files.
