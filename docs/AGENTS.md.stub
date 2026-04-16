# Playbook CLI

CLI tool for the project-playbook workflow — plan tasks, track status, run reviews, and relay context between sessions.

## Key Files
- `src/playbook/cli.py` — Click CLI entry point, registers all subcommands
- `src/playbook/commands/init.py` — `playbook init` — scaffold a new project playbook
- `src/playbook/commands/task.py` — `playbook task` — create/manage task files
- `src/playbook/commands/status.py` — `playbook status` — show project status
- `src/playbook/commands/relay.py` — `playbook relay` — generate context relay for new sessions
- `src/playbook/commands/review.py` — `playbook review-spec` — review spec compliance
- `src/playbook/commands/verify.py` — `playbook verify` — verify task completion
- `src/playbook/commands/check.py` — `playbook check` — run project health checks
- `src/playbook/parser.py` — markdown parser for playbook/task files
- `src/playbook/reviewer.py` — spec review logic
- `src/playbook/templates.py` — template generation for playbook files
- `src/playbook/config.py` — CLI configuration
- `pyproject.toml` — package config, entry point: `playbook = "playbook.cli:cli"`
- `smoke_test.sh` — end-to-end smoke test script

## Installation
- `pip install -e .` (or `pip install -e ".[dev]"` for tests)
- Provides the `playbook` command after install

## Dependencies
- click, rich, httpx (runtime)
- pytest (dev)

## Not a Service
- This is a CLI tool, not a running service. No port, no deployment.
- Installed into venvs or globally on the dev machine.

## Gotchas
- Expects to run inside a project directory with PLAYBOOK.md and tasks/ folder.
- Uses httpx — some commands may call external APIs (context-engine relay).
- Python >=3.12 required.
