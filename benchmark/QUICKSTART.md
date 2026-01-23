# Quick Start: Manual Benchmarking

Fast track to running manual benchmarks with CASS logging.

## Setup (5 minutes)

```bash
cd /data/projects/acfs-enhanced/benchmark

# 1. Install dependencies
./scripts/setup.sh

# 2. Select test tasks
source venv/bin/activate
python select_tasks.py

# 3. Create workspace
mkdir -p ~/swebench-test/results

# 4. Copy scorecard template
cp scorecard_template.csv ~/swebench-test/results/scorecard.csv
```

## Test One Task (30-60 minutes)

### Vanilla Test

```bash
cd ~/swebench-test

# Get task details
cat /data/projects/acfs-enhanced/benchmark/manual_test_tasks.json | jq '.[0]'

# Clone repo
git clone https://github.com/django/django.git TASK-01-vanilla
cd TASK-01-vanilla
git checkout <base_commit>

# Start timer
START=$(date +%s)

# Start Claude Code
claude

# In Claude:
> Fix this issue: [paste problem_statement]
> [Work on the fix...]

# End timer
END=$(date +%s)
ELAPSED=$((END - START))
echo "Time: ${ELAPSED}s"

# Test solution
git apply << 'EOF'
[paste test_patch from JSON]
EOF

pytest  # or appropriate test command

# Record in scorecard:
# TASK-01,vanilla,$ELAPSED,PASS/FAIL,YES/NO,<files_changed>,<quality 1-5>,<notes>
```

### acfs-enhanced Test

```bash
cd ~/swebench-test

# Clone repo
git clone https://github.com/django/django.git TASK-01-acfs
cd TASK-01-acfs
git checkout <base_commit>

# Copy PRIME template
mkdir -p .claude
cp /data/projects/acfs-enhanced/templates/.beads/PRIME.md.template .claude/PRIME.md

# Start timer & Claude Code
START=$(date +%s)
claude

# In Claude:
> Fix this issue: [paste problem_statement]
> Follow the PRIME.md workflow
> [Work on the fix...]

END=$(date +%s)
ELAPSED=$((END - START))

# Test & record same as vanilla
```

## After Testing (30 minutes)

### Export CASS Sessions

```bash
cd /data/projects/acfs-enhanced/benchmark

# Find your test sessions
cass search "TASK-01" --after 2026-01-23

# Export them
cass export <vanilla-session-path> --format json > results/transcripts/TASK-01-vanilla.json
cass export <acfs-session-path> --format json > results/transcripts/TASK-01-acfs.json
```

### Generate Report

```bash
python analyze_manual_results.py \
  --scorecard ~/swebench-test/results/scorecard.csv \
  --transcripts results/transcripts/ \
  --output results/benchmark_report.md

cat results/benchmark_report.md
```

## Full Test Plan (1-2 days)

### Day 1: Testing (6-8 hours)

Test all 14 tasks (both configs):
- Morning: TASK-01 through TASK-07
- Afternoon: TASK-08 through TASK-14
- ~20-30 min per task × 2 configs = ~7 hours

### Day 2: Analysis (2-4 hours)

- Export all CASS sessions
- Run analysis script
- Review transcripts for patterns
- Generate final report

## Tips for Speed

1. **Batch similar repos** - Do all Django tasks together (context stays warm)
2. **Use tmux** - Run vanilla in one pane, acfs in another
3. **Script the setup** - Automate git clone + checkout
4. **Take breaks** - Fresh mind = better testing

## Expected Results

### Success Looks Like:
- acfs-enhanced: 10-12/14 tasks passed (71-86%)
- vanilla: 7-9/14 tasks passed (50-64%)
- **Delta: +15-20% improvement**

### What We Learn:
- Does PRIME keep focus during long debugging?
- Fewer "while we're here" refactors with guidance?
- Better error recovery with structured workflow?

---

**Start with just 1 task to get the feel, then scale up!**
