"""playbook status — display color-coded task queue."""

import sys

import click
from rich.console import Console
from rich.text import Text

from playbook.config import find_project_root, get_project_paths
from playbook.parser import parse_tasks


STATUS_MAP = {
    "[ ]": ("TODO", "dim white"),
    "[>]": ("IN PROGRESS", "yellow"),
    "[✓]": ("DONE", "green"),
    "[!]": ("FAILED", "red"),
    "[~]": ("SKIPPED", "dim strikethrough"),
}


@click.command("status")
def status_cmd():
    """Show the current task queue with status indicators."""
    try:
        root = find_project_root()
    except click.ClickException:
        click.echo("Error: Not a playbook project (PLAYBOOK.md not found)", err=True)
        sys.exit(1)

    paths = get_project_paths(root)

    try:
        tasks = parse_tasks(paths["tasks_md"])
    except Exception as e:
        click.echo(f"Error: Could not parse TASKS.md: {e}", err=True)
        sys.exit(2)

    console = Console()

    # Header: project name
    project_name = root.name
    console.print(Text(project_name, style="bold"))
    console.print()

    # Task lines
    for task in tasks:
        number = task["number"]
        title = task["task"]
        status = task["status"]

        label, style = STATUS_MAP.get(status, ("UNKNOWN", "white"))

        line = Text()
        line.append(f"  {number}  {title} ", style=style)
        dots = "." * max(1, 50 - len(title))
        line.append(f"{dots} ", style=style)
        line.append(label, style=style)
        console.print(line)

    # Summary
    done_count = sum(1 for t in tasks if t["status"] == "[✓]")
    total_count = len(tasks)
    console.print()
    console.print(f"{done_count}/{total_count} tasks complete")
