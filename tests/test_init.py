"""Tests for playbook init command."""

import os
from pathlib import Path

from click.testing import CliRunner

from playbook.cli import cli
from playbook.config import find_project_root
from playbook.templates import TEMPLATES


def test_init_creates_all_files(tmp_path):
    """playbook init test-project creates directory with all 9 files."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "test-project", "--no-git"])
        assert result.exit_code == 0

        project_dir = Path.cwd() / "test-project"
        for rel_path in TEMPLATES:
            file_path = project_dir / rel_path
            assert file_path.exists(), f"Missing file: {rel_path}"


def test_init_tasks_md_content(tmp_path):
    """TASKS.md content contains the expected header."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(cli, ["init", "test-project", "--no-git"])
        tasks_md = (Path.cwd() / "test-project" / "TASKS.md").read_text()
        assert "| # | Task | Status | Depends On | Notes |" in tasks_md


def test_init_template_has_nnn_placeholder(tmp_path):
    """_TEMPLATE.md in created project contains the NNN placeholder."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(cli, ["init", "test-project", "--no-git"])
        template = (Path.cwd() / "test-project" / "tasks" / "_TEMPLATE.md").read_text()
        assert "NNN" in template


def test_init_with_git(tmp_path):
    """.git/ directory exists when git is initialized."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "test-project"])
        assert result.exit_code == 0
        assert (Path.cwd() / "test-project" / ".git").is_dir()


def test_init_dir_already_exists(tmp_path):
    """Exits with code 1 when directory already exists."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        Path("test-project").mkdir()
        result = runner.invoke(cli, ["init", "test-project"])
        assert result.exit_code == 1
        assert "already exists" in result.output


def test_init_no_git_flag(tmp_path):
    """--no-git creates project without .git/ directory."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["init", "test-project", "--no-git"])
        assert result.exit_code == 0
        assert not (Path.cwd() / "test-project" / ".git").exists()


def test_init_valid_playbook_project(tmp_path):
    """Created project is detected as a valid playbook project."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(cli, ["init", "test-project", "--no-git"])
        project_dir = Path.cwd() / "test-project"
        root = find_project_root(project_dir)
        assert root == project_dir
