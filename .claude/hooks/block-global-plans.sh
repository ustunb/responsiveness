#!/bin/bash
#
# Hook: Block writes to global ~/.claude/plans/ directory
# Enforces project-local plan storage with meaningful names
#

# Get the file path from the tool input (passed as JSON via stdin)
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Check if targeting global plans directory (not project-local)
if [[ "$FILE_PATH" == *"/.claude/plans/"* ]] && [[ "$FILE_PATH" != "$CLAUDE_PROJECT_DIR/.claude/plans/"* ]]; then
  cat >&2 << 'EOF'
BLOCKED: Do not write plans to global ~/.claude/plans/ directory.

Write to the project-local directory instead:
  .claude/plans/next/<meaningful-name>.md

Use a descriptive name like:
  - separability-refactor.md
  - add-parallelization.md
  - fix-cplex-backend.md

NOT random names like 'tranquil-questing-hennessy.md'
EOF
  # Exit code 2 blocks the tool call and shows stderr to Claude
  exit 2
fi

exit 0
