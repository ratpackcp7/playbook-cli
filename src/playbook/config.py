"""Project detection and path resolution."""

from pathlib import Path

import click


def find_project_root(start_path: Path = None) -> Path:
    """Walk up from start_path looking for a directory containing PLAYBOOK.md.

    Returns the Path to the project root directory.
    Raises click.ClickException if no PLAYBOOK.md is found.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    while True:
        if (current / "PLAYBOOK.md").exists():
            return current
        parent = current.parent
        if parent == current:
            raise click.ClickException(
                "Not a playbook project (PLAYBOOK.md not found)"
            )
        current = parent


def get_project_paths(root: Path) -> dict:
    """Return dict of standard project paths relative to root."""
    return {
        "root": root,
        "spec": root / "SPEC.md",
        "agent_context": root / "AGENT_CONTEXT.md",
        "tasks_md": root / "TASKS.md",
        "tasks_dir": root / "tasks",
        "reviews_dir": root / "reviews",
    }
