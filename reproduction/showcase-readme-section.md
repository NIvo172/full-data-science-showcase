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
