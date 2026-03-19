"""Tests for playbook relay command."""

import pytest
from click.testing import CliRunner

from playbook.cli import cli


@pytest.fixture
def in_project(tmp_project, monkeypatch):
    """Change to tmp_project directory and create a sample task file."""
    monkeypatch.chdir(tmp_project)
    task_file = tmp_project / "tasks" / "001-example.md"
    task_file.write_text("# Task 001: Example\n\nDo the thing.\n")
    return tmp_project


def test_relay_contains_all_section_headers(in_project):
    """relay 001 output contains all 4 section headers."""
    runner = CliRunner()
    result = runner.invoke(cli, ["relay", "001"], catch_exceptions=False)

    assert result.exit_code == 0
    for header in [
        "=== AGENT CONTEXT ===",
        "=== PROJECT SPEC ===",
        "=== CURRENT TASK ===",
        "=== INSTRUCTIONS ===",
    ]:
        assert header in result.output


def test_relay_contains_agent_context(in_project):
    """relay 001 output includes content from AGENT_CONTEXT.md."""
    runner = CliRunner()
    result = runner.invoke(cli, ["relay", "001"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "# Agent Context" in result.output


def test_relay_contains_task_content(in_project):
    """relay 001 output includes content from the task file."""
    runner = CliRunner()
    result = runner.invoke(cli, ["relay", "001"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "Do the thing." in result.output


def test_relay_no_zero_padding(in_project):
    """relay 1 (no zero-padding) works the same as 001."""
    runner = CliRunner()
    result = runner.invoke(cli, ["relay", "1"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "=== AGENT CONTEXT ===" in result.output
    assert "Do the thing." in result.output


def test_relay_nonexistent_task(in_project):
    """relay 999 (nonexistent task) exits non-zero."""
    runner = CliRunner()
    result = runner.invoke(cli, ["relay", "999"])

    assert result.exit_code != 0


def test_relay_missing_spec(in_project):
    """relay with SPEC.md deleted exits non-zero."""
    (in_project / "SPEC.md").unlink()
    runner = CliRunner()
    result = runner.invoke(cli, ["relay", "001"])

    assert result.exit_code != 0


def test_relay_missing_agent_context(in_project):
    """relay with AGENT_CONTEXT.md deleted exits non-zero."""
    (in_project / "AGENT_CONTEXT.md").unlink()
    runner = CliRunner()
    result = runner.invoke(cli, ["relay", "001"])

    assert result.exit_code != 0


def test_relay_copy_without_xclip(in_project):
    """relay --copy without xclip falls back to stdout, no crash."""
    runner = CliRunner()
    result = runner.invoke(cli, ["relay", "001", "--copy"], catch_exceptions=False)

    # Should not crash — falls back to stdout
    assert result.exit_code == 0
    assert "=== AGENT CONTEXT ===" in result.output
