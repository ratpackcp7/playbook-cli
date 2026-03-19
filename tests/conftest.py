"""Shared test fixtures."""

import pytest
from pathlib import Path


SAMPLE_TASKS_MD = """\
| # | Task | Status | Depends On | Notes |
|---|---|---|---|---|
| 001 | Example | `[ ]` | — | test |
"""

SAMPLE_TEMPLATE = """\
# Task NNN: [Title]

## Objective

[What this task achieves]

## Deliverables

- [ ] Deliverable 1

## Acceptance Criteria

1. [ ] Criterion 1
"""


@pytest.fixture
def tmp_project(tmp_path):
    """Create a valid playbook project structure in a temp directory."""
    root = tmp_path / "test-project"
    root.mkdir()

    # Create sentinel and required files
    (root / "PLAYBOOK.md").write_text("# Playbook\n")
    (root / "SPEC.md").write_text("# Spec\n")
    (root / "AGENT_CONTEXT.md").write_text("# Agent Context\n")
    (root / "TASKS.md").write_text(SAMPLE_TASKS_MD)

    # Create directories
    tasks_dir = root / "tasks"
    tasks_dir.mkdir()
    (tasks_dir / "_TEMPLATE.md").write_text(SAMPLE_TEMPLATE)

    reviews_dir = root / "reviews"
    reviews_dir.mkdir()

    return root
