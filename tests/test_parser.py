"""Tests for parse_tasks."""

from playbook.parser import parse_tasks


def test_parse_single_row(tmp_project):
    """Parse TASKS.md with 1 row returns correct dict with no backticks in status."""
    tasks_md = tmp_project / "TASKS.md"
    result = parse_tasks(tasks_md)

    assert len(result) == 1
    row = result[0]
    assert row["number"] == "001"
    assert row["task"] == "Example"
    assert row["status"] == "[ ]"
    assert row["depends_on"] == "—"
    assert row["notes"] == "test"
    # Status must not contain backticks
    assert "`" not in row["status"]


def test_parse_mixed_statuses(tmp_project):
    """Parse TASKS.md with 3 rows with mixed statuses."""
    tasks_md = tmp_project / "TASKS.md"
    tasks_md.write_text(
        "| # | Task | Status | Depends On | Notes |\n"
        "|---|---|---|---|---|\n"
        "| 001 | First | `[ ]` | — | todo |\n"
        "| 002 | Second | `[✓]` | 001 | done |\n"
        "| 003 | Third | `[!]` | — | failed |\n"
    )

    result = parse_tasks(tasks_md)
    assert len(result) == 3
    assert result[0]["status"] == "[ ]"
    assert result[1]["status"] == "[✓]"
    assert result[2]["status"] == "[!]"


def test_parse_empty_table(tmp_project):
    """Parse TASKS.md with 0 data rows returns empty list."""
    tasks_md = tmp_project / "TASKS.md"
    tasks_md.write_text(
        "| # | Task | Status | Depends On | Notes |\n"
        "|---|---|---|---|---|\n"
    )

    result = parse_tasks(tasks_md)
    assert result == []


def test_parse_extra_whitespace(tmp_project):
    """Parse TASKS.md with extra whitespace in cells — values are stripped."""
    tasks_md = tmp_project / "TASKS.md"
    tasks_md.write_text(
        "| # | Task | Status | Depends On | Notes |\n"
        "|---|---|---|---|---|\n"
        "|  001  |  Spaced Task  |  `[ ]`  |  —  |  some notes  |\n"
    )

    result = parse_tasks(tasks_md)
    assert len(result) == 1
    assert result[0]["number"] == "001"
    assert result[0]["task"] == "Spaced Task"
    assert result[0]["status"] == "[ ]"
    assert result[0]["depends_on"] == "—"
    assert result[0]["notes"] == "some notes"


def test_parse_empty_rows_between_data(tmp_project):
    """Empty rows between data rows are skipped."""
    tasks_md = tmp_project / "TASKS.md"
    tasks_md.write_text(
        "| # | Task | Status | Depends On | Notes |\n"
        "|---|---|---|---|---|\n"
        "| 001 | First | `[ ]` | — | a |\n"
        "\n"
        "\n"
        "| 002 | Second | `[>]` | — | b |\n"
    )

    result = parse_tasks(tasks_md)
    assert len(result) == 2
    assert result[0]["number"] == "001"
    assert result[1]["number"] == "002"
