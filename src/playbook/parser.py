"""TASKS.md parser."""

from pathlib import Path


def parse_tasks(tasks_md_path: Path) -> list[dict]:
    """Parse TASKS.md and return a list of task dicts.

    Skips header row (starts with '| #'), separator rows (contain '|---|'),
    and empty rows. Strips backticks from status values.
    """
    text = tasks_md_path.read_text(encoding="utf-8")
    rows = []

    for line in text.splitlines():
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Skip non-table lines
        if not stripped.startswith("|"):
            continue

        # Skip header row
        if stripped.startswith("| #"):
            continue

        # Skip separator row
        if "|---|" in stripped:
            continue

        # Parse data row: split on |, strip each cell
        cells = [cell.strip() for cell in stripped.split("|")]
        # Leading and trailing | produce empty strings at start/end
        cells = [c for c in cells if c != "" or False]
        # Filter out empty strings from leading/trailing pipes
        cells = stripped.split("|")
        # Remove first and last empty elements from leading/trailing |
        cells = cells[1:-1]
        cells = [c.strip() for c in cells]

        if len(cells) < 5:
            continue

        # Strip backticks from status cell
        status = cells[2].strip("`")

        rows.append({
            "number": cells[0],
            "task": cells[1],
            "status": status,
            "depends_on": cells[3],
            "notes": cells[4],
        })

    return rows


def update_task_status(tasks_md_path: Path, number: str, new_status: str) -> bool:
    """Update the status cell of a task row in TASKS.md.

    Finds the row where the first cell matches number (after stripping),
    replaces the status cell with backtick-wrapped new_status.
    Returns True if found and updated, False if not found.
    """
    text = tasks_md_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    found = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if stripped.startswith("| #") or "|---|" in stripped:
            continue

        cells = stripped.split("|")
        if len(cells) < 6:  # leading empty + 5 cols + trailing empty
            continue

        cell_number = cells[1].strip()
        if cell_number == number:
            cells[3] = f" `{new_status}` "
            lines[i] = "|".join(cells)
            if not lines[i].endswith("\n"):
                lines[i] += "\n"
            found = True
            break

    if found:
        tasks_md_path.write_text("".join(lines), encoding="utf-8")
    return found


def append_task_row(tasks_md_path: Path, number: str, title: str) -> None:
    """Append a new task row to TASKS.md with backtick-wrapped status."""
    text = tasks_md_path.read_text(encoding="utf-8")
    if text and not text.endswith("\n"):
        text += "\n"
    text += f"| {number} | {title} | `[ ]` | — | |\n"
    tasks_md_path.write_text(text, encoding="utf-8")
