# Manual Benchmark Testing Protocol

Guide for manually testing acfs-enhanced improvements using real SWE-bench tasks with CASS logging.

## Overview

We test configurations by **manually solving the same tasks** with different setups and comparing:
- **Success rate**: Did we fix the bug?
- **Time taken**: How long to solve?
- **Code quality**: Is the fix clean and minimal?
- **Process quality**: Did we stay focused? Make unnecessary changes?

**CASS automatically logs everything** - we just need to solve tasks and review the transcripts.

## Test Configurations

### Config 1: Vanilla (Baseline)
- No PRIME template
- No workflow guardrails
- Just you + Claude Code

### Config 2: acfs-enhanced
- PRIME template loaded
- Workflow guidance active
- Heartbeat monitoring

### Config 3: +mcp_agent_mail (Future)
- Add agent messaging
- File reservation system

### Config 4: +CASS memory (Future)
- Cross-session learning
- Pattern recognition

## Setup

### 1. Prepare Test Tasks

```bash
cd /data/projects/acfs-enhanced/benchmark

# Generate task list
source venv/bin/activate
python select_tasks.py

# Review tasks
cat manual_test_tasks.json | jq '.[] | {task_id, repo, instance_id}'
```

### 2. Create Test Workspace

```bash
# Create directory for test repos
mkdir -p ~/swebench-test
cd ~/swebench-test
```

### 3. Verify CASS is Running

```bash
cass stats
# Should show your existing sessions

# CASS automatically indexes new sessions - no setup needed!
```

## Testing Protocol

### For Each Task

#### Step 1: Clone Repository

```bash
cd ~/swebench-test

# Get repo from task JSON
REPO="django/django"  # example
TASK_ID="TASK-01"
BASE_COMMIT="abc123def"

# Clone
git clone https://github.com/$REPO.git $TASK_ID-repo
cd $TASK_ID-repo
git checkout $BASE_COMMIT
```

#### Step 2: Start Claude Code Session (Tagged)

**Important**: Use a **descriptive directory name** so CASS can differentiate sessions:

```bash
# For vanilla test
cd ~/swebench-test/TASK-01-vanilla
git clone ...
claude

# For acfs-enhanced test
cd ~/swebench-test/TASK-01-acfs
git clone ...
# Copy PRIME template
cp /data/projects/acfs-enhanced/templates/.beads/PRIME.md.template .claude/PRIME.md
claude
```

The directory name becomes the session identifier in CASS!

#### Step 3: Solve the Task

**Present the problem to Claude:**

```
I need you to fix this GitHub issue:

[paste problem_statement from task JSON]

The repository is at base commit [commit hash].

Please:
1. Understand the issue
2. Locate the relevant code
3. Implement a minimal fix
4. Verify with tests

[For acfs-enhanced: "Follow the PRIME.md template"]
```

**Track your time:**
```bash
# Start timer
START_TIME=$(date +%s)

# ... work with Claude ...

# End timer
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo "Time: ${ELAPSED}s"
```

#### Step 4: Verify the Fix

```bash
# Apply test patch from task JSON
git apply << 'EOF'
[paste test_patch]
EOF

# Run tests
pytest  # or whatever test command the repo uses

# Record result
echo "Tests passed: YES/NO"
```

#### Step 5: Record Results

Add to scorecard (see template below):

```bash
# Append to results file
echo "TASK-01,vanilla,$ELAPSED,PASS" >> vanilla_results.csv
echo "TASK-01,acfs,$ELAPSED,PASS" >> acfs_results.csv
```

## CASS Integration

### Reviewing Sessions

After completing tasks, review what happened:

```bash
# Search for your test sessions
cass search "swebench" --after 2026-01-23

# Export specific session
cass export ~/.local/share/claude/sessions/TASK-01-vanilla.jsonl --format markdown > TASK-01-vanilla-transcript.md

# Compare sessions side-by-side
diff TASK-01-vanilla-transcript.md TASK-01-acfs-transcript.md
```

### Analyzing Patterns

```bash
# How many tool calls did each config use?
cass search "tool_use" --in TASK-01-vanilla | wc -l
cass search "tool_use" --in TASK-01-acfs | wc -l

# Did PRIME prevent scope creep?
cass search "refactor" --in TASK-01-vanilla
cass search "refactor" --in TASK-01-acfs

# Were there errors/retries?
cass search "error" --in TASK-01-vanilla
cass search "error" --in TASK-01-acfs
```

### Exporting for Analysis

```bash
# Export all test sessions
for task in TASK-{01..14}; do
  cass export ~/.local/share/claude/sessions/${task}-vanilla.jsonl \
    --format json > results/${task}-vanilla.json

  cass export ~/.local/share/claude/sessions/${task}-acfs.jsonl \
    --format json > results/${task}-acfs.json
done
```

## Scorecard Template

Create `results/scorecard.csv`:

```csv
task_id,config,time_seconds,outcome,tests_pass,notes
TASK-01,vanilla,450,PASS,YES,Clean fix but took a while to find the issue
TASK-01,acfs,320,PASS,YES,PRIME template kept focus - faster
TASK-02,vanilla,680,FAIL,NO,Made too many changes; broke other tests
TASK-02,acfs,520,PASS,YES,Minimal change as directed by PRIME
...
```

Fields:
- **task_id**: TASK-01 through TASK-14
- **config**: vanilla, acfs, acfs+mail, acfs+cass
- **time_seconds**: Time to complete (0 if gave up)
- **outcome**: PASS (fixed), FAIL (didn't work), TIMEOUT (gave up after 30min)
- **tests_pass**: YES/NO/PARTIAL
- **notes**: Brief observation

## Quality Metrics

Beyond pass/fail, track:

### Focus & Scope Discipline
- Did we only change what's needed?
- Were there "while we're here" refactors?
- Did we stay on task?

**How to check:**
```bash
# Count files changed
git diff --stat $BASE_COMMIT..HEAD

# Review CASS transcript for scope creep
cass search "refactor\|improve\|also\|while we" --in TASK-XX
```

### Error Recovery
- How many failed attempts before success?
- Did we learn from errors?

**How to check:**
```bash
# Search for error patterns
cass search "error\|failed\|traceback" --in TASK-XX | wc -l
```

### Consistency
- Is code style consistent with the repo?
- Proper error handling?
- Tests added if needed?

**Manual review of the diff**

## Tips for Effective Testing

### 1. Start Fresh
- Use a new repo clone for each test
- Don't carry over changes between vanilla/acfs tests
- Clear your head between attempts

### 2. Be Honest
- If you get stuck after 30min, mark it TIMEOUT
- Don't "help" Claude more in one config vs another
- Record actual time, not idealized time

### 3. Take Notes
- Jot down observations during the session
- What worked well?
- What was frustrating?
- Did PRIME actually help or just add overhead?

### 4. Use CASS Effectively
- Tag sessions clearly with directory names
- Export transcripts right after each session
- Compare transcripts while the experience is fresh

## Analysis Scripts

After collecting results, analyze:

```bash
# Run analysis
cd /data/projects/acfs-enhanced/benchmark
python analyze_manual_results.py \
  --scorecard results/scorecard.csv \
  --transcripts results/transcripts/ \
  --output results/manual_benchmark_report.md
```

This will generate:
- Success rate comparison
- Time comparison
- Quality metrics
- Transcript analysis (tool usage, error patterns)

## Example Session

### Vanilla Test

```bash
$ cd ~/swebench-test
$ git clone https://github.com/django/django.git TASK-01-vanilla
$ cd TASK-01-vanilla
$ git checkout abc123

$ claude
> I need you to fix: Set default FILE_UPLOAD_PERMISSION to 0o644...
> [Claude works on the fix]
> [20 minutes later]
> Done!

$ # Apply test patch
$ git apply test.patch
$ pytest tests/file_uploads/
PASSED ✓

# Record: TASK-01,vanilla,1200,PASS,YES,Fixed but explored several wrong paths first
```

### acfs-enhanced Test

```bash
$ cd ~/swebench-test
$ git clone https://github.com/django/django.git TASK-01-acfs
$ cd TASK-01-acfs
$ git checkout abc123

$ # Load PRIME template
$ mkdir .claude
$ cp /data/projects/acfs-enhanced/templates/.beads/PRIME.md.template .claude/PRIME.md

$ claude
> I need you to fix: Set default FILE_UPLOAD_PERMISSION to 0o644...
> Follow the PRIME.md workflow.
> [Claude works with template guidance]
> [15 minutes later]
> Done!

$ # Apply test patch
$ git apply test.patch
$ pytest tests/file_uploads/
PASSED ✓

# Record: TASK-01,acfs,900,PASS,YES,PRIME kept focus - found right file quickly
```

### Compare Transcripts

```bash
$ cass export ~/.local/share/claude/sessions/TASK-01-vanilla.jsonl > vanilla.md
$ cass export ~/.local/share/claude/sessions/TASK-01-acfs.jsonl > acfs.md
$ diff -u vanilla.md acfs.md | less

# Notice differences:
# - vanilla: read 8 files before finding the right one
# - acfs: read 3 files, stayed focused
# - vanilla: suggested refactoring unrelated code
# - acfs: minimal change only
```

## Target: Complete in 1-2 Days

- **Day 1**: Test vanilla + acfs on all 14 tasks (~6-8 hours)
- **Day 2**: Export CASS transcripts, analyze, generate report (~2-4 hours)

This gives us **real data** on whether acfs-enhanced actually helps, based on your direct experience with the tools.

## What This Tells Us

### If acfs-enhanced wins (>70% success vs 50% vanilla):
✅ PRIME templates provide real value
→ Proceed to test +mcp_agent_mail, +CASS memory

### If vanilla wins:
❌ PRIME adds overhead without benefit
→ Simplify templates, try minimal version

### If they're similar:
⚠️ PRIME doesn't impact single-session work
→ Focus on multi-agent features where coordination matters

## Next Steps

After baseline (vanilla vs acfs):

1. **Phase 2**: Add mcp_agent_mail
   - Test file reservation preventing conflicts
   - Agent messaging for coordination

2. **Phase 3**: Add CASS memory integration
   - Test cross-session learning
   - Pattern recognition

3. **Phase 4**: Full stack
   - All tools integrated
   - Multi-agent concurrent work

Each phase: 14 tasks × new config = incremental cost.

---

**Ready to start?**

```bash
cd /data/projects/acfs-enhanced/benchmark
python select_tasks.py              # Get task list
cat MANUAL_TESTING.md               # Read this guide
mkdir ~/swebench-test               # Create workspace
# Start with TASK-01!
```
