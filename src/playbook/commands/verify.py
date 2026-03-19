"""playbook verify <NNN> — run the Verify block from a task file."""

import re
import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

from playbook.config import find_project_root


def _find_task_file(tasks_dir: Path, number: str) -> Path | None:
    """Find the task file matching the given number."""
    pattern = re.compile(rf"^{re.escape(number)}-.*\.md$")
    for f in tasks_dir.iterdir():
        if pattern.match(f.name):
            return f
    return None


def _extract_verify_commands(task_content: str) -> list[str] | None:
    """Extract bash commands from the ## Verify section's code block."""
    lines = task_content.splitlines()
    in_verify = False
    in_code_block = False
    commands = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## Verify"):
            in_verify = True
            continue
        if in_verify and not in_code_block:
            if stripped.startswith("```"):
                in_code_block = True
                continue
            if stripped.startswith("## "):
                break
        if in_verify and in_code_block:
            if stripped.startswith("```"):
                break
            if stripped:
                commands.append(stripped)

    if not in_verify:
        return None
    return commands if commands else None


@click.command("verify")
@click.argument("task_number")
def verify_cmd(task_number: str) -> None:
    """Run the Verify block from a task file."""
    console = Console()

    try:
        root = find_project_root()
    except click.ClickException:
        console.print("[red]Error:[/red] Not a playbook project (PLAYBOOK.md not found)")
        sys.exit(1)

    number = task_number.zfill(3)
    tasks_dir = root / "tasks"

    task_file = _find_task_file(tasks_dir, number)
    if task_file is None:
        console.print(f"[red]Error:[/red] No task file found for {number}")
        sys.exit(1)

    content = task_file.read_text(encoding="utf-8")
    commands = _extract_verify_commands(content)

    if commands is None:
        console.print(f"No verify block in task {number}")
        sys.exit(0)

    all_passed = True
    for cmd in commands:
        console.print(f"[bold]$ {cmd}[/bold]")
        result = subprocess.run(cmd, shell=True, cwd=root)
        if result.returncode == 0:
            console.print(f"  [green]PASS[/green]")
        else:
            console.print(f"  [red]FAIL[/red] (exit code {result.returncode})")
            all_passed = False

    sys.exit(0 if all_passed else 1)
