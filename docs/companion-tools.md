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

### mcp_agent_mail (am)

Agent coordination platform - "Gmail for your coding agents."

**Why it matters**: Our heartbeat system tracks liveness, but agents can't communicate. `agent_mail` adds messaging, file reservations, and conflict prevention for true multi-agent coordination.

**Key features**:
- Memorable agent identities (e.g., "GreenCastle", "BlueLake")
- Thread-based messaging with acknowledgment tracking
- Advisory file reservations prevent edit conflicts
- SQLite FTS5 search across all messages
- Git-backed artifacts for audit trails

**Installation**:
```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail/main/scripts/install.sh" | bash -s -- --yes

# Launch server
am
```

**Integration with ACFS workflows**:
```python
# In PRIME.md, agents can coordinate:

# 1. Start session with file reservations
macro_start_session(
  human_key="/path/to/project",
  program="Claude Code",
  file_reservation_paths=["src/api/**"],
  file_reservation_ttl_seconds=3600
)

# 2. Notify other agents when done with a file
send_message(
  project_key="/path/to/project",
  sender_name="Agent1",
  to=["Agent2", "Agent3"],
  subject="API module complete",
  body_md="## Done\n- `/src/api/users.py` ready for integration",
  thread_id="FEAT-123"
)

# 3. Check for blocking messages before claiming work
fetch_inbox(
  project_key="/path/to/project",
  agent_name="Agent2",
  urgent_only=True
)
```

**Use case**: When agents need to coordinate on shared files or pass work between each other. Replaces simple "claim and close" with richer collaboration.

---

### flywheel_connectors (FCP)

Mesh-native protocol for secure, distributed AI assistant operations.

**Why it matters**: Run agent swarms across multiple machines with cryptographic security, capability-based access control, and automatic secret management.

**Key features**:
- **Zone-based isolation**: Cryptographic namespaces (owner, private, work, community, public)
- **Threshold cryptography**: Shamir secret sharing - no single device holds complete secrets
- **Capability-based access**: Signed tokens with explicit authority chains
- **Secretless connectors**: Egress proxy injects credentials, binaries never see raw API keys
- **Tamper-evident audit**: Hash-linked chains with quorum-signed checkpoints

**Architecture**:
```
┌─────────────────────────────────────────────────────────────────┐
│                     TAILSCALE MESH                              │
│                                                                 │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐               │
│   │ Device 1 │ ←→  │ Device 2 │ ←→  │ Device 3 │               │
│   │ MeshNode │     │ MeshNode │     │ MeshNode │               │
│   └────┬─────┘     └────┬─────┘     └────┬─────┘               │
│        │                │                │                      │
│   ┌────┴────┐      ┌────┴────┐      ┌────┴────┐                │
│   │Connector│      │Connector│      │Connector│                │
│   │ Twitter │      │ Linear  │      │ Stripe  │                │
│   └─────────┘      └─────────┘      └─────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

**Performance targets**:
- Local invocation: <2ms p50
- Tailnet operations: <20ms p50 direct
- Memory overhead: <10MB per connector

**When to use**:
- Multi-machine agent deployments
- Sensitive operations requiring secret isolation
- Enterprise environments with audit requirements
- Distributed teams sharing agent infrastructure

**Integration with ACFS**:
```bash
# Instead of single-machine ntm spawn:
fcp spawn --mesh="team-mesh" --connectors="twitter,linear" --agents=5

# Agents claim work across the mesh
fcp agent claim --zone=work --capability="write:content"
```

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

---

## Integration Checklist

For a production multi-agent setup, consider:

**Core (Required)**:
- [ ] Base ACFS tools (bd, ntm, dcg, cass)
- [ ] acfs-enhanced (PRIME, heartbeats, atomic claiming)

**Reliability & Monitoring**:
- [ ] process_triage (smart stuck detection)
- [ ] coding_agent_usage_tracker (cost monitoring)
- [ ] rano (network debugging) - as needed

**Agent Coordination**:
- [ ] mcp_agent_mail (agent messaging & file reservations)

**Distributed/Enterprise**:
- [ ] flywheel_connectors (multi-machine mesh, secret isolation)

**Workflow Sharing**:
- [ ] meta_skill (package and share workflows)
