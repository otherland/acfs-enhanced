# ACFS Enhanced

Extensions to [ACFS](https://agent-flywheel.com) for long-running, multi-agent workflows.

## What This Adds

| Feature | Purpose |
|---------|---------|
| **PRIME Templates** | Context that survives session compaction |
| **Heartbeat System** | Monitor agent liveness, detect stuck agents |
| **Atomic Claiming** | Prevent duplicate work in parallel execution |
| **Brand Voice Enforcement** | Consistent output quality across agents |
| **Recovery Scripts** | Auto-recover stuck agents |

## Quick Install

```bash
# Prerequisites: bd, ntm, claude (from agent-flywheel.com)

# Clone this repo
git clone https://github.com/yourorg/acfs-enhanced.git

# Initialize your project
cd your-project
../acfs-enhanced/install.sh .
```

## How It Works

### PRIME Injection

Agents lose context in long sessions (compaction). PRIME.md is auto-injected:
- On session start
- Before compaction

This keeps agents on-task across multi-hour sessions.

```
┌─────────────────────────────────────────────────────────────────┐
│ Session Start          Compaction              Compaction       │
│      ↓                    ↓                       ↓             │
│  [PRIME] → work → work → [PRIME] → work → work → [PRIME] → ... │
└─────────────────────────────────────────────────────────────────┘
```

### Multi-Agent Coordination

```
┌─────────────────────────────────────────────────────────────────┐
│                         BD BEADS                                │
│                    (work item tracker)                          │
│                           │                                     │
│              ┌────────────┼────────────┐                        │
│              ↓            ↓            ↓                        │
│         ┌────────┐   ┌────────┐   ┌────────┐                    │
│         │Agent 1 │   │Agent 2 │   │Agent 3 │                    │
│         │claim   │   │claim   │   │claim   │                    │
│         │work    │   │work    │   │work    │                    │
│         │close   │   │close   │   │close   │                    │
│         └────────┘   └────────┘   └────────┘                    │
│              │            │            │                        │
│              └────────────┼────────────┘                        │
│                           ↓                                     │
│                    .heartbeats/                                 │
│                   (liveness monitoring)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
acfs-enhanced/
├── install.sh              # Bootstrap a project
├── docs/
│   └── quick-start.md      # Getting started guide
├── templates/
│   ├── .beads/
│   │   ├── PRIME.md.template
│   │   └── config.yaml
│   ├── .claude/
│   │   ├── settings.local.json
│   │   └── agents/
│   └── workflows/
│       └── content-generation/
├── scripts/
│   ├── heartbeat.sh        # Send agent heartbeat
│   ├── monitor.sh          # Watch for stuck agents
│   └── recover-agent.sh    # Restart stuck agents
├── hooks/
│   └── dcg-rules/          # DCG safety configuration
└── examples/
    ├── PRIME-seo-example.md
    └── brand-voice-cybersecurity.md
```

## Base ACFS Tools Used

| Tool | Purpose | Docs |
|------|---------|------|
| **bd** | Issue tracking with dependencies | [Beads](https://agent-flywheel.com/learn/beads) |
| **ntm** | Multi-agent session management | [NTM](https://agent-flywheel.com/learn/commands) |
| **dcg** | Pre-execution safety | [DCG](https://agent-flywheel.com/learn/dcg) |
| **cass** | Session history search | [CASS](https://agent-flywheel.com/learn/cass) |

## Usage

See [docs/quick-start.md](docs/quick-start.md) for complete instructions.

```bash
# 1. Initialize project
./install.sh /path/to/your-project

# 2. Edit .beads/PRIME.md with your workflow

# 3. Create work items
bd create "Task 1" --label=work
bd create "Task 2" --label=work

# 4. Spawn agents
ntm spawn your-project --cc=5

# 5. Start work
echo "Follow PRIME.md" | ntm send your-project --cc=""

# 6. Monitor
./scripts/monitor.sh
```

## Examples

- [SEO Content Generation](examples/workflow-seo-readme.md) - Multi-agent content production
- [PRIME Template](examples/PRIME-seo-example.md) - Complete PRIME.md example
- [Brand Voice](examples/brand-voice-cybersecurity.md) - Output quality enforcement

## Companion Tools

These tools from the ACFS ecosystem complement acfs-enhanced:

| Tool | Purpose | Priority |
|------|---------|----------|
| **[process_triage](https://github.com/Dicklesworthstone/process_triage)** | Bayesian stuck process detection | High - smarter than heartbeat timeouts |
| **[coding_agent_usage_tracker](https://github.com/Dicklesworthstone/coding_agent_usage_tracker)** | Multi-provider cost monitoring | High - track swarm costs |
| **[wezterm_automata](https://github.com/Dicklesworthstone/wezterm_automata)** | Terminal hypervisor with pattern triggers | Medium - alternative to NTM |
| **[meta_skill](https://github.com/Dicklesworthstone/meta_skill)** | Skill/workflow sharing platform | Medium - distribute PRIME templates |
| **[rano](https://github.com/Dicklesworthstone/rano)** | Network observer for AI CLIs | Medium - debug API issues |

See [docs/companion-tools.md](docs/companion-tools.md) for integration guides.

## License

MIT
