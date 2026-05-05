# CLAUDE.md — Playbook CLI

CLI tool that automates the project playbook workflow — creating task files, tracking status, assembling relay prompts for multi-session AI agent work.

## Before You Start
- Read `AGENTS.md` for full file inventory and architecture
- Read `SPEC.md` for detailed design decisions and command specs

## Key Facts
- **Python** 3.12+ project (not a service — CLI tool, no port)
- **Framework**: Click 8.x + Rich
- **Entry point**: `playbook = "playbook.cli:cli"` (from pyproject.toml)
- **Install**: `pip install -e .` (or `pip install -e ".[dev]"` for tests)
- **Tests**: `pytest tests/ -v`
- **Smoke test**: `bash smoke_test.sh`

## Install / Run

```bash
cd ~/projects/playbook-cli
pip install -e .
# Now available as `playbook` command
```

## Available Commands

| Command | Purpose |
|---------|---------|
| `playbook init <name>` | Scaffold a new project playbook |
| `playbook task new "<title>"` | Create a new task file |
| `playbook status` | Show project status (task counts, completion) |
| `playbook relay <NNN>` | Generate context relay for new sessions |
| `playbook review-spec` | Review spec compliance |
| `playbook verify` | Verify task completion |
| `playbook check` | Run project health checks |

## How it works

- Expects to run inside a project directory with `PLAYBOOK.md` and `tasks/` folder
- All state lives in markdown files (no database)
- `parser.py` reads `TASKS.md` and task files
- `templates.py` generates markdown templates
- Some commands call external APIs via httpx (e.g., context-engine relay)

## Dependencies

- **Runtime**: click, rich, httpx
- **Dev**: pytest

## Rules
- One commit per task
- Tests must pass before committing
- Do not add a database — all state stays in markdown

## Active Work

See `HANDOFF.md` for current work status and next steps.

<!-- CP7-AGENT-STANDARDS:START -->

## CP7 Agent Standard

Before behavior changes, read `/home/chris/cp7-bridge/docs/agent-standards/AGENT-OPERATING-STANDARD.md`, this project's README/HANDOFF, and `docs/decisions/`.

Create or update an ADR for changes to ports, bind addresses, tunnels, Docker Compose, volumes, healthchecks, systemd, timers, persistent data paths, MCP tools, auth, allowlists, writable roots, or unusual config.

Every change report must include what changed, why, verification, rollback, and touched files/services.

Verifier:

```bash
/home/chris/cp7-bridge/scripts/verify_agent_standards.sh
```

<!-- CP7-AGENT-STANDARDS:END -->
