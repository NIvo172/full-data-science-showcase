"""Contracts for the full generated project's validation workflow."""

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_script_module(name: str, path: Path) -> ModuleType:
    """Load one generated script without relying on the repository root being importable."""
    specification = spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise ImportError(f"Could not load {path}")
    module = module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


BUILD_DOCS = load_script_module("full_example_build_docs", PROJECT_ROOT / "scripts/build_docs.py")
VALIDATE_FULL_PROJECT = load_script_module(
    "full_example_validate_project", PROJECT_ROOT / "scripts/validate_full_project.py"
)


def test_full_validation_driver_covers_every_project_capability() -> None:
    """Keep the executable validation driver aligned with the full fixture."""
    validation_script = (PROJECT_ROOT / "scripts/validate_full_project.py").read_text(encoding="utf-8")
    required_commands = (
        'CLEAN_PROJECT = ("uv", "run", "--locked", "tox", "run", "-e", "clean")',
        'DEFAULT_SUITE = ("uv", "run", "--locked", "tox")',
        'PYTHON_MATRIX = ("uv", "run", "--locked", "tox", "run", "-m", "test")',
        'PRE_COMMIT = ("uv", "run", "--locked", "tox", "run", "-e", "pre-commit")',
        'DOCS_HTML = ("uv", "run", "--locked", "tox", "run", "-e", "docs", "--", "html")',
        'DOCS_COVERAGE = ("uv", "run", "--locked", "tox", "run", "-e", "docs", "--", "coverage")',
        'DOCS_ALL = ("uv", "run", "--locked", "tox", "run", "-e", "docs")',
        'UML = ("uv", "run", "--locked", "tox", "run", "-e", "uml")',
        'DVC_STATUS = ("uv", "run", "--locked", "--group", "dvc", "dvc", "status")',
        'DVC_METRICS = ("uv", "run", "--locked", "--group", "dvc", "dvc", "metrics", "show")',
        '"reports/figures/cumulative_mean.csv",\n    "--show-vega",',
        'DVC_EXPERIMENT = ("uv", "run", "--locked", "--group", "dvc", "dvc", "exp", "run")',
        'PACKAGE_CHECK = ("uv", "run", "--locked", "tox", "run", "-e", "package-check")',
        'BUILD = ("uv", "run", "--locked", "tox", "run", "-e", "build")',
    )

    for command in required_commands:
        assert command in validation_script


def test_full_validation_driver_checks_every_generated_artifact() -> None:
    """Require validation to inspect reports, distributions, and DVC outputs."""
    validation_script = (PROJECT_ROOT / "scripts/validate_full_project.py").read_text(encoding="utf-8")

    for path in (
        "reports/pytest/report.html",
        "reports/pytest/report.jsonl",
        "reports/coverage/html/index.html",
        "reports/coverage/coverage.xml",
        "reports/coverage/coverage.json",
        "reports/sphinx/html/index.html",
        "reports/sphinx/coverage/python.txt",
        "reports/sphinx/coverage/index.html",
        "data/processed/summary.json",
        "data/processed/metrics.json",
        "reports/figures/cumulative_mean.csv",
    ):
        assert path in validation_script

    assert "require_distributions()" in validation_script
    assert "require_no_coverage_data_files()" in validation_script
    assert "require_no_pytest_temporary_directories()" in validation_script
    assert "require_clean_worktree()" in validation_script


@pytest.mark.parametrize(
    ("target", "expected_events"),
    [
        ("clean", ["clean"]),
        ("html", ["build:html"]),
        ("coverage", ["build:coverage", "check:coverage"]),
        ("all", ["build:coverage", "check:coverage", "build:html"]),
    ],
)
def test_documentation_driver_dispatches_every_target(
    target: str,
    expected_events: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise every documentation command without recursively invoking Sphinx."""
    events: list[str] = []
    monkeypatch.setattr(BUILD_DOCS, "GENERATE_UML", False)
    monkeypatch.setattr(BUILD_DOCS, "clean_documentation", lambda: events.append("clean"))
    monkeypatch.setattr(BUILD_DOCS, "build", lambda builder: events.append(f"build:{builder}"))
    monkeypatch.setattr(BUILD_DOCS, "check_api_coverage", lambda: events.append("check:coverage"))
    monkeypatch.setattr(sys, "argv", ["build_docs.py", target])

    assert BUILD_DOCS.main() == 0
    assert events == expected_events


def test_full_validation_driver_executes_the_complete_manifest(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the orchestration logic with external commands replaced by recorders."""
    observed_commands: list[tuple[str, ...]] = []
    monkeypatch.setattr(VALIDATE_FULL_PROJECT, "run", observed_commands.append)
    monkeypatch.setattr(VALIDATE_FULL_PROJECT, "require_absent", lambda _paths: None)
    monkeypatch.setattr(VALIDATE_FULL_PROJECT, "require_nonempty_files", lambda _paths: None)
    monkeypatch.setattr(VALIDATE_FULL_PROJECT, "require_dvc_outputs", lambda: None)
    monkeypatch.setattr(VALIDATE_FULL_PROJECT, "require_distributions", lambda: None)
    monkeypatch.setattr(VALIDATE_FULL_PROJECT, "require_no_coverage_data_files", lambda: None)
    monkeypatch.setattr(VALIDATE_FULL_PROJECT, "require_no_pytest_temporary_directories", lambda: None)
    monkeypatch.setattr(VALIDATE_FULL_PROJECT, "require_clean_worktree", lambda: None)

    assert VALIDATE_FULL_PROJECT.main() == 0
    assert tuple(observed_commands) == VALIDATE_FULL_PROJECT.VALIDATION_COMMANDS


def test_sphinx_docs_separate_generated_commands_from_showcase_examples() -> None:
    """Keep canonical commands separate from fixture-specific walkthroughs."""
    index = (PROJECT_ROOT / "docs/source/index.md").read_text(encoding="utf-8")
    command_reference = (PROJECT_ROOT / "docs/source/command-reference.md").read_text(encoding="utf-8")
    workflows = (PROJECT_ROOT / "docs/source/showcase-workflows.md").read_text(encoding="utf-8")

    assert "readme\ncommand-reference\nshowcase-workflows\napi" in index
    assert "contains only commands supported by this project's selected Copier features" in command_reference
    assert "The exhaustive driver is deliberately showcase-specific" in workflows

    for command in (
        "uv run --locked tox",
        "uv run --locked tox run -m test",
        "uv run --locked tox run -e docs -- html",
        "uv run dvc repro",
        "uv run --locked tox run -e package-check",
        "uv run --locked python scripts/validate_full_project.py",
    ):
        assert command in workflows

    for expected_output in (
        "reports/pytest/report.html",
        "reports/coverage/",
        "reports/sphinx/html/index.html",
        "data/processed/summary.json",
        "reports/figures/cumulative_mean.csv",
        "dist/",
    ):
        assert expected_output in workflows

    assert "Mean `2.5`, record count `4`" in workflows
    assert "64-character input SHA-256 digest" in workflows
