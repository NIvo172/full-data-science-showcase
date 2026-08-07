# Showcase workflows and expected outputs

This page demonstrates how the commands fit together in the all-features data-science project. Use the {doc}`project command reference <command-reference>` for the canonical command list supported by this generated project; use this page for concrete sequences, fixture values, and expected artefacts.

## Choose the validation depth

| Situation | Command | Result |
| --- | --- | --- |
| Fast static feedback | `uv run --locked tox run -e lint` | Docstrings, Ruff, formatting, and strict Mypy |
| One focused test | `uv run --locked tox run -e py311 -- -k <expression>` | The selected test against the built wheel |
| Normal local or CI validation | `uv run --locked tox` | The configured default environments and reports |
| Exhaustive showcase audit | `uv run --locked python scripts/validate_full_project.py` | Every supported workflow plus output and clean-worktree checks |

The exhaustive driver is deliberately showcase-specific. A normal generated project uses Tox as its public validation interface and does not need a second orchestration script.

## Reproduce or initialise the repository

To create a fresh showcase from the companion template's current `HEAD`, place the repositories beside one another and run:

```bash
uv run scripts/generate_showcase.py ../reproduced-data-science-showcase
```

Add `--initialize` to run the generated `scripts/init_project.py`, or `--validate` to initialise and then execute the exhaustive audit. The mutable `HEAD` reference is temporary and must eventually be replaced by an immutable release tag or commit.

When starting from the source archive instead, initialise it once:

```bash
uv run scripts/init_project.py \
  --git-name "Your Name" \
  --git-email "you@example.com"
```

Initialisation creates repository-local Git identity, commits resolved state, reproduces the DVC pipeline, and creates the default `v0.0.1` tag. It prints progress to the terminal and does not create a setup log.

## Run and inspect the deterministic pipeline

The fixture has four observations: `1`, `2`, `3`, and `4`. Reproduce its declared DVC stage and inspect its results:

```bash
uv run dvc status
uv run dvc repro
uv run dvc metrics show
uv run dvc plots show reports/figures/cumulative_mean.csv --show-vega
uv run dvc exp run
```

The pipeline must produce:

| Path | Expected content |
| --- | --- |
| `data/processed/summary.json` | Mean `2.5`, record count `4`, rounding precision `3`, and a 64-character input SHA-256 digest |
| `data/processed/metrics.json` | `{"mean": 2.5, "record_count": 4}` |
| `reports/figures/cumulative_mean.csv` | Observation-by-observation cumulative mean data declared as a DVC plot |
| `dvc.lock` | Resolved stage dependencies, parameters, and output hashes |

Changing `summary.round_digits` in `configs/models/baseline.yaml` makes the stage stale. `dvc repro` updates the outputs and lock; restore the fixture value before expecting a clean worktree.

## Build and check the documentation

Exercise each documentation driver target independently:

```bash
uv run --locked tox run -e docs -- clean
uv run --locked tox run -e docs -- html
uv run --locked tox run -e docs -- coverage
uv run --locked tox run -e docs
```

The strict build treats warnings as errors and produces:

| Path | Purpose |
| --- | --- |
| `reports/sphinx/html/index.html` | Browsable Sphinx site, including this page, API docs, gallery, notebooks, and UML |
| `reports/sphinx/coverage/python.txt` | Machine-readable API documentation coverage details |
| `reports/sphinx/coverage/index.html` | Browser-readable API coverage report |
| `docs/source/auto_examples/` | Generated Sphinx-Gallery pages |
| `docs/source/diagrams/` | Generated Mermaid UML sources |

Run `uv run --locked tox run -e uml` when only the UML source needs regeneration. The {doc}`documentation guide <documentation-guide>` explains page ownership and authoring conventions.

## Exercise tests, hooks, notebooks, and packaging

```bash
uv run --locked tox run -m test
uv run --locked tox run -e pre-commit
uv run --locked tox run -e notebooks
uv run --locked tox run -e package-check
uv run --locked tox run -e build
```

Expected outputs include the self-contained test report at `reports/pytest/report.html`, event records at `reports/pytest/report.jsonl`, coverage under `reports/coverage/`, and one source archive plus one wheel under `dist/`. Notebook validation checks stored output and metadata policy without starting JupyterLab; use `uv run --group notebooks jupyter lab` for interactive work.

## Run the exhaustive showcase contract

After initialisation, the following single command checks all of the workflows above:

```bash
uv run --locked python scripts/validate_full_project.py
```

The driver starts with a clean, locked checkout; runs the default suite and the complete Python matrix; exercises hooks, every documentation target, UML, DVC status/metrics/plots/experiments, package checks, builds, and the pipeline CLI; verifies all expected files and deterministic metric values; and finally requires `git status --short` to be empty. Success ends with:

```text
Full generated-project validation completed successfully.
```

## Clean generated output

Remove reports, distributions, caches covered by the task, and generated documentation sources with:

```bash
uv run --locked tox run -e clean
```

This does not delete tracked DVC outputs or source material. If a validation command changes tracked state, inspect it with `git status --short` before deciding whether the change is an intended update.
