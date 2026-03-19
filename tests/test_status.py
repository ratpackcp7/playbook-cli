"""Tests for playbook status command."""

import pytest
from click.testing import CliRunner

from playbook.cli import cli


@pytest.fixture
def in_project(tmp_project, monkeypatch):
    """Change to tmp_project directory for the duration of the test."""
    monkeypatch.chdir(tmp_project)
    return tmp_project


def test_status_single_task(in_project):
    """Status with 1 task shows task info and 0/1 complete."""
    runner = CliRunner()
    result = runner.invoke(cli, ["status"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "001" in result.output
    assert "Example" in result.output
    assert "TODO" in result.output
    assert "0/1 tasks complete" in result.output


def test_status_mixed_tasks(in_project):
    """Status with 3 tasks of mixed status shows correct summary."""
    tasks_md = in_project / "TASKS.md"
    tasks_md.write_text(
        "| # | Task | Status | Depends On | Notes |\n"
        "|---|---|---|---|---|\n"
        "| 001 | Scaffold | `[ ]` | — | |\n"
        "| 002 | Config | `[✓]` | 001 | |\n"
        "| 003 | Parser | `[!]` | 001 | failed |\n"
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["status"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "1/3 tasks complete" in result.output
    assert "TODO" in result.output
    assert "DONE" in result.output
    assert "FAILED" in result.output


def test_status_empty_tasks(in_project):
    """Status with 0 tasks (just header) shows 0/0 and no crash."""
    tasks_md = in_project / "TASKS.md"
    tasks_md.write_text(
        "| # | Task | Status | Depends On | Notes |\n"
        "|---|---|---|---|---|\n"
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["status"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "0/0 tasks complete" in result.output


def test_status_outside_project(tmp_path, monkeypatch):
    """Status outside a playbook project exits with code 1."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["status"])

    assert result.exit_code == 1


def test_status_shows_project_name(in_project):
    """Status output contains the project directory name as header."""
    runner = CliRunner()
    result = runner.invoke(cli, ["status"], catch_exceptions=False)

    assert "test-project" in result.output
