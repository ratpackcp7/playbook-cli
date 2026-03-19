"""Tests for config module."""

import pytest
import click

from playbook.config import find_project_root, get_project_paths


def test_find_project_root_from_root(tmp_project):
    """find_project_root from project root returns that directory."""
    result = find_project_root(tmp_project)
    assert result == tmp_project


def test_find_project_root_from_subdirectory(tmp_project):
    """find_project_root from tasks/ subdirectory returns parent project root."""
    tasks_dir = tmp_project / "tasks"
    result = find_project_root(tasks_dir)
    assert result == tmp_project


def test_find_project_root_not_found(tmp_path):
    """find_project_root raises ClickException when no PLAYBOOK.md exists."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with pytest.raises(click.ClickException, match="Not a playbook project"):
        find_project_root(empty_dir)


def test_get_project_paths(tmp_project):
    """get_project_paths returns dict with all expected keys relative to root."""
    paths = get_project_paths(tmp_project)

    assert paths["root"] == tmp_project
    assert paths["spec"] == tmp_project / "SPEC.md"
    assert paths["agent_context"] == tmp_project / "AGENT_CONTEXT.md"
    assert paths["tasks_md"] == tmp_project / "TASKS.md"
    assert paths["tasks_dir"] == tmp_project / "tasks"
    assert paths["reviews_dir"] == tmp_project / "reviews"
