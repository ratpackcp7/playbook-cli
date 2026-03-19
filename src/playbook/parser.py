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
