# SEO Content Generation

Batch generation of SEO content using ACFS (Agentic Coding Flywheel System).

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ CM PLAYBOOK          │ BD BEADS              │ NTM AGENTS              │
│ Rules agents follow  │ Work items to track   │ Parallel execution      │
├─────────────────────────────────────────────────────────────────────────┤
│ cm context "glossary"│ bd ready --labels=seo │ ntm spawn seo --cc=10   │
│ → Returns rules for  │ → Returns claimable   │ → 10 Claude agents      │
│   article generation │   article tasks       │   ready to work         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Deterministic Workflow (Recommended)

### 1. Setup: Create Beads for Each Article

```bash
cd /data/projects/steward-security

# Create epic for the batch
bd create "SEO Glossary Batch 1" --type=epic --label=seo

# Create task beads as CHILDREN of epic (use --parent, not --deps)
bd create "Generate glossary: SQL Injection" \
  --parent=<epic-id> \
  --label=seo --label=glossary \
  -d "slug: sql-injection, category: attack"

# Verify swarm structure
bd swarm validate <epic-id>

# Create swarm for orchestration
bd swarm create <epic-id>
```

**Important:** Use `--parent=epic-id` to make beads children of the epic.
Using `--deps="epic:id"` creates the wrong relationship and swarm won't track them.

### 2. Agent Workflow (What Each Agent Does)

```bash
# 1. Get procedural rules
cm context "generate glossary article" --json

# 2. Find ready work
bd ready --labels=seo,glossary --unassigned --json

# 3. Claim work ATOMICALLY (prevents race conditions)
bd update <bead-id> --claim
# If fails (already claimed), pick different bead and retry

# 4. Execute (read prompts, WebSearch, write article)
# ... agent does the work ...

# 5. Complete
bd close <bead-id> --reason="Article generated: seo/output/glossary/slug.md"
```

### 3. Monitor Progress

```bash
# Swarm status (computed from beads)
bd swarm status <epic-id> --json

# Example output:
# {
#   "total_issues": 10,
#   "completed": ["ztb", "dsi"],
#   "active": ["o3d"],
#   "ready": ["4v6", "nl6", ...],
#   "blocked": [],
#   "progress_percent": 20
# }
```

## Current Test Swarm

```
Epic: cybersecurity-consultancy-mu8 (SEO Glossary Generation Test Batch)
Swarm: cybersecurity-consultancy-p1s
Tasks: 10 glossary articles (all ready, wave 0)
```

## Quick Start (Multi-Agent)

```bash
cd /data/projects/steward-security

# 1. Spawn session with multiple agents (max 20 per session)
cd /data/projects && ntm spawn steward-security --cc=5

# 2. Wait for agents to initialize (important!)
sleep 15

# 3. Send prompt to ALL Claude agents (use --cc="" with empty string)
echo "Start the SEO workflow. Follow PRIME.md instructions.
Run: bd ready --label=seo --label=glossary
Claim ONE bead, generate the article, close bead, loop.
Each agent claim different beads. Do not wait for input." | ntm send steward-security --cc=""

# 4. Monitor progress
python3 seo/scripts/monitor.py --watch --interval 60

# 5. Check completion
bd swarm status <epic-id>
```

**Important:** Use `--cc=""` (with empty quotes) to broadcast to all Claude agents.
Do NOT use `--pane=X` for individual targeting - agents may not execute.

## Scaling to 5000 Articles

### Strategy: Multiple Sessions + Multiple Agents

```bash
# 5 sessions × 20 agents = 100 parallel workers
# 5000 articles ÷ 100 agents = 50 articles per agent

# Spawn sessions
for i in {1..5}; do
  ntm spawn seo-$i --cc=20 --no-user
done

# Distribute batches (50 items each)
# Use a script to send batch to each agent pane
./seo/scripts/distribute-batches.sh

# Wait for all
for i in {1..5}; do
  ntm wait seo-$i --until=idle --timeout=3h
done
```

### Batch Distribution Script

```bash
#!/bin/bash
# seo/scripts/distribute-batches.sh

TERMS_FILE="seo/data/glossary-vars.json"
BATCH_SIZE=50
PANE=2  # Start at pane 2 (pane 1 is user)

# Extract terms and send batches to agents
jq -c '.terms[]' "$TERMS_FILE" | split -l $BATCH_SIZE - /tmp/batch_

for batch in /tmp/batch_*; do
  SESSION="seo-$((PANE / 20 + 1))"
  PANE_NUM=$((PANE % 20 + 2))

  TERMS=$(cat "$batch" | jq -r '"\(.term) - slug: \(.slug) - category: \(.category)"' | tr '\n' '\n')

  ntm send "$SESSION" --pane=$PANE_NUM "Generate these glossary articles:
$TERMS

Read: seo/prompts/glossary-prompt.md and seo/context/brand-voice.md
For each: WebSearch, write 400-600 words, save to seo/output/glossary/{slug}.md
Do sequentially. Say COMPLETE when done."

  PANE=$((PANE + 1))
done
```

## Directory Structure

```
seo/
├── context/
│   └── brand-voice.md        # Wexley Labs tone/style
├── prompts/
│   ├── glossary-prompt.md    # Article format
│   ├── location-prompt.md
│   └── industry-prompt.md
├── data/
│   ├── glossary-vars.json    # All terms
│   └── glossary.json         # Original data
├── output/                   # Generated articles
│   ├── glossary/
│   └── ...
└── scripts/
    └── distribute-batches.sh
```

## Tool Reference

| Tool | Purpose | Key Commands |
|------|---------|--------------|
| **ntm** | Session/agent management | `spawn`, `send`, `status`, `wait`, `kill` |
| **bd** | Issue tracking (Go, has daemon) | `init`, `create`, `ready`, `swarm`, `close` |
| **cm** | Procedural memory/rules | `context`, `playbook add`, `playbook list` |
| **bv** | Beads viewer/analyzer | Dependency graphs, insights |

### CM Playbook (Current Rules)

```bash
# View current rules
cm playbook list

# Current SEO rule (b-mkmvy34r-43eg83):
# SEO-GLOSSARY: When generating cybersecurity glossary articles:
# 1) Read seo/prompts/glossary-prompt.md for format
# 2) Read seo/context/brand-voice.md for tone
# 3) Use WebSearch for current examples (2023-2024 breaches)
# 4) British English only (organisation, defence, colour)
# 5) 400-600 words
# 6) Save to seo/output/glossary/{slug}.md
# 7) Avoid AI patterns
```

## Agent Monitoring

ntm provides comprehensive monitoring via robot commands:

```bash
# Overall status (sessions, agents, beads)
ntm --robot-status --json

# Agent activity (idle/busy/error)
ntm --robot-activity=session-name

# Health check per agent
ntm --robot-health=session-name

# Alerts (stuck agents, crashes, rate limits)
ntm --robot-alerts --json
ntm --robot-alerts --alerts-severity=critical

# Inspect specific pane output
ntm --robot-inspect-pane=session --inspect-index=2 --inspect-lines=200

# Wait for completion with stuck detection
ntm --robot-wait=session --wait-until=idle --wait-exit-on-error --wait-timeout=2h
```

### bd Daemon (required for full monitoring)

```bash
# Ensure bd is available (not just br)
ln -s ~/.local/bin/bd.old ~/.local/bin/bd  # if needed

# Initialize in project
cd /data/projects/steward-security && bd init steward

# Start daemon
ntm beads daemon start

# Check daemon health
ntm beads daemon health
bd daemon --health
```

## Commands

```bash
# Spawn (run from /data/projects, session name = project dir name)
cd /data/projects && ntm spawn steward-security --cc=N  # N Claude agents (max 20)
ntm spawn name --cc=20 --no-user  # Headless (no user pane)

# Send to ALL Claude agents (MUST use --cc="" with empty quotes)
echo "your prompt" | ntm send name --cc=""  # Broadcast to all Claude agents
ntm send name --cc="" --file=prompt.txt     # From file

# Send to specific pane (NOT recommended - may not execute)
ntm send name --pane=2 "prompt"   # Send to pane 2 only

# Monitor (basic)
ntm status name
ntm wait name --until=idle --timeout=2h

# Monitor (advanced - JSON for scripts)
ntm --robot-status --json
ntm --robot-activity=name --json
ntm --robot-health=name --json

# Interrupt stuck agent
ntm --robot-interrupt=name --panes=4 --interrupt-msg="Please continue with remaining articles"

# Cleanup
ntm kill name
```

## System Resources

Testing showed:
- ~400MB RAM per Claude agent
- 16 cores can handle 15 agents at full load (load average 16.90)
- 62GB total RAM available
- **Recommended**: 10-15 agents per session for stability

## Verified Working

Tested with 3 articles (single agent):
- `sql-injection.md` - 4.3KB, proper format
- `xss.md` - 3.7KB, proper format
- `phishing.md` - 4.3KB, proper format

Tested with 10 articles (5 parallel agents × 2 each):
- 8/10 articles generated (80% success rate)
- 1 agent got stuck (pane 4) - use `--robot-inspect-pane` to diagnose
- All generated articles had correct format, British English, current examples

## Troubleshooting

### Stuck Agent Detection

```bash
# Check which agents are stuck
ntm --robot-activity=session-name --json | jq '.agents[] | select(.state != "idle")'

# Inspect stuck agent output
ntm --robot-inspect-pane=session --inspect-index=4 --inspect-lines=200

# Interrupt and retry
ntm --robot-interrupt=session --panes=4 --interrupt-msg="Continue with remaining articles"
```

### bd Database Issues

If `ntm --robot-status` shows `beads.available: false`:
```bash
# Check database health
cd /data/projects/steward-security && bd doctor

# If schema is incompatible, recreate from JSONL
rm .beads/beads.db && bd init steward
```
