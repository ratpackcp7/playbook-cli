"""Tests for playbook verify command."""

import os

import pytest
from click.testing import CliRunner

from playbook.cli import cli


TASK_WITH_VERIFY = """\
# Task 001: Example

## Objective
Do something.

## Verify
```bash
echo "hello"
true
```

## Notes
Done.
"""

TASK_WITHOUT_VERIFY = """\
# Task 001: Example

## Objective
Do something.

## Notes
Done.
"""


@pytest.fixture
def in_project(tmp_project, monkeypatch):
    monkeypatch.chdir(tmp_project)
    return tmp_project


def test_verify_runs_commands(in_project):
    """playbook verify on a task with a Verify bash block runs the commands."""
    (in_project / "tasks" / "001-example.md").write_text(TASK_WITH_VERIFY)
    runner = CliRunner()
    result = runner.invoke(cli, ["verify", "001"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "PASS" in result.output


def test_verify_no_verify_section(in_project):
    """playbook verify on a task with no Verify section prints message, exits 0."""
    (in_project / "tasks" / "001-example.md").write_text(TASK_WITHOUT_VERIFY)
    runner = CliRunner()
    result = runner.invoke(cli, ["verify", "001"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "No verify block in task 001" in result.output


def test_verify_task_not_found(in_project):
    """playbook verify 999 exits non-zero when task file not found."""
    runner = CliRunner()
    result = runner.invoke(cli, ["verify", "999"])
    assert result.exit_code == 1
    assert "No task file found" in result.output
