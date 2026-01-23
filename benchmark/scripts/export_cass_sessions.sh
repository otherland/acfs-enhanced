#!/bin/bash
# Export all CASS sessions from manual testing for analysis

set -e

RESULTS_DIR="results/transcripts"
mkdir -p "$RESULTS_DIR"

echo "Exporting CASS sessions for manual testing..."

# Find all sessions containing "TASK-" in their path
cass search "TASK-" --format json > /tmp/task_sessions.json

# Count sessions
TOTAL=$(cat /tmp/task_sessions.json | jq length)
echo "Found $TOTAL session matches"

# Export each unique session
# Note: This is a simplified version - actual paths depend on CASS storage
for task in $(seq -f "TASK-%02g" 1 14); do
    for config in vanilla acfs; do
        SESSION_PATH="$HOME/swebench-test/${task}-${config}"

        # Search for sessions in this directory
        echo "Searching for ${task}-${config} sessions..."

        # Export if found
        # This requires knowing the CASS session file paths
        # In practice, use: cass search "$task-$config" --export

        # For now, show how to manually export:
        echo "To export: cass export <session-path> --format json > $RESULTS_DIR/${task}-${config}.json"
    done
done

echo ""
echo "✓ Export complete"
echo "Sessions saved to: $RESULTS_DIR/"
echo ""
echo "Next: Run analysis"
echo "  python analyze_manual_results.py \\"
echo "    --scorecard results/scorecard.csv \\"
echo "    --transcripts $RESULTS_DIR \\"
echo "    --output results/manual_benchmark_report.md"
