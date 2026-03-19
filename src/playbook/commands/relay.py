"""playbook relay — assemble a complete relay prompt for a task."""

import subprocess
import sys

import click

from playbook.config import find_project_root, get_project_paths


INSTRUCTIONS_BLOCK = """\
Execute the task above. Follow the spec exactly.

If you encounter a conflict, ambiguity, or something that seems wrong:
1. Document the concern at the top of your output
2. Complete the task as spec'd anyway
3. Do not improvise alternatives unless the spec is impossible to follow

When done, provide your output in this format:

## CONCERNS (if any)
- [describe any spec conflicts, ambiguities, or issues]

## FILES MODIFIED
- path/to/file.py (created/modified)

## VERIFICATION
- [what you tested and results]

## STATUS
COMPLETE | BLOCKED (reason)"""


@click.command("relay")
@click.argument("task_number")
@click.option("--copy", is_flag=True, default=False, help="Copy prompt to clipboard via xclip")
def relay_cmd(task_number, copy):
    """Assemble a complete relay prompt for a specific task."""
    try:
        root = find_project_root()
    except click.ClickException:
        click.echo("Error: Not a playbook project (PLAYBOOK.md not found)", err=True)
        sys.exit(1)

    paths = get_project_paths(root)

    # Read AGENT_CONTEXT.md
    agent_context_path = paths["agent_context"]
    if not agent_context_path.exists():
        click.echo("Error: AGENT_CONTEXT.md not found", err=True)
        sys.exit(3)
    agent_context = agent_context_path.read_text()

    # Read SPEC.md
    spec_path = paths["spec"]
    if not spec_path.exists():
        click.echo("Error: SPEC.md not found", err=True)
        sys.exit(3)
    spec = spec_path.read_text()

    # Find task file matching NNN
    padded = task_number.zfill(3)
    tasks_dir = paths["tasks_dir"]
    matches = sorted(tasks_dir.glob(f"{padded}-*.md"))
    if not matches:
        click.echo(f"Error: No task file found matching {padded} in tasks/", err=True)
        sys.exit(2)
    task_file = matches[0]
    task_content = task_file.read_text()

    # Assemble prompt
    prompt = (
        f"=== AGENT CONTEXT ===\n\n"
        f"{agent_context}\n"
        f"=== PROJECT SPEC ===\n\n"
        f"{spec}\n"
        f"=== CURRENT TASK ===\n\n"
        f"{task_content}\n"
        f"=== INSTRUCTIONS ===\n\n"
        f"{INSTRUCTIONS_BLOCK}\n"
    )

    # Output
    if copy:
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=prompt.encode(),
                check=True,
            )
        except FileNotFoundError:
            click.echo("Warning: xclip not found, printing to stdout instead", err=True)
            click.echo(prompt, nl=False)
    else:
        click.echo(prompt, nl=False)

    # Stats to stderr
    word_count = len(prompt.split())
    char_count = len(prompt)
    click.echo(f"--- {word_count} words, {char_count} chars ---", err=True)
