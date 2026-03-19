"""Tests for the review-spec command."""

import os
from unittest.mock import MagicMock, patch

import httpx
import pytest
from click.testing import CliRunner

from playbook.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# 1. --dry-run exits 0, shows all 3 models, DRY RUN indicator, SPEC.md content
def test_dry_run_shows_models_and_spec(runner, tmp_project, monkeypatch):
    monkeypatch.chdir(tmp_project)
    result = runner.invoke(cli, ["review-spec", "--dry-run"])
    assert result.exit_code == 0
    assert "Dry Run" in result.output
    # All 3 default model names present
    assert "Gemini 2.5 Pro" in result.output
    assert "DeepSeek V3.2" in result.output
    assert "Qwen3 235B" in result.output
    # SPEC.md content included in user message preview
    assert "# Spec" in result.output


# 2. Outside a playbook project → exit 1
def test_outside_project_exits_1(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ["review-spec"])
    assert result.exit_code == 1


# 3. No OPENROUTER_API_KEY → exit 2
def test_no_api_key_exits_2(runner, tmp_project, monkeypatch):
    monkeypatch.chdir(tmp_project)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    result = runner.invoke(cli, ["review-spec"])
    assert result.exit_code == 2
    assert "OPENROUTER_API_KEY" in result.output


# 4. SPEC.md deleted → exit 3
def test_missing_spec_exits_3(runner, tmp_project, monkeypatch):
    monkeypatch.chdir(tmp_project)
    (tmp_project / "SPEC.md").unlink()
    result = runner.invoke(cli, ["review-spec"])
    assert result.exit_code == 3


# 5. --model filter shows only 1 model
def test_model_filter_single_model(runner, tmp_project, monkeypatch):
    monkeypatch.chdir(tmp_project)
    result = runner.invoke(cli, ["review-spec", "--model", "google/gemini-2.5-pro", "--dry-run"])
    assert result.exit_code == 0
    assert "Gemini 2.5 Pro" in result.output
    # Other models should NOT appear in the model panel listing
    assert "DeepSeek V3.2" not in result.output
    assert "Qwen3 235B" not in result.output


# 6. Mock: successful API call writes review file
def test_mock_api_writes_review_file(runner, tmp_project, monkeypatch):
    monkeypatch.chdir(tmp_project)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-fake")

    fake_response = MagicMock()
    fake_response.json.return_value = {
        "choices": [{"message": {"content": "1. Issue one\n2. Issue two\n3. Issue three"}}],
        "usage": {"prompt_tokens": 3000, "completion_tokens": 500},
    }
    fake_response.raise_for_status = MagicMock()

    with patch("playbook.reviewer.httpx.post", return_value=fake_response) as mock_post:
        result = runner.invoke(cli, ["review-spec", "--model", "deepseek/deepseek-chat"])

    assert result.exit_code == 0
    mock_post.assert_called_once()

    review_file = tmp_project / "reviews" / "spec-review-deepseek.md"
    assert review_file.exists()
    content = review_file.read_text()
    assert "Spec Review" in content
    assert "DeepSeek V3.2" in content
    assert "1. Issue one" in content
    assert "2. Issue two" in content


# 7. Mock: ConnectError → exit 4 with descriptive message
def test_mock_connect_error_exits_4(runner, tmp_project, monkeypatch):
    monkeypatch.chdir(tmp_project)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-fake")

    with patch("playbook.reviewer.httpx.post", side_effect=httpx.ConnectError("Connection refused")):
        result = runner.invoke(cli, ["review-spec", "--model", "deepseek/deepseek-chat"])

    assert result.exit_code == 4
    assert "Error" in result.output or "error" in result.output
