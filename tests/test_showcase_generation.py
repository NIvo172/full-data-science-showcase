"""Contracts for the self-contained showcase generator."""

from __future__ import annotations

import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from shutil import which
from types import ModuleType

import pytest


def require_git() -> str:
    """Return the Git executable required by these integration contracts."""
    executable = which("git")
    if executable is None:
        raise RuntimeError("Git is required to test showcase reproduction.")
    return executable


GIT = require_git()


def run_git(*arguments: str, cwd: Path, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    """Run a trusted Git test command."""
    return subprocess.run(  # noqa: S603
        (GIT, *arguments), cwd=cwd, check=True, capture_output=capture_output, text=True
    )


def load_script_module(name: str, path: Path) -> ModuleType:
    """Load a project script without executing its command-line entry point."""
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = load_script_module("showcase_generator", PROJECT_ROOT / "scripts/generate_showcase.py")


def test_reproduction_answers_enable_every_capability() -> None:
    """Keep the stored Copier answers aligned with the all-features showcase."""
    answers = GENERATOR.load_answers()

    assert answers["project_kind"] == "data_science"
    assert answers["ci_provider"] == "github"
    for option in (
        "use_docs",
        "use_notebooks",
        "use_dvc",
        "use_uml",
        "use_example_gallery",
        "use_precommit",
        "use_vscode",
        "has_other_contributors",
    ):
        assert answers[option] is True


def test_reproduction_overlay_contains_every_showcase_owned_file() -> None:
    """Require the pipeline, documentation, data, and validation overlay."""
    required_paths = (
        "configs/models/baseline.yaml",
        "docs/source/data-science-example.md",
        "docs/source/documentation-guide.md",
        "docs/source/index.md",
        "docs/source/showcase-workflows.md",
        "dvc.yaml",
        "models/README.md",
        "references/data_dictionary.md",
        "reports/README.md",
        "scripts/validate_full_project.py",
        "src/full_data_science_example/pipeline.py",
        "tests/data/observations.csv",
        "tests/test_pipeline.py",
        "tests/test_project_workflows.py",
        "tests/test_showcase_generation.py",
    )

    for relative_path in required_paths:
        assert (GENERATOR.OVERLAY_ROOT / relative_path).is_file()

    assert not (GENERATOR.OVERLAY_ROOT / "docs/source/command-reference.md").exists()


def test_template_head_resolution_requires_a_git_commit(tmp_path: Path) -> None:
    """Require HEAD rather than silently rendering an unversioned directory."""
    template = tmp_path / "template"
    template.mkdir()
    (template / "copier.yml").write_text("_subdirectory: template\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="valid HEAD"):
        GENERATOR.resolve_template_head(template)

    run_git("init", "--initial-branch=main", cwd=template, capture_output=True)
    run_git("config", "user.name", "Showcase Test", cwd=template)
    run_git("config", "user.email", "showcase@example.com", cwd=template)
    run_git("add", "copier.yml", cwd=template)
    run_git("commit", "-m", "Template HEAD", cwd=template, capture_output=True)

    expected = run_git("rev-parse", "HEAD", cwd=template, capture_output=True).stdout.strip()
    assert GENERATOR.resolve_template_head(template) == expected


def test_readme_insertion_adds_head_policy_note(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the temporary mutable-HEAD policy visible in reproduced projects."""
    destination = tmp_path / "destination"
    destination.mkdir()
    (destination / "README.md").write_text("# Example\n\nDescription\n\n## Requirements\n", encoding="utf-8")
    section = tmp_path / "section.md"
    section.write_text("## About this showcase\n\nTemplate `HEAD` is temporary.\n", encoding="utf-8")
    monkeypatch.setattr(GENERATOR, "README_SECTION_FILE", section)

    GENERATOR.apply_showcase_readme(destination)

    readme = (destination / "README.md").read_text(encoding="utf-8")
    assert readme.index("## About this showcase") < readme.index("## Requirements")
    assert "Template `HEAD` is temporary." in readme


def test_current_readme_contains_the_owned_showcase_section() -> None:
    """Keep the checked-in README synchronized with reproduced projects."""
    section = GENERATOR.README_SECTION_FILE.read_text(encoding="utf-8").strip()

    assert section in (GENERATOR.PROJECT_ROOT / "README.md").read_text(encoding="utf-8")


def test_overlay_lint_exclusion_is_idempotent(tmp_path: Path) -> None:
    """Avoid checking stored duplicates while retaining checks for active files."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[tool.ruff]\nextend-exclude = [\n    "reports",\n]\n', encoding="utf-8")

    GENERATOR.configure_overlay_lint_exclusion(tmp_path)
    GENERATOR.configure_overlay_lint_exclusion(tmp_path)

    assert pyproject.read_text(encoding="utf-8").count('    "reproduction/overlay",') == 1


def test_local_cache_ignores_are_idempotent(tmp_path: Path) -> None:
    """Keep exhaustive-validation caches outside formatting and repository checks."""
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text(".venv/\n.tox/\n__pycache__/\n", encoding="utf-8")

    GENERATOR.configure_local_cache_ignores(tmp_path)
    GENERATOR.configure_local_cache_ignores(tmp_path)

    contents = gitignore.read_text(encoding="utf-8")
    assert contents.count(".pre-commit-cache/") == 1
    assert contents.count(".task-tmp/") == 1


def test_dvc_overlay_ignore_is_idempotent(tmp_path: Path) -> None:
    """Keep stored pipeline definitions out of DVC's active workspace graph."""
    dvcignore = tmp_path / ".dvcignore"
    dvcignore.write_text("# DVC exclusions\n", encoding="utf-8")

    GENERATOR.configure_dvc_ignores(tmp_path)
    GENERATOR.configure_dvc_ignores(tmp_path)

    assert dvcignore.read_text(encoding="utf-8").count("/reproduction/overlay/") == 1


def test_generator_refuses_to_replace_its_source_tree() -> None:
    """Protect the source and template repositories from force replacement."""
    with pytest.raises(RuntimeError, match="unsafe destination"):
        GENERATOR.validate_destination(GENERATOR.PROJECT_ROOT, GENERATOR.DEFAULT_TEMPLATE.resolve())

    assert GENERATOR.TEMPLATE_REF == "HEAD"
