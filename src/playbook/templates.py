"""Embedded markdown templates for playbook init.

Each value is the exact content of a file from the project-playbook
template repository. The TEMPLATES dict maps relative file paths
(from the project root) to their string content.
"""

TEMPLATES: dict[str, str] = {}

# ---------- README.md ----------
TEMPLATES["README.md"] = """\
# Project Playbook

A template repository for planning, specifying, and executing software projects using a human-architect + AI-agent workflow.

## How to Use

1. **Create a new repo from this template** on GitHub (Use as template) or clone and reinitialize
2. **Fill out SPEC.md** \u2014 architecture, data models, API contracts, file tree
3. **Break work into tasks** \u2014 create numbered task files in `tasks/`
4. **Execute** \u2014 relay tasks to Claude Code one at a time
5. **Review** \u2014 verify output, log in `reviews/`, advance to next task

## Repo Structure

```
\u251c\u2500\u2500 PLAYBOOK.md            # The process \u2014 phases, decision gates, workflows
\u251c\u2500\u2500 SPEC.md                # Project-specific architecture & design
\u251c\u2500\u2500 TASKS.md               # Ordered task queue with status
\u251c\u2500\u2500 AGENT_CONTEXT.md       # Agent constraints, conventions, permissions
\u251c\u2500\u2500 tasks/
\u2502   \u251c\u2500\u2500 _TEMPLATE.md       # Copy this for each new task
\u2502   \u2514\u2500\u2500 001-example.md     # Individual task specs
\u2514\u2500\u2500 reviews/
    \u2514\u2500\u2500 001-example.md     # Post-task review notes
```

## Key Principles

- **Planning is the product.** The spec is written before any code. The agent executes, it doesn\u2019t design.
- **Strict spec, flagged concerns.** The agent follows the spec exactly but reports conflicts or ambiguities.
- **Verify before advancing.** Every task goes through a review gate before the next one starts.
- **Context lives in files.** The agent reads the spec from disk \u2014 no token-heavy prompt stuffing.

## Requirements

- Claude Code installed on the execution host
- GitHub CLI (`gh`) authenticated
- SSH/tmux access or relay script for agent dispatch
"""

# ---------- PLAYBOOK.md ----------
TEMPLATES["PLAYBOOK.md"] = """\
# Playbook \u2014 Project Execution Process

## Decision Gate: Should This Project Use the Playbook?

Use this process when **all three** are true:

1. **Multi-file deliverable** \u2014 more than 2-3 files being created or modified
2. **Architectural decisions required** \u2014 tech stack, data models, API design, or file structure choices
3. **Takes more than one agent session** \u2014 can\u2019t be completed in a single relay/prompt

**Skip this process and work directly** when:

- Quick config change, single script, or one-file fix
- The task is well-understood and needs no design phase
- Debugging or troubleshooting (interactive back-and-forth is better)
- Infrastructure/ops work that\u2019s mostly commands, not code architecture

When in doubt: if you can describe the entire task in 3 sentences and there\u2019s only one reasonable way to do it, skip the playbook.

---

## Phase 1: Architecture (Human + AI Advisor)

**Goal:** Lock down every design decision before writing code.

**Outputs:** Completed SPEC.md with:

- [ ] Problem statement \u2014 what this solves, who it\u2019s for
- [ ] Tech stack \u2014 language, framework, database, deployment target
- [ ] File tree \u2014 every file and directory, named and placed
- [ ] Data models \u2014 every table/schema/type with fields and relationships
- [ ] API contracts \u2014 every endpoint/interface with request/response shapes
- [ ] External dependencies \u2014 third-party services, APIs, packages with versions
- [ ] Environment \u2014 env vars, secrets, ports, config files
- [ ] Constraints \u2014 what the agent can\u2019t do (permissions, network, etc.)

**Rules:**

- No code is written in this phase
- Challenge every assumption (\u201cdo we actually need a database here?\u201d)
- Name things now, not later \u2014 file names, function names, route paths
- If two approaches are viable, pick one and document why

---

## Phase 2: Task Breakdown (Human + AI Advisor)

**Goal:** Decompose the spec into ordered, independently-executable tasks.

**Outputs:** Completed TASKS.md and individual task files in `tasks/`

**Task sizing rules:**

- Each task should be completable in **one agent session** (10-20 file operations max)
- Each task has a **clear input state** (what exists before) and **output state** (what exists after)
- Tasks are ordered by dependency \u2014 no task references code that hasn\u2019t been written yet
- First task is always **scaffold** \u2014 create the file structure, install dependencies, write config files, no business logic

**Task writing rules:**

- Copy `tasks/_TEMPLATE.md` for each task
- Include acceptance criteria that can be verified programmatically when possible
- Include the exact files the agent will create or modify
- Reference SPEC.md sections, don\u2019t repeat them (\u201cSee SPEC.md Data Models\u201d)

---

## Phase 3: Execute (AI Agent \u2014 Claude Code)

**Goal:** Complete one task at a time via relay.

**Relay prompt structure:**

```
Read /path/to/project/AGENT_CONTEXT.md for your constraints.
Read /path/to/project/SPEC.md for the full project spec.
Read /path/to/project/tasks/NNN-task-name.md for your current task.

Execute the task as specified. Follow the spec exactly.

If you encounter a conflict, ambiguity, or something that seems wrong:
1. Document the concern at the top of your output
2. Complete the task as spec\u2019d anyway
3. Do not improvise alternatives unless the spec is impossible to follow

When done, list every file you created or modified.
```

**Execution rules:**

- One task per relay \u2014 never batch
- Agent reads context from files, not from the prompt
- Agent commits its own work (commit message: \u201ctask NNN: short description\u201d)
- If a task fails or times out, do not re-relay blindly \u2014 go to Phase 4 first

---

## Phase 4: Verify (Human + AI Advisor)

**Goal:** Confirm the task was completed correctly before advancing.

### Verification Methods by Task Type

| Task Type | Primary Check | Secondary Check |
|---|---|---|
| **Scaffold / setup** | File tree matches spec | Dependencies install clean |
| **Data models / DB** | Schema matches spec | Migrations run without error |
| **API endpoints** | Routes exist, return expected shapes | curl/httpie smoke test |
| **Business logic** | Tests pass | Manual review of edge cases |
| **Frontend / UI** | Renders without errors | Visual spot-check |
| **Config / infra** | Service starts | Logs show no errors |
| **Integration** | End-to-end flow works | Error paths handled |

### Verification workflow:

1. **Read the agent\u2019s output** \u2014 check for flagged concerns at the top
2. **Run the primary check** for the task type
3. **Run the secondary check** if primary passes
4. **Log the result** in `reviews/NNN-task-name.md`
5. **If passed:** Update TASKS.md status, advance to next task
6. **If failed:** Go to Failure Protocol

---

## Failure Protocol

When a task produces incorrect output:

### Severity 1 \u2014 Minor issues (naming, formatting, small logic error)

1. Document the issue in `reviews/NNN-task-name.md`
2. Create a fix task (e.g., `tasks/NNN-fix.md`) with the specific correction
3. Relay the fix task \u2014 include the error description and expected fix

### Severity 2 \u2014 Significant deviation from spec

1. Document what went wrong and why in `reviews/NNN-task-name.md`
2. Check if the spec was ambiguous \u2014 if so, fix SPEC.md first
3. Re-relay the original task with additional clarification appended
4. If it fails twice: flag for human intervention (do it manually or redesign the task)

### Severity 3 \u2014 Architectural problem surfaces

1. **Stop execution.** Do not relay more tasks.
2. Return to Phase 1 \u2014 the spec needs revision
3. Assess impact on completed tasks \u2014 may need to re-do earlier work
4. Update SPEC.md, re-generate affected task files, resume from the affected point

### General retry rules:

- **Max 2 retries per task** \u2014 after that, human intervenes
- **Never retry without new information** \u2014 if the prompt was the same, the result will be the same
- **Append, don\u2019t replace** \u2014 add clarification to the task file, don\u2019t rewrite it (preserve history of what was tried)
"""

# ---------- SPEC.md (blank template) ----------
# NOTE: The project-playbook repo's SPEC.md contains the filled-in CLI spec.
# This is the blank template version that new projects should start with.
TEMPLATES["SPEC.md"] = """\
# Project Specification \u2014 [Project Name]

## Problem Statement

_What problem does this solve? Who is it for?_

## Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Language | | |
| Framework | | |
| Database | | |
| Deployment | | |

## File Tree

```
project/
\u251c\u2500\u2500 README.md
\u2514\u2500\u2500 ...
```

## Data Models

_Tables, schemas, types with fields and relationships._

## API Contracts

_Endpoints, request/response shapes._

## External Dependencies

| Package | Version | Purpose |
|---|---|---|

## Environment

_Env vars, secrets, ports, config files._

## Constraints

_What the agent can\u2019t do \u2014 permissions, network, etc._

## Design Decisions Log

1. **Decision** \u2014 rationale
"""

# ---------- TASKS.md ----------
TEMPLATES["TASKS.md"] = """\
# Task Queue

## Status Key

- `[ ]` \u2014 Not started
- `[>]` \u2014 In progress (relayed to agent)
- `[\u2713]` \u2014 Completed and verified
- `[!]` \u2014 Failed / needs revision
- `[~]` \u2014 Skipped (no longer needed)

## Tasks

| # | Task | Status | Depends On | Notes |
|---|---|---|---|---|
"""

# ---------- AGENT_CONTEXT.md ----------
TEMPLATES["AGENT_CONTEXT.md"] = """\
# Agent Context

> This file is read by Claude Code at the start of every task. Keep it current.

## Identity

You are executing tasks for a software project. You follow the spec exactly and flag concerns without deviating.

## Constraints

- **User:** `claude-agent` (uid 1001, no sudo)
- **Writable paths:** `/home/chris/projects/` and subdirectories
- **No sudo access** \u2014 cannot install system packages, modify systemd, or change permissions outside your scope
- **Docker:** Access via socket proxy at `127.0.0.1:2375` (read + container management, no privileged ops)
- **Network:** Tailscale only for inter-host communication
- **Git:** Commit your work after each task. Message format: `task NNN: short description`

## Conventions

- **Python:** 3.12+, use `venv`, pin dependencies in `requirements.txt`
- **Formatting:** Use the project\u2019s existing style. When starting fresh: 4-space indent, double quotes, type hints
- **Error handling:** Never silently swallow exceptions. Log or raise.
- **Naming:** snake_case for files and functions, PascalCase for classes, UPPER_SNAKE for constants
- **Commits:** One commit per task. Don\u2019t amend previous commits.
- **Tests:** If the task includes writing tests, they must pass before you commit.

## Output Format

At the end of every task, output:

```
## CONCERNS (if any)
- [describe any spec conflicts, ambiguities, or issues]

## FILES MODIFIED
- path/to/file1.py (created)
- path/to/file2.py (modified)

## VERIFICATION
- [describe what you tested/checked]
- [any commands run and their output]

## STATUS
COMPLETE | BLOCKED (reason)
```

## What NOT to Do

- Do not modify files outside the project directory
- Do not install system-level packages
- Do not create Docker containers unless the task explicitly says to
- Do not make network requests to external services unless the task requires it
- Do not refactor code that isn\u2019t part of your current task
- Do not add features, endpoints, or files not in the spec
"""

# ---------- .gitignore ----------
TEMPLATES[".gitignore"] = """\
__pycache__/
*.pyc
.env
venv/
.venv/
*.egg-info/
dist/
build/
.pytest_cache/
node_modules/
"""

# ---------- tasks/_TEMPLATE.md ----------
TEMPLATES["tasks/_TEMPLATE.md"] = """\
# Task NNN: [Title]

## Objective

_One sentence: what this task produces._

## Context

_What already exists before this task runs. Reference prior tasks if relevant._

## Spec Reference

_Point to the relevant sections of SPEC.md_

## Deliverables

_Exact files to create or modify:_

- [ ] `path/to/file.py` \u2014 description of what it contains
- [ ] `path/to/other.py` \u2014 description

## Acceptance Criteria

_How to verify this task is done correctly:_

1. [ ] Criterion 1 (e.g., \u201cServer starts without errors on port 8000\u201d)
2. [ ] Criterion 2 (e.g., \u201cGET /api/health returns 200\u201d)
3. [ ] Criterion 3

## Notes

_Any additional context, edge cases, or warnings._
"""

# ---------- tasks/001-example.md ----------
# NOTE: This file does not exist in the project-playbook repo.
# Created as a representative example matching the template structure.
TEMPLATES["tasks/001-example.md"] = """\
# Task 001: Scaffold

## Objective

Create the initial project structure, install dependencies, and verify the dev environment works.

## Context

Starting from an empty repository. This is the first task.

## Spec Reference

- \u00a7 Tech Stack
- \u00a7 File Tree
- \u00a7 External Dependencies

## Deliverables

- [ ] Project directory structure matching the spec file tree
- [ ] Dependency configuration file with all packages listed
- [ ] Development environment setup (venv, editable install)
- [ ] Verify: tests run (even if no real tests yet)

## Acceptance Criteria

1. [ ] File tree matches the spec
2. [ ] Dependencies install without errors
3. [ ] Test runner executes successfully (zero tests is OK)

## Notes

- This task is purely structural \u2014 no business logic.
- Get the foundation right so subsequent tasks can focus on functionality.
"""

# ---------- reviews/001-example.md ----------
# NOTE: This file does not exist in the project-playbook repo.
# Created as a representative example for the reviews directory.
TEMPLATES["reviews/001-example.md"] = """\
# Review 001: Scaffold

## Status: PASS / FAIL

## Checklist

- [ ] File tree matches spec
- [ ] Dependencies install cleanly
- [ ] Test runner works
- [ ] No extraneous files created

## Issues Found

_None, or describe issues here._

## Notes

_Any observations for future tasks._
"""
