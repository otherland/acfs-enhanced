#!/bin/bash
# Generic heartbeat script for ACFS agents
# Usage: ./heartbeat.sh <agent_name> <session> <pane> [current_bead] [items_completed]
#
# Writes a JSON heartbeat file to .heartbeats/ directory.
# Monitor scripts can check these files to detect stuck agents.

set -euo pipefail

AGENT_NAME="${1:-agent}"
SESSION="${2:-unknown}"
PANE="${3:-unknown}"
CURRENT_BEAD="${4:-null}"
ITEMS_COMPLETED="${5:-0}"

# Find project root (look for .beads directory)
find_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.beads" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    echo "$PWD"  # Fallback to current directory
}

PROJECT_ROOT="$(find_project_root)"
HEARTBEATS_DIR="${PROJECT_ROOT}/.heartbeats"
HEARTBEAT_FILE="${HEARTBEATS_DIR}/${AGENT_NAME}.heartbeat"

mkdir -p "$HEARTBEATS_DIR"

# Write heartbeat JSON
cat > "$HEARTBEAT_FILE" << EOF
{
  "agent": "$AGENT_NAME",
  "session": "$SESSION",
  "pane": "$PANE",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "current_bead": $([ "$CURRENT_BEAD" = "null" ] && echo "null" || echo "\"$CURRENT_BEAD\""),
  "items_completed": $ITEMS_COMPLETED,
  "project_root": "$PROJECT_ROOT"
}
EOF

echo "Heartbeat written: $HEARTBEAT_FILE"
