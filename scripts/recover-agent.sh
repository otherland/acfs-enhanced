#!/bin/bash
# Recover a stuck ACFS agent
# Usage: ./recover-agent.sh <agent-name> [--restart]
#
# Clears the heartbeat and optionally restarts the agent via NTM.

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <agent-name> [--restart]"
    echo "  --restart  Also restart the agent via NTM"
    exit 1
fi

AGENT_NAME="$1"
RESTART=false

for arg in "$@"; do
    case $arg in
        --restart)
            RESTART=true
            ;;
    esac
done

# Find project root
find_project_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.beads" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    echo "$PWD"
}

PROJECT_ROOT="$(find_project_root)"
HEARTBEATS_DIR="${PROJECT_ROOT}/.heartbeats"
HEARTBEAT_FILE="${HEARTBEATS_DIR}/${AGENT_NAME}.heartbeat"

# Check if heartbeat exists
if [[ ! -f "$HEARTBEAT_FILE" ]]; then
    echo "No heartbeat found for agent: $AGENT_NAME"
    exit 1
fi

# Get session info before clearing
SESSION=$(jq -r '.session' "$HEARTBEAT_FILE" 2>/dev/null || echo "")
PANE=$(jq -r '.pane' "$HEARTBEAT_FILE" 2>/dev/null || echo "")
CURRENT_BEAD=$(jq -r '.current_bead // "null"' "$HEARTBEAT_FILE" 2>/dev/null || echo "null")

echo "Agent: $AGENT_NAME"
echo "Session: $SESSION"
echo "Pane: $PANE"
echo "Current bead: $CURRENT_BEAD"
echo ""

# If agent was working on a bead, unclaim it
if [[ "$CURRENT_BEAD" != "null" && -n "$CURRENT_BEAD" ]]; then
    echo "Unclaiming bead: $CURRENT_BEAD"
    if command -v bd &>/dev/null; then
        bd update "$CURRENT_BEAD" --unclaim 2>/dev/null || echo "  (unclaim failed or not supported)"
    fi
fi

# Clear the heartbeat
echo "Clearing heartbeat file..."
rm -f "$HEARTBEAT_FILE"
echo "  Removed: $HEARTBEAT_FILE"

# Optionally restart via NTM
if $RESTART && [[ -n "$SESSION" ]]; then
    if command -v ntm &>/dev/null; then
        echo ""
        echo "Restarting agent via NTM..."
        # Send interrupt to clear any stuck state
        ntm interrupt "$SESSION" --pane="$PANE" 2>/dev/null || true
        sleep 2
        # Re-inject the PRIME context
        if [[ -f "${PROJECT_ROOT}/.beads/PRIME.md" ]]; then
            echo "Re-injecting PRIME context..."
            PRIME_CONTENT=$(cat "${PROJECT_ROOT}/.beads/PRIME.md")
            ntm send "$SESSION" --pane="$PANE" --msg="$PRIME_CONTENT" 2>/dev/null || true
        fi
        echo "Agent restarted."
    else
        echo "NTM not found - cannot restart automatically"
        echo "Manually restart the agent in session: $SESSION, pane: $PANE"
    fi
fi

echo ""
echo "Recovery complete for: $AGENT_NAME"
