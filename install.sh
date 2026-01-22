#!/bin/bash
# ACFS Enhanced Installation Script
# Installs templates and scripts for long-running agent workflows

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-.}"

echo "ACFS Enhanced Installer"
echo "======================="
echo ""

# Check prerequisites
check_prereqs() {
    local missing=()

    command -v bd &>/dev/null || missing+=("bd")
    command -v ntm &>/dev/null || missing+=("ntm")
    command -v claude &>/dev/null || command -v cc &>/dev/null || missing+=("claude/cc")

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Missing prerequisites: ${missing[*]}"
        echo ""
        echo "Install base ACFS tools from: https://agent-flywheel.com/learn/welcome"
        exit 1
    fi

    echo "✓ Prerequisites found: bd, ntm, claude"
}

# Initialize project structure
init_project() {
    local target="$1"

    echo ""
    echo "Initializing project in: $target"

    # Create directories
    mkdir -p "$target/.beads"
    mkdir -p "$target/.claude"
    mkdir -p "$target/.heartbeats"
    mkdir -p "$target/scripts"

    # Copy templates
    if [[ -f "$SCRIPT_DIR/templates/.beads/PRIME.md.template" ]]; then
        cp "$SCRIPT_DIR/templates/.beads/PRIME.md.template" "$target/.beads/PRIME.md"
        echo "  ✓ Created .beads/PRIME.md (customize this!)"
    fi

    if [[ -f "$SCRIPT_DIR/templates/.beads/config.yaml" ]]; then
        cp "$SCRIPT_DIR/templates/.beads/config.yaml" "$target/.beads/config.yaml"
        echo "  ✓ Created .beads/config.yaml"
    fi

    if [[ -f "$SCRIPT_DIR/templates/.claude/settings.local.json" ]]; then
        cp "$SCRIPT_DIR/templates/.claude/settings.local.json" "$target/.claude/settings.local.json"
        echo "  ✓ Created .claude/settings.local.json (hooks configured)"
    fi

    # Copy scripts
    for script in heartbeat.sh monitor.sh recover-agent.sh; do
        if [[ -f "$SCRIPT_DIR/scripts/$script" ]]; then
            cp "$SCRIPT_DIR/scripts/$script" "$target/scripts/"
            chmod +x "$target/scripts/$script"
            echo "  ✓ Copied scripts/$script"
        fi
    done

    # Create .gitignore entries
    if [[ -f "$target/.gitignore" ]]; then
        if ! grep -q '.heartbeats/' "$target/.gitignore" 2>/dev/null; then
            echo '.heartbeats/*.heartbeat' >> "$target/.gitignore"
            echo "  ✓ Added .heartbeats to .gitignore"
        fi
    else
        echo '.heartbeats/*.heartbeat' > "$target/.gitignore"
        echo "  ✓ Created .gitignore"
    fi

    # Initialize beads if not already done
    if [[ ! -f "$target/.beads/issues.jsonl" ]]; then
        local project_name
        project_name=$(basename "$target")
        (cd "$target" && bd init "$project_name" 2>/dev/null) || true
        echo "  ✓ Initialized beads tracker"
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo "Installation complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Edit .beads/PRIME.md to define your workflow"
    echo "  2. Create work items: bd create \"Task description\" --label=your-label"
    echo "  3. Spawn agents: ntm spawn $(basename "$TARGET_DIR") --cc=5"
    echo "  4. Start work: echo 'Follow PRIME.md' | ntm send $(basename "$TARGET_DIR") --cc=\"\""
    echo "  5. Monitor: ./scripts/monitor.sh --interval=60"
    echo ""
    echo "Documentation: $SCRIPT_DIR/docs/quick-start.md"
}

# Main
main() {
    check_prereqs

    # Resolve target directory
    if [[ "$TARGET_DIR" == "." ]]; then
        TARGET_DIR="$(pwd)"
    else
        TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
            mkdir -p "$TARGET_DIR"
            TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"
        }
    fi

    init_project "$TARGET_DIR"
    show_next_steps
}

main "$@"
