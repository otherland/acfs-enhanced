# Quick Start Guide

Get a long-running, multi-agent workflow up in 10 minutes.

## Prerequisites

You need the base ACFS tools installed:
- `bd` - Beads issue tracker
- `ntm` - Named Tmux Manager
- `cc` / `claude` - Claude Code CLI
- `dcg` - Destructive Command Guard (optional but recommended)

Install from: https://agent-flywheel.com/learn/welcome

## 1. Initialize Your Project

```bash
cd your-project

# Initialize beads (issue tracking)
bd init your-project

# Create .heartbeats directory for agent monitoring
mkdir -p .heartbeats
echo '.heartbeats/*.heartbeat' >> .gitignore
```

## 2. Create Your PRIME.md

The PRIME.md file is auto-injected into agent sessions on start and before compaction.
This keeps agents on-task even in long sessions.

```bash
# Copy the template
cp /path/to/acfs-enhanced/templates/.beads/PRIME.md.template .beads/PRIME.md

# Edit to match your workflow
# Key sections to customize:
# - YOUR MISSION
# - WORKFLOW steps
# - KEY RULES
# - OUTPUT FORMAT
```

## 3. Configure Hook Injection

Create `.claude/settings.local.json` in your project:

```json
{
  "hooks": {
    "PreCompact": [
      {
        "hooks": [{ "command": "bd prime", "type": "command" }],
        "matcher": ""
      }
    ],
    "SessionStart": [
      {
        "hooks": [{ "command": "bd prime", "type": "command" }],
        "matcher": ""
      }
    ]
  }
}
```

This runs `bd prime` which outputs your PRIME.md content for the agent to see.

## 4. Create Work Items (Beads)

```bash
# Create an epic to track the batch
bd create "My Content Batch" --type=epic --label=content

# Create individual work items as children
bd create "Generate article: Topic 1" \
  --parent=<epic-id> \
  --label=content \
  -d "slug: topic-1, type: blog"

bd create "Generate article: Topic 2" \
  --parent=<epic-id> \
  --label=content \
  -d "slug: topic-2, type: blog"

# Verify structure
bd swarm validate <epic-id>
```

## 5. Spawn Agents

```bash
# Navigate to projects directory
cd /data/projects

# Spawn session with 5 Claude agents
ntm spawn your-project --cc=5

# Wait for agents to initialize
sleep 15
```

## 6. Start the Work

```bash
# Broadcast to all Claude agents
echo "Start the workflow. Follow PRIME.md instructions.
Run: bd ready --label=content
Claim ONE bead, do the work, close bead, loop.
Each agent claim different beads. Do not wait for input." | ntm send your-project --cc=""
```

## 7. Monitor Progress

```bash
# Watch agent status
./scripts/monitor.sh --interval=60

# Or use ntm directly
ntm --robot-status --json

# Check bead completion
bd swarm status <epic-id>
```

## 8. Handle Stuck Agents

```bash
# Check for stale heartbeats
./scripts/monitor.sh --once

# Recover stuck agent
./scripts/recover-agent.sh agent-name --restart
```

## Directory Structure

After setup, your project should look like:

```
your-project/
├── .beads/
│   ├── config.yaml
│   ├── PRIME.md          # Your workflow instructions
│   └── issues.jsonl      # Work items (auto-managed)
├── .claude/
│   └── settings.local.json  # Hook configuration
├── .heartbeats/          # Agent heartbeat files
│   └── .gitignore
├── scripts/              # Copy from acfs-enhanced
│   ├── heartbeat.sh
│   ├── monitor.sh
│   └── recover-agent.sh
└── output/               # Where agents write results
```

## Key Concepts

### PRIME Injection
- Agents lose context in long sessions (compaction)
- PRIME.md is re-injected before compaction
- Keeps agents on-task across multi-hour sessions

### Atomic Claiming
- `bd update <id> --claim` is atomic
- Prevents two agents claiming same work
- If claim fails, agent picks different bead

### Heartbeats
- Agents send heartbeats when claiming/completing work
- Monitor checks for stale heartbeats (>5 min)
- Stuck agents can be auto-recovered

### NTM Robot Mode
- `ntm --robot-*` commands return JSON
- Use for scripted monitoring and automation
- `ntm --robot-status`, `--robot-health`, `--robot-activity`

## Next Steps

- Read [PRIME Templates](prime-templates.md) for advanced customization
- Read [Multi-Agent Patterns](multi-agent-patterns.md) for scaling
- See [Examples](../examples/) for complete workflow implementations
