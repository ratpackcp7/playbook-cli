"""playbook init <name> — create a new project from the playbook template."""

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

from playbook.templates import TEMPLATES


@click.command("init")
@click.argument("name")
@click.option("--no-git", is_flag=True, default=False, help="Skip git init and initial commit")
def init_cmd(name: str, no_git: bool) -> None:
    """Create a new project from the playbook template."""
    console = Console()
    project_dir = Path.cwd() / name

    # Fail if directory already exists
    if project_dir.exists():
        console.print(f"[red]Error:[/red] Directory '{name}' already exists.")
        sys.exit(1)

    # Create project directory
    project_dir.mkdir(parents=True)

    # Write all template files
    for rel_path, content in TEMPLATES.items():
        file_path = project_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    # Ensure tasks/ and reviews/ subdirectories exist
    (project_dir / "tasks").mkdir(exist_ok=True)
    (project_dir / "reviews").mkdir(exist_ok=True)

    file_count = len(TEMPLATES)

    # Git init unless --no-git
    if not no_git:
        try:
            subprocess.run(
                ["git", "init", "-b", "main"],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "add", "-A"],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial playbook from template"],
                cwd=project_dir,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error:[/red] Git initialization failed: {e}")
            sys.exit(2)

    console.print(f"[green]\u2713[/green] Created project [bold]{name}[/bold] with {file_count} files.")
    if not no_git:
        console.print("  Git repository initialized with initial commit.")
    console.print(f"  Edit [bold]{name}/SPEC.md[/bold] to get started.")
