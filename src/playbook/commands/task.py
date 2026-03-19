"""playbook task new "<title>" — create the next numbered task file."""

import re
import sys
from pathlib import Path

import click
from rich.console import Console

from playbook.config import find_project_root
from playbook.parser import append_task_row


def slugify(title: str) -> str:
    """Convert a title to a filename-safe slug.

    Rules: lowercase, spaces to hyphens, strip non-alphanumeric except hyphens,
    collapse multiple hyphens, strip leading/trailing hyphens, max 50 chars.
    """
    slug = title.lower()
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug.strip("-")
    slug = slug[:50]
    return slug


def find_next_number(tasks_dir: Path) -> str:
    """Scan tasks/ for highest-numbered .md file, return next number zero-padded to 3 digits."""
    pattern = re.compile(r"^(\d{3})-(.+)\.md$")
    highest = 0
    for f in tasks_dir.iterdir():
        match = pattern.match(f.name)
        if match:
            num = int(match.group(1))
            if num > highest:
                highest = num
    return f"{highest + 1:03d}"


@click.group("task")
def task_group():
    """Manage project tasks."""
    pass


@task_group.command("new")
@click.argument("title")
def new_cmd(title: str) -> None:
    """Create the next numbered task file."""
    console = Console()

    try:
        root = find_project_root()
    except click.ClickException:
        console.print("[red]Error:[/red] Not a playbook project (PLAYBOOK.md not found)")
        sys.exit(1)

    tasks_dir = root / "tasks"
    template_path = tasks_dir / "_TEMPLATE.md"

    if not template_path.exists():
        console.print("[red]Error:[/red] _TEMPLATE.md not found in tasks/")
        sys.exit(2)

    number = find_next_number(tasks_dir)
    slug = slugify(title)
    filename = f"{number}-{slug}.md"

    # Read template and replace placeholders
    template_content = template_path.read_text(encoding="utf-8")
    content = template_content.replace("NNN", number).replace("[Title]", title)

    # Write new task file
    task_path = tasks_dir / filename
    task_path.write_text(content, encoding="utf-8")

    # Append row to TASKS.md
    tasks_md_path = root / "TASKS.md"
    append_task_row(tasks_md_path, number, title)

    console.print(f"[green]✓[/green] Created {task_path.relative_to(root)}")
