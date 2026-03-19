"""Tests for playbook check command."""

from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from playbook.cli import cli


@pytest.fixture
def in_project(tmp_project, monkeypatch):
    """Change to tmp_project directory with a task file and agent report."""
    monkeypatch.chdir(tmp_project)
    task_file = tmp_project / "tasks" / "001-example.md"
    task_file.write_text("# Task 001: Example\n\nDo the thing.\n\n## Acceptance Criteria\n\n1. Thing is done\n")
    return tmp_project


def _mock_response(text="## Criterion 1\nPASS — looks good\n\n## Overall Verdict\nPASS"):
    """Create a mock httpx response."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "choices": [{"message": {"content": text}}]
    }
    mock.raise_for_status = MagicMock()
    return mock


def test_check_sends_task_and_report(in_project, monkeypatch):
    """check sends task + report content to the API."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    (in_project / ".playbook-report.md").write_text("## FILES MODIFIED\n- foo.py\n\n## STATUS\nCOMPLETE\n")

    with patch("playbook.commands.check.httpx.post", return_value=_mock_response()) as mock_post:
        runner = CliRunner()
        result = runner.invoke(cli, ["check", "001"], catch_exceptions=False)

    assert result.exit_code == 0
    # Verify the API was called with task and report content
    call_args = mock_post.call_args
    body = call_args.kwargs.get("json") or call_args[1].get("json")
    user_msg = body["messages"][1]["content"]
    assert "Do the thing." in user_msg
    assert "FILES MODIFIED" in user_msg
    # Verify review file was written
    assert (in_project / "reviews" / "check-001.md").exists()


def test_check_no_report(in_project, monkeypatch):
    """check with no .playbook-report.md exits non-zero."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "001"])

    assert result.exit_code != 0
    assert "No agent report found" in result.output or "No agent report found" in (result.output + getattr(result, 'stderr', ''))


def test_check_outside_project(tmp_path, monkeypatch):
    """check outside a playbook project exits non-zero."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["check", "001"])

    assert result.exit_code != 0
