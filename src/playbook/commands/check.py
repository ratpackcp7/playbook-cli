"""playbook check — verify task completion against agent report."""

import os
import sys

import click
import httpx
from rich.console import Console
from rich.markdown import Markdown

from playbook.config import find_project_root, get_project_paths

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
CHECK_MODEL = "google/gemini-3-flash-preview"

SYSTEM_PROMPT = (
    "You are verifying that a coding task was completed correctly. "
    "Compare the task requirements against the agent report. "
    "For each acceptance criterion, state PASS or FAIL with a one-line reason. "
    "End with an overall verdict: PASS or FAIL."
)


@click.command("check")
@click.argument("task_number")
def check_cmd(task_number):
    """Verify task completion by comparing task requirements against the agent report."""
    try:
        root = find_project_root()
    except click.ClickException:
        click.echo("Error: Not a playbook project (PLAYBOOK.md not found)", err=True)
        sys.exit(1)

    paths = get_project_paths(root)

    # Find task file matching NNN
    padded = task_number.zfill(3)
    tasks_dir = paths["tasks_dir"]
    matches = sorted(tasks_dir.glob(f"{padded}-*.md"))
    if not matches:
        click.echo(f"Error: No task file found matching {padded} in tasks/", err=True)
        sys.exit(2)
    task_file = matches[0]
    task_content = task_file.read_text()

    # Read agent report
    report_path = root / ".playbook-report.md"
    if not report_path.exists():
        click.echo("No agent report found.", err=True)
        sys.exit(1)
    report_content = report_path.read_text()

    # Get API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        click.echo("Error: OPENROUTER_API_KEY not set", err=True)
        sys.exit(2)

    # Build message
    user_message = (
        f"## TASK REQUIREMENTS\n\n{task_content}\n\n"
        f"## AGENT REPORT\n\n{report_content}"
    )

    # Call OpenRouter
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ratpackcp7/playbook-cli",
    }
    body = {
        "model": CHECK_MODEL,
        "max_tokens": 4000,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    }

    try:
        response = httpx.post(OPENROUTER_URL, json=body, headers=headers, timeout=120.0)
        response.raise_for_status()
    except httpx.HTTPError as e:
        click.echo(f"Error: API request failed: {e}", err=True)
        sys.exit(3)

    result_text = response.json()["choices"][0]["message"]["content"]

    # Print with Rich
    console = Console()
    console.print(Markdown(result_text))

    # Write review file
    reviews_dir = paths["reviews_dir"]
    reviews_dir.mkdir(parents=True, exist_ok=True)
    review_path = reviews_dir / f"check-{padded}.md"
    review_path.write_text(result_text + "\n")
    click.echo(f"\nReview written to reviews/check-{padded}.md", err=True)
