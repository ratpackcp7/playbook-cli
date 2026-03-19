# Playbook CLI

A command-line tool that automates the mechanical parts of the project playbook workflow — creating task files, tracking status, and assembling relay prompts.

## Install

```bash
git clone <repo-url> playbook-cli
cd playbook-cli
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Usage

### Initialize a new project

```bash
playbook init my-project
```

Creates a new directory with the full playbook template: PLAYBOOK.md, SPEC.md, TASKS.md, AGENT_CONTEXT.md, task templates, and a git repo.

Use `--no-git` to skip git initialization.

### Create a new task

```bash
playbook task new "Build the API"
```

Auto-numbers the task, creates the task file from the template, and appends it to TASKS.md.

### Check project status

```bash
playbook status
```

Shows all tasks with color-coded status indicators (TODO, IN PROGRESS, DONE, FAILED, SKIPPED) and a completion summary.

### Assemble a relay prompt

```bash
playbook relay 003
```

Combines AGENT_CONTEXT.md, SPEC.md, and the specified task file into a single prompt, printed to stdout.

```bash
playbook relay 003 --copy
```

Same as above, but copies the prompt to the clipboard via xclip (falls back to stdout if xclip is unavailable).

## Development

Run the test suite:

```bash
pytest
```

Run the smoke test (end-to-end CLI workflow):

```bash
bash smoke_test.sh
```

## How It Works

Playbook CLI automates the [project playbook workflow](https://github.com/ratpackcp7/project-playbook). You write the spec and review the work; the CLI handles file creation, numbering, status tracking, and prompt assembly.

Each initialized project contains a PLAYBOOK.md that describes the full workflow in detail.

This is a CLI tool — no ports, no database, no config files. All state lives in markdown files within your project directory.
