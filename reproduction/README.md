# Showcase reproduction source

This directory contains everything added on top of the Copier template:

- `copier-data.yml` stores the non-interactive Copier answers;
- `overlay/` stores project-owned files that are applied after rendering, including
  the showcase workflow guide and its expected outputs; and
- `showcase-readme-section.md` stores the showcase-specific README introduction.

The project command reference itself is rendered by the template and is intentionally
not duplicated in the overlay. This keeps the canonical selected-feature command list
separate from showcase-owned examples.

From the showcase repository root, generate a sibling project with:

```bash
uv run scripts/generate_showcase.py ../reproduced-data-science-showcase
```

The default template checkout is the sibling directory
`../python-project-copier-template`. Override it when needed:

```bash
uv run scripts/generate_showcase.py \
  --template /path/to/python-project-copier-template \
  ../reproduced-data-science-showcase
```

The template must be a Git repository with a valid `HEAD`. The generator always
passes `HEAD` to Copier and prints the resolved commit used for the render.

> **Future change required:** replace the mutable `HEAD` policy with a pinned template
> release tag or full commit hash once the template release workflow is established.

Optional lifecycle flags are:

- `--initialize`: run the generated `scripts/init_project.py`;
- `--validate`: initialise the project and run
  `scripts/validate_full_project.py`; and
- `--force`: replace an existing safe destination.

The generator copies this reproduction directory and itself into the destination, so
the resulting project remains self-reproducible.
