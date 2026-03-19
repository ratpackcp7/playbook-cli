"""Tests for playbook task new command."""

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from playbook.cli import cli
from playbook.commands.task import slugify
from playbook.parser import parse_tasks


@pytest.fixture
def in_project(tmp_project, monkeypatch):
    """Change to tmp_project directory for the duration of the test."""
    monkeypatch.chdir(tmp_project)
    return tmp_project


def test_task_new_creates_numbered_file(in_project):
    """task new in project with 001-example.md creates 002-build-the-api.md."""
    (in_project / "tasks" / "001-example.md").write_text("# Task 001: Example\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["task", "new", "Build the API"], catch_exceptions=False)
    assert result.exit_code == 0, result.output

    task_file = in_project / "tasks" / "002-build-the-api.md"
    assert task_file.exists()
    content = task_file.read_text()
    assert "Task 002" in content
    assert "Build the API" in content


def test_task_new_template_replacement(in_project):
    """Created task file has _TEMPLATE.md structure with NNN and [Title] replaced."""
    (in_project / "tasks" / "001-example.md").write_text("# Task 001: Example\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["task", "new", "Build the API"], catch_exceptions=False)
    assert result.exit_code == 0

    task_file = in_project / "tasks" / "002-build-the-api.md"
    content = task_file.read_text()
    assert "# Task 002: Build the API" in content
    assert "NNN" not in content
    assert "[Title]" not in content


def test_task_new_appends_to_tasks_md(in_project):
    """TASKS.md gets a new row with backtick-wrapped status."""
    (in_project / "tasks" / "001-example.md").write_text("# Task 001: Example\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["task", "new", "Build the API"], catch_exceptions=False)
    assert result.exit_code == 0

    tasks_md = (in_project / "TASKS.md").read_text()
    assert "| 002 | Build the API | `[ ]` | — | |" in tasks_md


def test_task_new_parse_tasks_roundtrip(in_project):
    """parse_tasks returns both original and new row after task new."""
    (in_project / "tasks" / "001-example.md").write_text("# Task 001: Example\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["task", "new", "Build the API"], catch_exceptions=False)
    assert result.exit_code == 0

    rows = parse_tasks(in_project / "TASKS.md")
    assert len(rows) == 2
    assert rows[0]["number"] == "001"
    assert rows[1]["number"] == "002"
    assert rows[1]["task"] == "Build the API"
    assert rows[1]["status"] == "[ ]"


def test_task_new_starts_at_001_when_no_numbered_files(in_project):
    """First task in empty tasks/ dir starts at 001."""
    runner = CliRunner()
    result = runner.invoke(cli, ["task", "new", "First Task"], catch_exceptions=False)
    assert result.exit_code == 0

    task_file = in_project / "tasks" / "001-first-task.md"
    assert task_file.exists()


def test_slugify_special_chars():
    """Slugify strips special chars correctly."""
    assert slugify("Hello, World! (v2)") == "hello-world-v2"


def test_slugify_multiple_spaces():
    """Slugify collapses multiple spaces/hyphens."""
    assert slugify("  too   many  spaces  ") == "too-many-spaces"


def test_task_new_from_subdirectory(in_project):
    """Running from a subdirectory still finds the project root."""
    subdir = in_project / "tasks"
    os.chdir(subdir)
    runner = CliRunner()
    result = runner.invoke(cli, ["task", "new", "Sub Task"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (in_project / "tasks" / "001-sub-task.md").exists()


def test_task_new_outside_project(tmp_path, monkeypatch):
    """Running outside a playbook project exits with code 1."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["task", "new", "Orphan Task"])
    assert result.exit_code == 1


def test_task_done_marks_complete(in_project):
    """playbook task done 001 changes status to [✓] in TASKS.md."""
    runner = CliRunner()
    result = runner.invoke(cli, ["task", "done", "001"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "Task 001 marked complete" in result.output

    tasks_md = (in_project / "TASKS.md").read_text()
    assert "`✓`" in tasks_md


def test_task_done_not_found(in_project):
    """playbook task done 999 exits non-zero when task not found."""
    runner = CliRunner()
    result = runner.invoke(cli, ["task", "done", "999"])
    assert result.exit_code == 2


def test_task_done_roundtrip(in_project):
    """parse_tasks after done shows status as [✓]."""
    runner = CliRunner()
    result = runner.invoke(cli, ["task", "done", "1"], catch_exceptions=False)
    assert result.exit_code == 0

    rows = parse_tasks(in_project / "TASKS.md")
    assert len(rows) == 1
    assert rows[0]["status"] == "✓"
