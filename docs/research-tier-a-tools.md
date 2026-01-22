# Tier A Tools: Detailed Research & Integration

Research on Tier A (Essential) repositories that power the ACFS ecosystem. Based on agent-driven codebase analysis and Jeffrey Emanuel's X posts (@doodlestein).

---

## Overview

These 9 repos form the core infrastructure for multi-agent agentic coding workflows:

| Tool | Stars | Status | Integration |
|------|-------|--------|-------------|
| agentic_coding_flywheel_setup | 848 | Core | VPS bootstrap system |
| mcp_agent_mail | 1,534 | Core | Agent coordination |
| beads_viewer | 1,061 | Core | Work item dashboard |
| claude_code_agent_farm | 635 | Core | Agent spawning |
| cass_memory_system | 168 | Core | Cross-session memory |
| slb | 52 | Core | Dangerous action sign-off |
| misc_coding_agent_tips_and_scripts | 178 | Core | Best practices |
| agent_flywheel_clawdbot_skills_and_integrations | 30 | Core | Skill extensions |
| curl_bash_one_liners_for_flywheel_tools | 13 | Core | Installation scripts |

---

## 1. agentic_coding_flywheel_setup (ACFS)

**Purpose**: Complete system bootstrap from fresh VPS to full agentic environment in <1 hour

**What it does**:
- Single `curl | bash` installs 30+ tools
- Configures zsh with powerlevel10k
- Sets up language runtimes: bun, Python, Rust, Go
- Deploys 3 AI agents: Claude Code, Codex CLI, Gemini CLI
- Installs entire coordination stack: NTM, DCG, CASS, BD, BEADS_VIEWER, SLB

**Key components** (from research):
- `acfs.manifest.yaml` - Tool registry and metadata
- `scripts/lib/phase-dicklesworthstone-tools.sh` - Tool installation phases
- `scripts/generated/install_stack.sh` - Full tool stack installer
- `packages/` - Shared components across all tools

**Integration with acfs-enhanced**:
- ACFS is a "meta-installer" - it installs base ACFS tools
- acfs-enhanced builds ON TOP of ACFS with templates (PRIME.md, CASS playbooks)
- Could reference ACFS manifest to show what's automatically installed vs. acfs-enhanced templates

**Recommendation**: Link to ACFS as the prerequisite in acfs-enhanced README (✓ already done)

**X Context** (from @doodlestein):
> "Agentic Coding Flywheel Setup transforms a fresh VPS into a fully-armed agentic coding environment in under an hour. Zero to fully-configured agentic coding VPS in 30 minutes."

---

## 2. mcp_agent_mail (am)

**Purpose**: Inter-agent messaging, coordination, and conflict prevention ("Gmail for agents")

**What it does**:
- Agents register with memorable identities (e.g., "GreenCastle", "BlueLake")
- Send/receive thread-based messages with acknowledgments
- File reservations (advisory + enforced pre-commit hook)
- Searchable message history (SQLite FTS5)
- Git-backed artifacts (human-auditable)

**Architecture**:
- HTTP-only transport over Git + SQLite persistence
- Dual model: Git for audit trails, SQLite for fast queries
- Contact policies for who can message whom
- Staleness detection releases abandoned locks

**Integration with acfs-enhanced**:
- Add to PRIME.md: agents use `macro_start_session()` to reserve files before claiming work
- Replaces simple heartbeats with richer communication
- Enables work passing between agents (e.g., "API module complete → ready for integration")

**Example from PRIME.md**:
```python
send_message(
  sender="Agent1",
  to=["Agent2"],
  subject="Module ready",
  body_md="## Changes\n- /src/api/users.py complete"
)
```

**Installation**:
```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail/main/scripts/install.sh" | bash
am  # Start server
```

**X Context** (from @doodlestein):
> "Each agent has a certain personality that emerges when they coordinate via MCP Agent Mail...Claude Sonnet 4.5 with ultrathink is eager but sloppy. Codex with gpt-5-codex takes longer but makes fewer mistakes—often becomes supervisor."

---

## 3. beads_viewer (bv)

**Purpose**: Visual TUI dashboard for Steve Yegge's beads task management

**What it does**:
- Real-time TUI for viewing work items (beads)
- DAG-based dependency analysis
- Graph metrics: PageRank, betweenness, critical path, cycle detection
- Triage system: `bv --robot-triage` outputs JSON for agents
- Multiple view modes: kanban, timeline, dependencies, burndown

**Architecture**:
- Written in Go
- Loads JSONL issue files
- Real-time TUI via bubbletea/Bubble Tea framework
- Export to multiple formats

**Integration with acfs-enhanced**:
- Complements `bd ready --json` commands in PRIME.md
- Agents can periodically run `bv --robot-triage` for smarter work selection
- Triage system provides recommendations instead of just listing ready items

**Example**:
```bash
# In PRIME.md workflow loop:
bv --robot-triage --label=seo | jq '.recommendations[]'
# Returns: prioritized recommendations, blockers, critical path items
```

**X Context** (from @doodlestein):
> "I'm a huge fan of Steve Yegge's beads project. I probably type 'beads' 500+ times a day while juggling 10 projects at once."

---

## 4. claude_code_agent_farm

**Purpose**: Infrastructure for spawning and managing multiple Claude Code agents

**What it does**:
- Python application that manages tmux sessions
- Spawns multiple Claude agents in parallel
- Health checks and liveness monitoring
- Provides `view_agents.sh` for status visualization
- Integrates with NTM (Named Tmux Manager)

**Architecture**:
- Works WITH NTM - doesn't replace it
- Manages Claude Code CLI instances
- Monitors process health
- Coordinates work distribution

**Integration with acfs-enhanced**:
- NTM is the PRIMARY tool in ACFS
- claude_code_agent_farm is an ALTERNATIVE/COMPLEMENT for specific workflows
- Use NTM in acfs-enhanced docs, mention agent_farm as option for non-tmux environments

**Recommendation**: Reference in companion-tools.md as "Alternative to NTM for non-tmux-based deployments"

---

## 5. cass_memory_system (cm / cass)

**Purpose**: Cross-agent session search and procedural memory

**What it does**:
- `cm context <query>` returns relevant procedural rules
- Three memory layers:
  - **Episodic**: Raw session logs (CASS)
  - **Semantic**: Procedural rules with confidence scoring
  - **Playbook**: Best practices with confidence decay

**Implementation** (from research):
- TypeScript-based
- `cm.ts` - Context command with semantic matching
- `playbook.ts` - Rule storage and retrieval
- `scoring.ts` - Relevance decay algorithms
- `semantic.ts` - Task description matching
- `diary.ts` - Session memory

**Integration with acfs-enhanced**:
- PRIME.md includes: `cm context "generate glossary article" --json`
- Agents read playbook rules BEFORE starting work
- FEEDBACK loop: `[cass: helpful b-xxx]` marks useful patterns

**Example from steward-security PRIME.md** (already in place):
```bash
# 1. FIRST: Get procedural rules from CASS Memory
cm context "generate glossary article" --json
```

**Installation**:
```bash
# Part of ACFS setup - includes CASS installation
```

---

## 6. slb (Simultaneous Launch Button)

**Purpose**: Agent sign-off system for dangerous commands

**What it does**:
- Three-tier risk classification (LOW, MEDIUM, HIGH)
- Cryptographic command binding
- Claude Code hooks integration
- Prevents agents from running dangerous commands without approval

**Architecture** (from research):
- Go implementation
- `internal/integrations/claude_code.go` - Hook system integration
- `internal/core/patterns.go` - Risk pattern matching
- Integrates via `.claude/hooks/PreToolUse`

**Differences from DCG**:
- **DCG**: Destructive Command Guard - blocks dangerous commands PRE-EXECUTION
- **SLB**: Requires SIGN-OFF - agent must acknowledge dangerous action

**Integration with acfs-enhanced**:
- Complements DCG for agent safety
- Could add to `.claude/settings.local.json` hooks
- Useful for production deployments

**Installation**:
```bash
# Included in ACFS setup
```

**Example flow**:
```
Agent decides to run: git push --force
↓
SLB classifies as HIGH risk
↓
Agent must sign-off: "Acknowledge risk: FORCE_PUSH"
↓
Command executes only with signed token
```

---

## 7. misc_coding_agent_tips_and_scripts

**Purpose**: Best practices, optimization techniques, and setup guides

**Key guides** (from research):
- `DESTRUCTIVE_GIT_COMMAND_CLAUDE_HOOKS_SETUP.md` - Git safety
- `SETTING_UP_CLAUDE_CODE_NATIVE.md` - Agent configuration
- `FIX_CLAUDE_CODE_MCP_CONFIG.md` - MCP fixes
- `GUIDE_TO_DEVOPS_CLI_TOOLS.md` - DevOps patterns
- `REDUCING_VERCEL_BUILD_CREDITS.md` - Cost optimization
- `GUIDE_TO_SETTING_UP_HOST_AWARE_COLOR_THEMES_FOR_GHOSTTY_AND_WEZTERM.md` - UX
- `WEZTERM_PERSISTENT_REMOTE_SESSIONS.md` - Remote agent setup

**Integration with acfs-enhanced**:
- Extract key patterns for `docs/best-practices.md`
- Use destructive git hooks example
- Reference for agent configuration

---

## 8. agent_flywheel_clawdbot_skills_and_integrations

**Purpose**: Skills and integrations for Clawdbot (Slack bot version of agent flywheel)

**What it does**:
- Extends agent flywheel for Slack integration
- Provides skills for team coordination
- Slack-based task management

**Integration with acfs-enhanced**:
- Reference as ecosystem extension
- Not required for core ACFS, but useful for team coordination

---

## 9. curl_bash_one_liners_for_flywheel_tools

**Purpose**: Installation scripts for individual ACFS tools

**What it does**:
- Individual curl installers for:
  - NTM (Named Tmux Manager)
  - DCG (Destructive Command Guard)
  - CASS (session search)
  - BD (beads)
  - And others

**Integration with acfs-enhanced**:
- Link from `install.sh` for granular tool installation
- Alternative to full ACFS setup

---

## X Posts Context (@doodlestein)

### Key Insights:

**Unix Philosophy for Agent Tools**:
> "The Unix tool approach of having focused, composable functional units that can be used in isolation or as part of a larger pipeline is also the best approach for tooling for coding agents."

**Problem with Monolithic Systems**:
> "The problem with trying to make a big unified system is people have their own workflows, so one-size-fits-all projects turn into sprawling complexity."

**Agent Personalities**:
> "Each agent has a personality that emerges...intertwined with their speed and cognitive power and confidence."

**Tool Ecosystem**:
- Agent Mail, Task Management (Beads), Task Selection (beads_viewer), History Search (CASS), Linting (UBS), Sensitive Commands (SLB), Session Management (NTM), Memory (CASS)

**Current Focus**:
- "Juggling like 10 projects at the same time"
- Extensive use of beads for multi-project coordination
- Heavy emphasis on agent communication via MCP Agent Mail

---

## Integration Recommendations

### For acfs-enhanced v2.0:

1. **Add to quick-start.md**:
   - Use `beads_viewer --robot-triage` for work selection
   - Use `cm context` in PRIME.md
   - Optional: Add `am` (agent_mail) for inter-agent coordination

2. **Add SLB hooks to `.claude/settings.local.json`**:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "command": "slb check --risk-only",
           "type": "command"
         }
       ]
     }
   }
   ```

3. **Add CASS feedback patterns to agent guidelines**

4. **Reference agent_farm as alternative to NTM** for non-tmux setups

5. **Create `docs/agent-communication-patterns.md`**:
   - How to use mcp_agent_mail for work passing
   - Conflict prevention with file reservations
   - Message templates for common scenarios

---

## Summary

**These 9 Tier A tools form a complete, composable system**:

- **Setup**: agentic_coding_flywheel_setup
- **Spawning**: NTM (+ claude_code_agent_farm option)
- **Memory**: CASS memory_system
- **Work Management**: Beads + beads_viewer
- **Coordination**: mcp_agent_mail
- **Safety**: DCG + SLB
- **Best Practices**: misc_coding_agent_tips_and_scripts
- **Extensions**: agent_flywheel_clawdbot_skills

**acfs-enhanced's role**: Layer on TOP of these tools with:
- PRIME templates for consistent instruction injection
- Heartbeat monitoring for liveness
- Brand voice enforcement
- Recovery scripts for stuck agents
- Quick-start guides for combining tools

All work TOGETHER, none replace each other.
