# ACFS Enhanced: Long-Running Agent Orchestration

## Problem Statement

The base ACFS tooling (from agent-flywheel.com) provides excellent individual tools:
- **bd/bv** - Graph-aware issue tracking with PageRank prioritisation
- **cass** - Cross-agent session search
- **ubs** - Pre-commit code quality scanning
- **dcg** - Destructive command guard (PreToolUse hook)
- **ru** - Multi-repo management with Agent Sweep
- **jfp** - Prompt library
- **apr** - Automated plan revision

**What's missing**: Patterns and scaffolding for **long-running, multi-agent workflows** that:
1. Survive context compaction (PRIME injection)
2. Coordinate parallel agents without conflicts (claiming, heartbeats)
3. Enforce consistent output quality (brand voice, humaniser)
4. Monitor agent health (heartbeat system)
5. Auto-recover from stuck states

## What We Built (Steward Security Project)

### 1. PRIME Template System
**Location**: `.beads/PRIME.md`

Auto-injected context that survives SessionStart and PreCompact hooks:
```markdown
# Beads Workflow Context - {Project Name}

> **Context Recovery**: This is auto-injected on SessionStart and PreCompact

## YOUR MISSION
{Clear objective for this agent type}

## WORKFLOW (Follow Exactly)
{Step-by-step commands with exact syntax}

## KEY RULES
{Non-negotiable constraints}

## SESSION CLOSE PROTOCOL
{What to do when work is complete}
```

**Value**: Agents don't "forget" their mission after long sessions or compaction.

### 2. Heartbeat Monitoring System
**Location**: `.heartbeats/` + `seo/scripts/heartbeat.sh`

```bash
# Agent sends heartbeat when claiming work
seo/scripts/heartbeat.sh "$AGENT_NAME" "$SESSION_NAME" "$PANE_NUM" "$BEAD_ID" "$ARTICLES_DONE"

# Monitor checks for stale heartbeats (>5 min)
# Can auto-restart stuck agents via NTM
```

**Files created**:
```
.heartbeats/
├── agent-1.json    # {"agent":"agent-1","bead":"b-123","articles":5,"ts":1234567890}
├── agent-2.json
└── ...
```

**Value**: Know when agents are stuck, can auto-recover.

### 3. Atomic Work Claiming
**Pattern**: `bd update <bead-id> --claim`

- Fails fast if already claimed by another agent
- Prevents duplicate work in parallel execution
- Combined with heartbeats = reliable coordination

### 4. Brand Voice Enforcement
**Location**: `.claude/agents/humanizer.md`

24-pattern AI detector with rewrite rules:
- British English enforcement (organisation, defence, colour)
- Banned phrases ("Additionally", "Furthermore", "It's important to note")
- Word count constraints
- Tone guidelines

**Value**: Consistent output quality across multiple agents.

### 5. Skills with Subagent Composition
**Location**: `~/.claude/skills/bd-to-br-migration/`

Skills that spawn and coordinate subagents:
```
bd-to-br-migration/
├── skill.md           # Entry point
├── scripts/
│   ├── verify.sh
│   └── migrate.sh
└── subagents/
    ├── analyzer.md
    └── migrator.md
```

### 6. SEO Workflow (Reference Implementation)
**Location**: `seo/`

Complete multi-agent content generation:
```
seo/
├── context/
│   └── brand-voice.md
├── prompts/
│   └── glossary-prompt.md
├── scripts/
│   └── heartbeat.sh
├── output/
│   └── glossary/
├── data/
│   └── keywords.csv
└── README.md
```

---

## New Repository Structure

```
acfs-enhanced/
├── README.md                    # Quick start guide
├── install.sh                   # Bootstrap script
│
├── docs/
│   ├── quick-start.md           # 5-minute setup
│   ├── prime-templates.md       # How to write PRIME.md
│   ├── multi-agent-patterns.md  # Coordination patterns
│   ├── heartbeat-system.md      # Monitoring setup
│   ├── brand-voice.md           # Output quality control
│   └── troubleshooting.md       # Common issues
│
├── templates/
│   ├── .beads/
│   │   ├── PRIME.md.template    # Customisable PRIME
│   │   ├── config.yaml          # Default config
│   │   └── README.md            # What goes here
│   │
│   ├── .claude/
│   │   ├── settings.local.json  # Project-level settings
│   │   └── agents/
│   │       └── humanizer.md     # Brand voice enforcer
│   │
│   ├── .heartbeats/
│   │   └── .gitkeep
│   │
│   └── workflows/
│       └── content-generation/  # SEO workflow template
│           ├── context/
│           ├── prompts/
│           ├── scripts/
│           └── output/
│
├── hooks/
│   ├── session-start/
│   │   └── prime-inject.sh      # Inject PRIME on session start
│   ├── pre-compact/
│   │   └── prime-inject.sh      # Re-inject before compaction
│   └── dcg-rules/
│       ├── git-safety.toml
│       └── filesystem-safety.toml
│
├── skills/
│   ├── README.md                # How to create skills
│   └── examples/
│       ├── content-generator/   # SEO skill
│       └── code-reviewer/       # Review skill
│
├── scripts/
│   ├── heartbeat.sh             # Generic heartbeat sender
│   ├── monitor.sh               # Heartbeat monitor
│   ├── recover-agent.sh         # Restart stuck agents
│   └── setup-project.sh         # Scaffold new project
│
└── examples/
    └── steward-security/        # This project as reference
        ├── .beads/
        ├── .claude/
        ├── seo/
        └── README.md
```

---

## Implementation Plan

### Phase 1: Extract and Document (Day 1)

1. **Extract from steward-security**:
   - [ ] Copy `.beads/PRIME.md` → `templates/.beads/PRIME.md.template`
   - [ ] Copy `seo/scripts/heartbeat.sh` → `scripts/heartbeat.sh`
   - [ ] Copy `.claude/agents/humanizer.md` → `templates/.claude/agents/`
   - [ ] Copy `seo/` structure → `templates/workflows/content-generation/`

2. **Document patterns**:
   - [ ] Write `docs/quick-start.md`
   - [ ] Write `docs/prime-templates.md`
   - [ ] Write `docs/multi-agent-patterns.md`

### Phase 2: Genericise (Day 2)

1. **Make templates configurable**:
   - [ ] Add `{{PROJECT_NAME}}`, `{{MISSION}}` placeholders to PRIME.md
   - [ ] Create `setup-project.sh` that prompts for values

2. **Create hooks**:
   - [ ] `session-start/prime-inject.sh` - reads `.beads/PRIME.md`, outputs to stdout
   - [ ] Document how to configure in `~/.claude/settings.json`

3. **Heartbeat system**:
   - [ ] Genericise `heartbeat.sh` to work with any workflow
   - [ ] Write `monitor.sh` that watches `.heartbeats/`
   - [ ] Write `recover-agent.sh` that restarts via NTM

### Phase 3: Integration with Base ACFS (Day 3)

1. **Bridge to existing tools**:
   - [ ] Document how PRIME works with `bd` workflow
   - [ ] Document how heartbeats integrate with `ru agent-sweep`
   - [ ] Document DCG rules for safe parallel execution

2. **Skills examples**:
   - [ ] Extract content-generator skill
   - [ ] Create code-reviewer skill template

### Phase 4: Testing and Polish (Day 4)

1. **Test on fresh project**:
   - [ ] Run `./install.sh` on clean system
   - [ ] Run `./scripts/setup-project.sh` to scaffold
   - [ ] Verify multi-agent workflow works

2. **Write troubleshooting guide**

---

## Key Decisions Needed

### 1. Where do hooks live?
- **Option A**: In `~/.claude/settings.json` (user-global)
- **Option B**: In `.claude/settings.local.json` (project-local)
- **Recommendation**: Project-local with install script that links/copies

### 2. NTM dependency?
- NTM not documented on agent-flywheel.com (404)
- Do we need it, or can we use plain tmux?
- **Recommendation**: Document both - NTM if available, tmux fallback

### 3. Heartbeat storage?
- **Option A**: Files in `.heartbeats/` (current)
- **Option B**: SQLite in `.beads/`
- **Option C**: Redis/external (for distributed)
- **Recommendation**: Keep files, add SQLite option later

### 4. Skill distribution?
- **Option A**: Copy into each project
- **Option B**: Symlink from `~/.claude/skills/`
- **Option C**: Install via `jfp install`
- **Recommendation**: Start with copy, add jfp integration later

---

## Success Criteria

1. **New project bootstrap in <5 minutes**:
   ```bash
   curl -fsSL https://acfs-enhanced.dev/install.sh | bash
   cd my-project
   acfs-init --template=content-generation
   ```

2. **Agent survives 8+ hour session** without losing context

3. **3+ agents work in parallel** without conflicts

4. **Stuck agent auto-recovered** within 10 minutes

5. **Output quality consistent** across all agents (brand voice)

---

## NTM (Named Tmux Manager) - Key Orchestration Tool

NTM IS installed (`~/.local/bin/ntm`, 20MB binary). Key capabilities:

### Spawning Agents
```bash
ntm spawn myproject --cc=2 --cod=2    # 2 Claude + 2 Codex agents
ntm add myproject --cc=1              # Add another Claude agent
```

### Robot Mode (for automation)
```bash
ntm --robot-spawn=seo-gen --spawn-cc=4 --spawn-wait    # Spawn and wait for ready
ntm --robot-send=seo-gen --msg="Start work" --all      # Broadcast to all
ntm --robot-status                                      # Get all session states
ntm --robot-snapshot                                    # Full state dump
ntm --robot-tail=seo-gen --lines=50                    # Get recent output
```

### Integration Points
- **Agent Mail**: `ntm mail` / `ntm lock` for file coordination
- **CASS**: `ntm cass` for session search
- **Checkpoints**: `ntm checkpoint` for save/restore
- **Health**: `ntm health` for agent status

### Documentation
NTM is documented on agent-flywheel.com (lesson 8: NTM Command Center, lesson 9: NTM Prompt Palette).

---

## Open Questions

1. ~~Where is NTM source/binary?~~ FOUND: `~/.local/bin/ntm`
2. Should this be a separate repo or monorepo with ACFS?
3. How to handle updates to base ACFS tools?
4. License considerations?

---

## Next Steps

1. [ ] Review this plan
2. [ ] Decide on open questions
3. [ ] Create GitHub repo
4. [ ] Start Phase 1 extraction
