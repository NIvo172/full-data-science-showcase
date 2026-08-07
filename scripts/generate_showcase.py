# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "copier>=9.17,<10",
# ]
# ///

"""Reproduce the full data-science showcase from the template's current HEAD."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPRODUCTION_ROOT = PROJECT_ROOT / "reproduction"
ANSWERS_FILE = REPRODUCTION_ROOT / "copier-data.yml"
OVERLAY_ROOT = REPRODUCTION_ROOT / "overlay"
README_SECTION_FILE = REPRODUCTION_ROOT / "showcase-readme-section.md"
DEFAULT_TEMPLATE = PROJECT_ROOT.parent / "python-project-copier-template"
TEMPLATE_REF = "HEAD"

# TODO: Replace mutable HEAD with an immutable template release tag or commit once the
# template release workflow is established.


def parse_arguments() -> argparse.Namespace:
    """Parse generator options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="Directory receiving the reproduced showcase.")
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help=f"Template Git checkout; default: {DEFAULT_TEMPLATE}",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing safe destination.")
    parser.add_argument("--initialize", action="store_true", help="Run init_project.py after generation.")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Initialise the result and run its exhaustive validation driver.",
    )
    parser.add_argument("--git-name", default="John Doe", help="Repository-local Git author name.")
    parser.add_argument("--git-email", default="john.doe@example.com", help="Repository-local Git author email.")
    return parser.parse_args()


def load_answers() -> dict[str, Any]:
    """Load the JSON-compatible YAML answer mapping."""
    answers = json.loads(ANSWERS_FILE.read_text(encoding="utf-8"))
    if not isinstance(answers, dict):
        raise TypeError(f"Expected an answer mapping in {ANSWERS_FILE}.")
    return answers


def resolve_template_head(template: Path) -> str:
    """Return the template HEAD commit or fail with an actionable message."""
    if not (template / "copier.yml").is_file():
        raise RuntimeError(f"Template does not contain copier.yml: {template}")

    root_result = subprocess.run(
        ("git", "-C", str(template), "rev-parse", "--show-toplevel"),
        capture_output=True,
        text=True,
        check=False,
    )
    result = subprocess.run(
        ("git", "-C", str(template), "rev-parse", "--verify", "HEAD^{commit}"),
        capture_output=True,
        text=True,
        check=False,
    )
    is_checkout_root = root_result.returncode == 0 and Path(root_result.stdout.strip()).resolve() == template.resolve()
    if not is_checkout_root or result.returncode != 0:
        raise RuntimeError(
            "The template must be a Git repository with a valid HEAD. "
            f"Git reported: {result.stderr.strip() or root_result.stderr.strip() or 'checkout root or HEAD not found'}"
        )
    return result.stdout.strip()


def validate_destination(destination: Path, template: Path) -> None:
    """Reject destinations that could overwrite the source or template checkout."""
    filesystem_root = Path(destination.anchor)
    home = Path.home().resolve()
    unsafe = (
        destination in (filesystem_root, home, PROJECT_ROOT, template)
        or destination.is_relative_to(PROJECT_ROOT)
        or PROJECT_ROOT.is_relative_to(destination)
        or destination.is_relative_to(template)
        or template.is_relative_to(destination)
    )
    if unsafe:
        raise RuntimeError(f"Refusing unsafe destination: {destination}")


def normalize_copier_source(destination: Path, template: Path) -> None:
    """Store the local template path relative to the reproduced project."""
    answers_path = destination / ".copier-answers.yml"
    relative_template = Path(os.path.relpath(template, destination)).as_posix()
    lines = answers_path.read_text(encoding="utf-8").splitlines()
    normalized = [f"_src_path: {relative_template}" if line.startswith("_src_path:") else line for line in lines]
    answers_path.write_text("\n".join(normalized) + "\n", encoding="utf-8")


def apply_showcase_readme(destination: Path) -> None:
    """Insert the showcase-owned introduction into the rendered README."""
    readme_path = destination / "README.md"
    marker = "\n## Requirements\n"
    readme = readme_path.read_text(encoding="utf-8")
    if marker not in readme:
        raise RuntimeError("Could not locate the Requirements section in the rendered README.")
    section = README_SECTION_FILE.read_text(encoding="utf-8").strip()
    readme_path.write_text(readme.replace(marker, f"\n{section}\n\n## Requirements\n", 1), encoding="utf-8")


def configure_overlay_lint_exclusion(destination: Path) -> None:
    """Exclude stored overlay copies while linting their active root counterparts."""
    pyproject_path = destination / "pyproject.toml"
    marker = '    "reports",\n'
    exclusion = '    "reproduction/overlay",\n'
    pyproject = pyproject_path.read_text(encoding="utf-8")
    if exclusion in pyproject:
        return
    if marker not in pyproject:
        raise RuntimeError("Could not locate the Ruff exclusion list in pyproject.toml.")
    pyproject_path.write_text(pyproject.replace(marker, f"{marker}{exclusion}", 1), encoding="utf-8")


def configure_local_cache_ignores(destination: Path) -> None:
    """Ignore local cache directories used by exhaustive showcase validation."""
    gitignore_path = destination / ".gitignore"
    marker = ".tox/\n"
    entries = ".pre-commit-cache/\n.task-tmp/\n"
    gitignore = gitignore_path.read_text(encoding="utf-8")
    if entries in gitignore:
        return
    if marker not in gitignore:
        raise RuntimeError("Could not locate the environment section in .gitignore.")
    gitignore_path.write_text(gitignore.replace(marker, f"{marker}{entries}", 1), encoding="utf-8")


def configure_dvc_ignores(destination: Path) -> None:
    """Prevent stored reproduction sources from becoming a second DVC pipeline."""
    dvcignore_path = destination / ".dvcignore"
    entry = "/reproduction/overlay/"
    dvcignore = dvcignore_path.read_text(encoding="utf-8")
    if entry in dvcignore.splitlines():
        return
    note = "# The active pipeline files are checked at the project root; these are reproduction sources."
    dvcignore_path.write_text(f"{dvcignore.rstrip()}\n\n{note}\n{entry}\n", encoding="utf-8")


def copy_showcase_sources(destination: Path) -> None:
    """Apply the project overlay and copy the self-reproduction sources."""
    shutil.copytree(OVERLAY_ROOT, destination, dirs_exist_ok=True)
    shutil.copytree(REPRODUCTION_ROOT, destination / "reproduction", dirs_exist_ok=True)
    shutil.copy2(Path(__file__), destination / "scripts/generate_showcase.py")
    apply_showcase_readme(destination)
    configure_overlay_lint_exclusion(destination)
    configure_local_cache_ignores(destination)
    configure_dvc_ignores(destination)


def run(command: list[str], *, cwd: Path) -> None:
    """Run one lifecycle command."""
    print(f"$ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def generate(destination: Path, template: Path, *, force: bool) -> str:
    """Render the template HEAD and apply the complete showcase source."""
    from copier import run_copy  # type: ignore[import-not-found]

    destination = destination.resolve()
    template = template.resolve()
    validate_destination(destination, template)
    template_commit = resolve_template_head(template)

    if destination.exists():
        if not force:
            raise FileExistsError(f"Destination already exists: {destination}")
        shutil.rmtree(destination)

    run_copy(
        src_path=str(template),
        dst_path=destination,
        data=load_answers(),
        defaults=True,
        overwrite=True,
        vcs_ref=TEMPLATE_REF,
    )
    copy_showcase_sources(destination)
    normalize_copier_source(destination, template)
    return template_commit


def main() -> int:
    """Generate the showcase and optionally execute its lifecycle."""
    arguments = parse_arguments()
    destination = arguments.destination.resolve()

    try:
        template_commit = generate(destination, arguments.template, force=bool(arguments.force))
        print(f"Generated showcase from template HEAD {template_commit} at {destination}")

        if arguments.initialize or arguments.validate:
            run(
                [
                    "uv",
                    "run",
                    "scripts/init_project.py",
                    "--git-name",
                    str(arguments.git_name),
                    "--git-email",
                    str(arguments.git_email),
                ],
                cwd=destination,
            )
        if arguments.validate:
            run(["uv", "run", "--locked", "python", "scripts/validate_full_project.py"], cwd=destination)
        elif not arguments.initialize:
            print(f"Next: uv run {destination / 'scripts/init_project.py'}")
            print(f"Then: cd {destination} && uv run --locked tox")
    except (FileExistsError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Showcase generation failed: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
