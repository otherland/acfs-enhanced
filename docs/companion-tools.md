# Companion Tools

Tools from the ACFS ecosystem that enhance multi-agent workflows.

## High Priority

### process_triage (pt)

Bayesian process killer that detects stuck processes smarter than simple timeouts.

**Why it matters**: Our heartbeat system uses fixed 5-minute timeouts. `pt` uses heuristics like CPU usage, memory patterns, and historical data to detect genuinely stuck agents vs temporarily blocked ones.

**Installation**:
```bash
cargo install process_triage
# or
pip install process-triage
```

**Integration with monitor.sh**:
```bash
# Instead of simple heartbeat timeout check:
pt scan --pattern "claude" --stuck-threshold=0.8 --json | jq '.stuck_processes[]'

# Auto-kill with confirmation:
pt triage --pattern "claude" --auto-kill --min-confidence=0.9
```

**Use case**: Replace the simple heartbeat timeout in `monitor.sh` with `pt` for smarter detection.

---

### coding_agent_usage_tracker (caut)

Track API usage and costs across multiple AI providers.

**Why it matters**: Running 5+ agents for hours burns through API credits. `caut` tracks per-session and per-agent costs.

**Installation**:
```bash
pip install coding-agent-usage-tracker
```

**Integration**:
```bash
# Start tracking before spawning agents
caut start --session="seo-batch-$(date +%Y%m%d)"

# After work completes
caut report --session="seo-batch-*" --format=table

# Set budget alerts
caut alert --threshold=50.00 --action="ntm kill-all"
```

**Use case**: Add `caut start` to your spawn script, `caut report` to your completion workflow.

---

## Medium Priority

### wezterm_automata

Terminal hypervisor with pattern detection and automatic workflow triggers.

**Why it matters**: More sophisticated than NTM for complex workflows. Can detect terminal output patterns and trigger actions automatically.

**Key features**:
- Pattern-based triggers (detect errors, completions)
- Automatic recovery actions
- Visual workflow monitoring
- Cross-platform (unlike tmux)

**When to use**: If you need pattern-based automation beyond what NTM provides, or want a GUI-based monitor.

**Note**: Requires WezTerm as your terminal emulator.

---

### meta_skill (ms)

Local-first skill management platform with MCP integration.

**Why it matters**: Share PRIME templates and workflows as installable "skills" across projects and teams.

**Installation**:
```bash
cargo install meta_skill
```

**Publishing a workflow**:
```bash
# Package your PRIME template as a skill
ms init --from=.beads/PRIME.md --name="seo-glossary-workflow"

# Share locally
ms publish --local

# Others can install
ms install seo-glossary-workflow
```

**Use case**: Turn battle-tested PRIME templates into reusable packages.

---

### rano

Network observer for AI CLI processes.

**Why it matters**: Debug rate limiting, track API latency, detect network issues affecting agents.

**Installation**:
```bash
cargo install rano
```

**Usage**:
```bash
# Monitor all Claude API traffic
rano watch --filter="api.anthropic.com" --format=summary

# Detect rate limiting
rano alerts --rate-limit-threshold=5 --notify=slack
```

**Use case**: Debug why agents are slow or failing silently.

---

## Lower Priority

### coding_agent_account_manager (caam)

Sub-100ms account switching for AI subscriptions.

**When needed**: If you have multiple Claude/OpenAI accounts and need to distribute load or switch contexts quickly.

### remote_compilation_helper

Offload compilation to remote machines via SSH.

**When needed**: For build-heavy workflows where local compilation would block agents.

### flywheel_connectors

Mesh-native protocol for secure distributed agent operations.

**When needed**: Multi-machine agent networks with security requirements.

---

## Integration Checklist

For a production multi-agent setup, consider:

- [ ] Base ACFS tools (bd, ntm, dcg, cass)
- [ ] acfs-enhanced (PRIME, heartbeats, atomic claiming)
- [ ] process_triage (smart stuck detection)
- [ ] coding_agent_usage_tracker (cost monitoring)
- [ ] meta_skill (workflow sharing) - optional
- [ ] rano (network debugging) - as needed
