# Full Data Science Example

End-to-end example exercising every template capability

## About this showcase

This is a complete, checked-in project created from the companion
`python-project-copier-template` repository. It enables every optional capability and
adds a small reproducible data pipeline plus integration tests.

Use it to inspect the resulting project structure, commands, reports, documentation,
packaging, DVC workflow, and CI configuration.

Its Sphinx site keeps the template-rendered project command reference separate from
showcase-only walkthroughs, fixture values, and expected outputs.

### Reproduce the showcase

Place this repository beside a Git checkout of `python-project-copier-template`, then
generate a new copy from the template's current `HEAD`:

```bash
uv run scripts/generate_showcase.py ../reproduced-data-science-showcase
```

Use `--template PATH` when the template is elsewhere. The destination must not exist
unless `--force` is supplied. Add `--initialize` to run `init_project.py`, or
`--validate` to initialise the result and execute its exhaustive validation driver.

> **Future reproducibility change:** the generator intentionally uses the template's
> current `HEAD` for now. Replace this with an immutable release tag or commit before
> relying on the workflow for historical, byte-for-byte reproduction.

### Start from the source archive

After extracting this repository beside `python-project-copier-template`, run the
one-time initialisation and the independent validation commands:

```bash
uv run scripts/init_project.py \
  --git-name "Your Name" \
  --git-email "you@example.com"
uv run --locked tox
```

Initialisation creates local Git history, resolves the committed dependency state,
reproduces the DVC pipeline, and creates `v0.0.1`. It writes to the terminal without
creating a log. The exhaustive showcase-only command is:

```bash
uv run --locked python scripts/validate_full_project.py
```

## Requirements

- Python 3.11 or newer
- [`uv`](https://docs.astral.sh/uv/)

## Installation

After the distribution is available from the configured package index:

```bash
uv add full-data-science-example
```

The equivalent pip command is:

```bash
python -m pip install full-data-science-example
```

For repository development, use the locked checkout workflow in `CONTRIBUTING.md` instead of installing from the package index.

## Usage

The generated starter API exposes a greeting function:

```python
from full_data_science_example.main import hello

print(hello("Ada"))
```

Data-science assets are organised under `configs/`, `data/`, `models/`, `references/`, and `reports/`, with exploratory work under `notebooks/`.
DVC metadata and pipeline state are tracked through `.dvc/`, `dvc.yaml`, and `dvc.lock`; no storage remote is configured by the template.

## Development

For an established repository checkout:

```bash
uv sync --locked
uv run --locked tox
```

Install the repository hooks once:

```bash
uv run pre-commit install
```

The repository guides separate daily development from maintainer-only operations:

| File | Audience | Contents |
| --- | --- | --- |
| `AGENTS.md` | AI agents and contributors | The canonical task → command catalog: environment, Tox envs, validation, and maintenance workflows |
| `CONTRIBUTING.md` | Contributors | Environment setup, dependencies, validation, reports, and optional feature workflows |
| `MAINTAINING.md` | Maintainers | One-time bootstrap, lock/version policy, CI, builds, collaboration, and Copier updates |
| `docs/README.md` | Documentation authors | Pages, API reference, examples, notebooks, and UML |
| `CODE_OF_CONDUCT.md` | Community | Participation and enforcement standards |

The one-time `scripts/init_project.py` bootstrap is documented in `MAINTAINING.md`. Contributors cloning an existing repository should not rerun it.

## Validation outputs

The default Tox suite writes:

- `reports/pytest/report.html`: self-contained test report.
- `reports/pytest/report.jsonl`: machine-readable pytest event stream.
- `reports/coverage/html/index.html`: browser-readable test coverage.
- `reports/sphinx/html/index.html`: rendered documentation.
- `reports/sphinx/coverage/index.html`: API documentation coverage.

Generated output is ignored by Git and can be removed with:

```bash
uv run --locked tox run -e clean
```

## Project links

- [Homepage](https://example.com/full-data-science-example)
- [Documentation](https://example.com/full-data-science-example/docs)
- [Repository](https://github.com/example/full-data-science-example)
- [Issues](https://github.com/example/full-data-science-example/issues)
- [Changelog](https://github.com/example/full-data-science-example/blob/main/CHANGELOG.md)

## Licence

This project is licensed under the MIT license. See `LICENSE`.
