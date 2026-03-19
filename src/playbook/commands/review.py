"""playbook review-spec command."""

import sys

import click
from rich.console import Console

from playbook.config import find_project_root, get_project_paths
from playbook.reviewer import (
    DEFAULT_MODELS,
    SYSTEM_PROMPT,
    build_user_message,
    call_openrouter,
    count_issues,
    estimate_cost,
    estimate_tokens,
    extract_response_content,
    get_api_key,
    load_review_config,
    write_review_file,
)

console = Console()


@click.command("review-spec")
@click.option("--model", "model_filter", default=None, help="Run only one specific model ID instead of the full panel.")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be sent without making API calls.")
def review_spec_cmd(model_filter: str | None, dry_run: bool) -> None:
    """Send SPEC.md + TASKS.md to LLM models for adversarial review."""
    # 1. Detect project root
    try:
        root = find_project_root()
    except click.ClickException:
        console.print("[red]Error:[/red] Not a playbook project (PLAYBOOK.md not found)")
        sys.exit(1)

    paths = get_project_paths(root)

    # 2. Read SPEC.md and TASKS.md
    spec_path = paths["spec"]
    tasks_path = paths["tasks_md"]

    if not spec_path.exists() or not tasks_path.exists():
        missing = []
        if not spec_path.exists():
            missing.append("SPEC.md")
        if not tasks_path.exists():
            missing.append("TASKS.md")
        console.print(f"[red]Error:[/red] Missing required files: {', '.join(missing)}")
        sys.exit(3)

    spec_content = spec_path.read_text()
    tasks_content = tasks_path.read_text()

    # 3. Load model panel
    models = load_review_config(root)

    # Filter to single model if requested
    if model_filter:
        models = [m for m in models if m["id"] == model_filter]
        if not models:
            console.print(f"[red]Error:[/red] Model '{model_filter}' not found in panel.")
            console.print("Available models:")
            for m in load_review_config(root):
                console.print(f"  {m['id']}")
            sys.exit(1)

    # 4. Build prompt
    user_message = build_user_message(spec_content, tasks_content)
    input_tokens = estimate_tokens(SYSTEM_PROMPT + user_message)

    # 5. Dry run — show what would be sent
    if dry_run:
        console.print("\n[bold]Dry Run — review-spec[/bold]\n")
        console.print(f"[bold]Project root:[/bold] {root}")
        console.print(f"[bold]Input tokens (est):[/bold] ~{input_tokens}")
        console.print(f"\n[bold]System prompt:[/bold]")
        console.print(SYSTEM_PROMPT)
        console.print(f"\n[bold]User message[/bold] ({len(user_message)} chars):")
        # Show first 500 chars of user message
        preview = user_message[:500]
        if len(user_message) > 500:
            preview += f"\n... ({len(user_message) - 500} more chars)"
        console.print(preview)
        console.print(f"\n[bold]Model panel ({len(models)} models):[/bold]")
        for m in models:
            cost = estimate_cost(input_tokens)
            console.print(f"  {m['name']} ({m['role']})  — {m['id']}  ~${cost:.4f}")
        console.print()
        return

    # 6. Get API key (only needed for real calls)
    try:
        api_key = get_api_key()
    except SystemExit:
        console.print("[red]Error:[/red] OPENROUTER_API_KEY environment variable not set.")
        sys.exit(2)

    # 7. Call each model
    reviews_dir = paths["reviews_dir"]
    results = []
    total_cost = 0.0

    for model in models:
        console.print(f"  Reviewing with [bold]{model['name']}[/bold] ({model['role']})...", end=" ")
        try:
            api_response = call_openrouter(model["id"], api_key, user_message)
            response_text = extract_response_content(api_response)
            cost = estimate_cost(input_tokens)
            issues = count_issues(response_text)

            write_review_file(reviews_dir, model, response_text, input_tokens, cost)

            total_cost += cost
            results.append({"model": model, "issues": issues, "cost": cost})
            console.print("[green]done[/green]")
        except Exception as e:
            console.print(f"[red]failed[/red]")
            console.print(f"    [red]Error:[/red] {e}")
            sys.exit(4)

    # 8. Print summary
    console.print(f"\n[bold]Spec Review Complete[/bold]\n")
    for r in results:
        m = r["model"]
        label = f"{m['name']} ({m['role']})"
        console.print(f"  {label:<35} — {r['issues']:>3} issues  ~${r['cost']:.3f}")
    console.print(f"\n  Total estimated cost: ~${total_cost:.3f}")
    console.print(f"  Reviews written to {reviews_dir.relative_to(root)}/\n")
