#!/bin/bash
# Monitor script for ACFS agent heartbeats
# Usage: ./monitor.sh [--interval=60] [--stale=300] [--once]
#
# Checks .heartbeats/ directory for stale agents and reports status.

set -euo pipefail

# Defaults
INTERVAL=60        # Check every 60 seconds
STALE_THRESHOLD=300  # 5 minutes = stale
ONCE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --interval=*)
            INTERVAL="${arg#*=}"
            ;;
        --stale=*)
            STALE_THRESHOLD="${arg#*=}"
            ;;
        --once)
            ONCE=true
            ;;
        --help)
            echo "Usage: $0 [--interval=60] [--stale=300] [--once]"
            echo "  --interval=N  Check every N seconds (default: 60)"
            echo "  --stale=N     Consider agent stale after N seconds (default: 300)"
            echo "  --once        Run once and exit"
            exit 0
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

check_heartbeats() {
    local now
    now=$(date +%s)

    echo "=== Agent Status @ $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
    echo ""

    if [[ ! -d "$HEARTBEATS_DIR" ]] || [[ -z "$(ls -A "$HEARTBEATS_DIR" 2>/dev/null)" ]]; then
        echo "No heartbeats found in $HEARTBEATS_DIR"
        return
    fi

    local active=0
    local stale=0

    for hb_file in "$HEARTBEATS_DIR"/*.heartbeat; do
        [[ -f "$hb_file" ]] || continue

        local agent session pane ts bead items
        agent=$(jq -r '.agent' "$hb_file" 2>/dev/null || echo "unknown")
        session=$(jq -r '.session' "$hb_file" 2>/dev/null || echo "unknown")
        pane=$(jq -r '.pane' "$hb_file" 2>/dev/null || echo "?")
        ts=$(jq -r '.timestamp' "$hb_file" 2>/dev/null || echo "")
        bead=$(jq -r '.current_bead // "idle"' "$hb_file" 2>/dev/null || echo "idle")
        items=$(jq -r '.items_completed // 0' "$hb_file" 2>/dev/null || echo "0")

        # Calculate age
        local hb_epoch age status
        hb_epoch=$(date -d "$ts" +%s 2>/dev/null || echo "0")
        age=$((now - hb_epoch))

        if [[ $age -gt $STALE_THRESHOLD ]]; then
            status="STALE"
            ((stale++))
        else
            status="ACTIVE"
            ((active++))
        fi

        printf "%-12s %-8s %-20s bead=%-10s items=%-3s age=%ds\n" \
            "[$status]" "$agent" "$session:$pane" "$bead" "$items" "$age"
    done

    echo ""
    echo "Summary: $active active, $stale stale (threshold: ${STALE_THRESHOLD}s)"

    if [[ $stale -gt 0 ]]; then
        echo ""
        echo "WARNING: Stale agents detected. Consider running:"
        echo "  ./scripts/recover-agent.sh <agent-name>"
    fi
}

# Main loop
if $ONCE; then
    check_heartbeats
else
    echo "Monitoring heartbeats every ${INTERVAL}s (stale threshold: ${STALE_THRESHOLD}s)"
    echo "Press Ctrl+C to stop"
    echo ""
    while true; do
        check_heartbeats
        echo ""
        sleep "$INTERVAL"
    done
fi
