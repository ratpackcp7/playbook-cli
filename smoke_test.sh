#!/usr/bin/env bash
set -euo pipefail

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "=== Playbook CLI Smoke Test ==="
echo ""

# 1. Init a project
echo "STEP 1: playbook init smoke-test-project"
cd "$TMPDIR"
playbook init smoke-test-project

# 2. Verify project structure
echo "STEP 2: Verify project directory and files exist"
test -d smoke-test-project
test -f smoke-test-project/PLAYBOOK.md
test -f smoke-test-project/SPEC.md
test -f smoke-test-project/TASKS.md
test -f smoke-test-project/AGENT_CONTEXT.md
echo "  OK: All expected files exist"

# 3. cd into project
cd smoke-test-project

# 4. Verify the example task file exists
echo "STEP 3: Verify tasks/001-example.md exists"
test -f tasks/001-example.md
echo "  OK: 001-example.md exists"

# 5. Run status
echo "STEP 4: playbook status"
STATUS_OUT=$(playbook status)
echo "$STATUS_OUT"

# 6. Verify status output contains "tasks complete"
echo "STEP 5: Verify status contains 'tasks complete'"
echo "$STATUS_OUT" | grep -q "tasks complete"
echo "  OK: Found 'tasks complete'"

# 7. Create a new task
echo "STEP 6: playbook task new 'Build the database'"
playbook task new "Build the database"

# 8. Verify task file exists (002 because 001-example.md already exists)
echo "STEP 7: Verify tasks/002-build-the-database.md exists"
test -f tasks/002-build-the-database.md
echo "  OK: Task file exists"

# 9. Run status again
echo "STEP 8: playbook status (after new task)"
STATUS_OUT2=$(playbook status)
echo "$STATUS_OUT2"

# 10. Verify updated status
echo "STEP 9: Verify status contains 'Build the database'"
echo "$STATUS_OUT2" | grep -q "Build the database"
echo "  OK: Found 'Build the database'"
echo "$STATUS_OUT2" | grep -q "0/1 tasks complete"
echo "  OK: Found '0/1 tasks complete'"

# 11. Relay task 001
echo "STEP 10: playbook relay 001"
RELAY_OUT=$(playbook relay 001 2>/dev/null)

# 12. Verify relay output
echo "STEP 11: Verify relay 001 output"
echo "$RELAY_OUT" | grep -q "=== AGENT CONTEXT ==="
echo "  OK: Found '=== AGENT CONTEXT ==='"
echo "$RELAY_OUT" | grep -q "=== PROJECT SPEC ==="
echo "  OK: Found '=== PROJECT SPEC ==='"
echo "$RELAY_OUT" | grep -q "=== CURRENT TASK ==="
echo "  OK: Found '=== CURRENT TASK ==='"

# 13. Relay task 002
echo "STEP 12: playbook relay 002"
RELAY_OUT2=$(playbook relay 002 2>/dev/null)

# 14. Verify relay 002 contains task title
echo "STEP 13: Verify relay 002 contains 'Build the database'"
echo "$RELAY_OUT2" | grep -q "Build the database"
echo "  OK: Found 'Build the database'"

# 15. Relay non-existent task (expect failure)
echo "STEP 14: playbook relay 999 (expect failure)"
if playbook relay 999 2>/dev/null; then
    echo "  FAIL: Expected non-zero exit code"
    exit 1
else
    echo "  OK: Got expected non-zero exit code"
fi

echo ""
echo "SMOKE TEST PASSED"
