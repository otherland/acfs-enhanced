#!/bin/bash
# Helper functions for CASS during manual testing

# Find sessions for a specific task
find_task_sessions() {
    local task_id="$1"
    echo "Sessions for $task_id:"
    cass search "$task_id" --format table
}

# Export session to markdown
export_session() {
    local session_path="$1"
    local output_file="$2"

    if [ -z "$output_file" ]; then
        output_file="${session_path##*/}.md"
    fi

    cass export "$session_path" --format markdown > "$output_file"
    echo "Exported to: $output_file"
}

# Compare two sessions side by side
compare_sessions() {
    local vanilla_path="$1"
    local acfs_path="$2"

    echo "Exporting sessions..."
    cass export "$vanilla_path" --format markdown > /tmp/vanilla.md
    cass export "$acfs_path" --format markdown > /tmp/acfs.md

    echo "Diff:"
    diff -u /tmp/vanilla.md /tmp/acfs.md | less
}

# Count tool uses in a session
count_tools() {
    local session_path="$1"
    cass export "$session_path" --format json | jq '[.[] | select(.type == "tool_use")] | length'
}

# Search for errors in a session
find_errors() {
    local session_path="$1"
    cass export "$session_path" --format json | jq '.[] | select(.content | tostring | test("error"; "i"))'
}

# Show usage if no args
if [ $# -eq 0 ]; then
    echo "CASS Helper Functions"
    echo ""
    echo "Usage:"
    echo "  source scripts/cass_helpers.sh"
    echo "  find_task_sessions TASK-01"
    echo "  export_session <path> [output.md]"
    echo "  compare_sessions <vanilla-path> <acfs-path>"
    echo "  count_tools <session-path>"
    echo "  find_errors <session-path>"
fi
