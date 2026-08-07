"""Run the full data-science example's end-to-end validation contract."""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SYNC = ("uv", "sync", "--locked")
CLEAN_PROJECT = ("uv", "run", "--locked", "tox", "run", "-e", "clean")
DEFAULT_SUITE = ("uv", "run", "--locked", "tox")
PYTHON_MATRIX = ("uv", "run", "--locked", "tox", "run", "-m", "test")
PRE_COMMIT = ("uv", "run", "--locked", "tox", "run", "-e", "pre-commit")
DOCS_CLEAN = ("uv", "run", "--locked", "tox", "run", "-e", "docs", "--", "clean")
DOCS_HTML = ("uv", "run", "--locked", "tox", "run", "-e", "docs", "--", "html")
DOCS_COVERAGE = ("uv", "run", "--locked", "tox", "run", "-e", "docs", "--", "coverage")
DOCS_ALL = ("uv", "run", "--locked", "tox", "run", "-e", "docs")
UML = ("uv", "run", "--locked", "tox", "run", "-e", "uml")
DVC_STATUS = ("uv", "run", "--locked", "--group", "dvc", "dvc", "status")
DVC_METRICS = ("uv", "run", "--locked", "--group", "dvc", "dvc", "metrics", "show")
DVC_PLOTS = (
    "uv",
    "run",
    "--locked",
    "--group",
    "dvc",
    "dvc",
    "plots",
    "show",
    "reports/figures/cumulative_mean.csv",
    "--show-vega",
)
DVC_EXPERIMENT = ("uv", "run", "--locked", "--group", "dvc", "dvc", "exp", "run")
PACKAGE_CHECK = ("uv", "run", "--locked", "tox", "run", "-e", "package-check")
BUILD = ("uv", "run", "--locked", "tox", "run", "-e", "build")
PIPELINE_HELP = ("uv", "run", "--locked", "python", "-m", "full_data_science_example.pipeline", "--help")

VALIDATION_COMMANDS = (
    SYNC,
    CLEAN_PROJECT,
    DEFAULT_SUITE,
    PYTHON_MATRIX,
    PRE_COMMIT,
    DOCS_CLEAN,
    DOCS_HTML,
    DOCS_COVERAGE,
    DOCS_ALL,
    UML,
    DVC_STATUS,
    DVC_METRICS,
    DVC_PLOTS,
    DVC_EXPERIMENT,
    PACKAGE_CHECK,
    BUILD,
    PIPELINE_HELP,
)

STANDARD_OUTPUTS = (
    Path("reports/pytest/report.html"),
    Path("reports/pytest/report.jsonl"),
    Path("reports/coverage/html/index.html"),
    Path("reports/coverage/coverage.xml"),
    Path("reports/coverage/coverage.json"),
    Path("reports/sphinx/html/index.html"),
    Path("reports/sphinx/coverage/python.txt"),
    Path("reports/sphinx/coverage/index.html"),
    Path("dvc.lock"),
    Path("data/processed/summary.json"),
    Path("data/processed/metrics.json"),
    Path("reports/figures/cumulative_mean.csv"),
)

CLEANED_OUTPUTS = (
    Path("build"),
    Path("dist"),
    Path("reports/coverage"),
    Path("reports/pytest"),
    Path("reports/sphinx"),
    Path("docs/_build"),
    Path("docs/source/_autosummary"),
    Path("docs/source/auto_examples"),
    Path("docs/source/sg_execution_times.rst"),
)

DOCUMENTATION_OUTPUTS = (
    Path("reports/sphinx/html/index.html"),
    Path("reports/sphinx/coverage/python.txt"),
    Path("reports/sphinx/coverage/index.html"),
)


def run(command: tuple[str, ...]) -> None:
    """Run one validation command from the repository root."""
    print(f"$ {shlex.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def require_nonempty_files(paths: tuple[Path, ...]) -> None:
    """Require every relative path to be a non-empty file."""
    missing = [str(path) for path in paths if not (ROOT / path).is_file() or (ROOT / path).stat().st_size == 0]
    if missing:
        raise RuntimeError("Expected non-empty files were not generated:\n- " + "\n- ".join(missing))


def require_absent(paths: tuple[Path, ...]) -> None:
    """Require generated paths to have been removed by a clean command."""
    retained = [str(path) for path in paths if (ROOT / path).exists()]
    if retained:
        raise RuntimeError("Generated paths remained after cleaning:\n- " + "\n- ".join(retained))


def require_no_coverage_data_files() -> None:
    """Require cleanup to remove primary and interrupted coverage data files."""
    retained = [ROOT / ".coverage", *ROOT.glob(".coverage.*")]
    retained = [path for path in retained if path.exists()]
    if retained:
        relative_paths = [str(path.relative_to(ROOT)) for path in retained]
        raise RuntimeError("Coverage data remained after cleaning:\n- " + "\n- ".join(relative_paths))


def require_no_pytest_temporary_directories() -> None:
    """Require cleanup to remove project-local pytest temporary directories."""
    retained = [path for path in ROOT.glob("pytest-of-*") if path.exists()]
    if retained:
        relative_paths = [str(path.relative_to(ROOT)) for path in retained]
        raise RuntimeError("Pytest temporary directories remained after cleaning:\n- " + "\n- ".join(relative_paths))


def require_distributions() -> None:
    """Require both source and wheel distributions."""
    source_distributions = sorted((ROOT / "dist").glob("*.tar.gz"))
    wheels = sorted((ROOT / "dist").glob("*.whl"))
    if not source_distributions or not wheels:
        raise RuntimeError("Expected both a source distribution and a wheel in dist/.")
    require_nonempty_files(tuple(path.relative_to(ROOT) for path in (*source_distributions, *wheels)))


def require_dvc_outputs() -> None:
    """Validate the deterministic DVC metrics and provenance outputs."""
    summary = json.loads((ROOT / "data/processed/summary.json").read_text(encoding="utf-8"))
    metrics = json.loads((ROOT / "data/processed/metrics.json").read_text(encoding="utf-8"))
    if summary["mean"] != 2.5 or summary["record_count"] != 4 or summary["round_digits"] != 3:
        raise RuntimeError(f"Unexpected DVC summary: {summary}")
    if len(summary["input_sha256"]) != 64:
        raise RuntimeError("The DVC summary does not contain a SHA-256 provenance digest.")
    if metrics != {"mean": 2.5, "record_count": 4}:
        raise RuntimeError(f"Unexpected DVC metrics: {metrics}")


def require_clean_worktree() -> None:
    """Require validation to leave tracked project files unchanged."""
    result = subprocess.run(
        ("git", "status", "--short"),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        raise RuntimeError(f"Validation left tracked worktree changes:\n{result.stdout}")


def main() -> int:
    """Execute every supported full-example validation path."""
    for command in VALIDATION_COMMANDS:
        run(command)
        if command == CLEAN_PROJECT:
            require_absent(CLEANED_OUTPUTS)
            require_no_coverage_data_files()
            require_no_pytest_temporary_directories()
        elif command == DEFAULT_SUITE:
            require_nonempty_files(STANDARD_OUTPUTS)
            require_dvc_outputs()
            require_distributions()
        elif command == DOCS_CLEAN:
            require_absent(DOCUMENTATION_OUTPUTS)
        elif command == DOCS_HTML:
            require_nonempty_files((Path("reports/sphinx/html/index.html"),))
        elif command == DOCS_COVERAGE:
            require_nonempty_files(
                (Path("reports/sphinx/coverage/python.txt"), Path("reports/sphinx/coverage/index.html"))
            )

    require_nonempty_files(STANDARD_OUTPUTS)
    require_dvc_outputs()
    require_distributions()
    require_clean_worktree()
    print("Full generated-project validation completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
