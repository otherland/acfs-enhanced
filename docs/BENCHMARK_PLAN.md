# ACFS Benchmark Plan: SWE-bench Lite Baseline

**Goal**: Establish baseline performance of acfs-enhanced vs vanilla Claude Code using industry-standard SWE-bench Lite.
**Primary Metric**: Task success rate (% of 300 GitHub issues resolved correctly)
**Timeline**: Baseline measurement → Incremental tool testing

---

## Phase 1: Baseline Measurement

### Objective
Quantify the performance impact of current acfs-enhanced features (PRIME templates, heartbeat monitoring, atomic work claiming) against vanilla Claude Code.

### Test Configurations

#### Config A: Vanilla Claude Code
- **Description**: Stock Claude Code CLI with no modifications
- **Features**: None (baseline)
- **Agent spawn**: Single agent per task
- **Memory**: No cross-session memory
- **Coordination**: None

#### Config B: acfs-enhanced (Current State)
- **Description**: Current acfs-enhanced with PRIME injection
- **Features**:
  - PRIME.md template injection at session start
  - Heartbeat monitoring (15-second intervals)
  - Atomic work claiming via `.bd_work_claimed`
  - Brand voice enforcement
  - Pre-compaction PRIME re-injection
- **Agent spawn**: NTM-based spawning with work item claiming
- **Memory**: PRIME templates provide context
- **Coordination**: File-based claim/release mechanism

### Success Criteria
- **Pass**: Agent produces code that passes all test cases in the SWE-bench issue
- **Fail**: Code fails tests, doesn't compile, or agent gets stuck/times out
- **Partial**: Agent makes progress but doesn't fully resolve issue

---

## SWE-bench Lite Setup

### Prerequisites
```bash
# Install SWE-bench
git clone https://github.com/princeton-nlp/SWE-bench.git
cd SWE-bench
pip install -e .

# Download Lite dataset (300 tasks)
python -m swebench.harness.get_tasks_pipeline \
  --instances_path gold \
  --split lite \
  --output_dir ./tasks
```

### Dataset Characteristics
- **Size**: 300 verified GitHub issues
- **Sources**: Django, Flask, matplotlib, requests, scikit-learn, etc.
- **Difficulty**: Pre-filtered for solvability (human-verified solutions exist)
- **Runtime**: ~30-45 minutes per full run (300 tasks)

### Test Harness Integration

#### Option 1: Official SWE-bench Harness
```bash
# Run with vanilla Claude Code
python -m swebench.harness.run_evaluation \
  --model "claude-sonnet-4-5" \
  --agent_type "vanilla_claude_code" \
  --instances_path ./tasks/lite.jsonl \
  --output_dir ./results/vanilla \
  --max_workers 1

# Run with acfs-enhanced
python -m swebench.harness.run_evaluation \
  --model "claude-sonnet-4-5" \
  --agent_type "acfs_enhanced" \
  --instances_path ./tasks/lite.jsonl \
  --output_dir ./results/acfs_enhanced \
  --max_workers 1
```

#### Option 2: Custom Test Runner (Recommended)
Create `benchmark/run_swebench.py` that:
1. Spins up agent with specified config (vanilla or acfs-enhanced)
2. Provides issue description + repo context
3. Captures agent output (code changes)
4. Runs test harness to verify solution
5. Logs results to structured format

**Advantages**:
- Direct control over PRIME injection timing
- Better observability (log agent messages, tool calls)
- Custom metrics (time-to-first-edit, number of retries, etc.)
- Easier to add secondary metrics later

---

## Execution Plan

### Step 1: Environment Setup
- [ ] Clone SWE-bench repo
- [ ] Download Lite dataset (300 tasks)
- [ ] Verify Docker environment (required for isolated test execution)
- [ ] Create test runner script (`benchmark/run_swebench.py`)
- [ ] Set up logging infrastructure (save agent transcripts, metrics)

### Step 2: Sample Run (10 tasks)
Before running full 300-task suite, validate setup with 10 representative tasks:
```bash
python benchmark/run_swebench.py \
  --config vanilla \
  --sample 10 \
  --output ./results/sample_vanilla

python benchmark/run_swebench.py \
  --config acfs_enhanced \
  --sample 10 \
  --output ./results/sample_acfs
```

**Why**: Catch configuration issues early, estimate full runtime, verify logging works.

### Step 3: Full Baseline Run
```bash
# Vanilla Claude Code (Control)
python benchmark/run_swebench.py \
  --config vanilla \
  --instances ./tasks/lite.jsonl \
  --output ./results/baseline_vanilla \
  --timeout 600  # 10 min per task

# acfs-enhanced (Test)
python benchmark/run_swebench.py \
  --config acfs_enhanced \
  --instances ./tasks/lite.jsonl \
  --output ./results/baseline_acfs \
  --timeout 600
```

**Estimated Time**: 2-4 hours per config (parallel execution possible if resources allow)

### Step 4: Results Analysis
Generate comparative report:
```bash
python benchmark/analyze_results.py \
  --vanilla ./results/baseline_vanilla \
  --acfs ./results/baseline_acfs \
  --output ./results/baseline_comparison.md
```

---

## Metrics Collection

### Primary Metric: Task Success Rate
```
Success Rate = (Resolved Tasks / Total Tasks) × 100
```

**Per-Config Breakdown**:
- Total tasks: 300
- Resolved: X
- Failed: Y
- Timeout: Z
- Success rate: (X / 300) × 100%

### Secondary Metrics (Nice-to-Have)
Track these for deeper insights, but don't optimize for them in Phase 1:
- **Time-to-resolution**: Median time from task start to passing tests
- **Retries**: Number of times agent re-attempts after test failure
- **Tool usage**: Edit/Read/Bash calls per task
- **Context efficiency**: Tokens used per task

### Statistical Significance
- **Minimum detectable difference**: 5% (e.g., 45% → 50%)
- **Confidence level**: 95%
- With 300 tasks, a 5% difference is statistically significant (p < 0.05)

---

## Expected Outcomes

### Hypothesis
acfs-enhanced will outperform vanilla Claude Code on tasks requiring:
1. **Consistency**: PRIME templates enforce best practices (proper error handling, testing, etc.)
2. **Context awareness**: Pre-compaction re-injection maintains focus during long sessions
3. **Workflow discipline**: Atomic claiming prevents redundant work (relevant when scaling to multi-agent)

### Baseline Performance Targets
Based on current Claude Code benchmarks and SWE-bench leaderboards:

| Config         | Expected Success Rate | Rationale                                           |
|----------------|-----------------------|-----------------------------------------------------|
| Vanilla        | 35-45%                | Sonnet 4.5 baseline (no workflow optimizations)     |
| acfs-enhanced  | 40-50%                | +5-10% from PRIME templates + consistency           |

**If acfs-enhanced < vanilla**: Indicates PRIME overhead hurts more than it helps → Need to refine templates
**If acfs-enhanced ≈ vanilla**: Current features don't impact single-agent performance → Focus on multi-agent coordination tools
**If acfs-enhanced > vanilla**: Validates approach → Proceed to Phase 2 (incremental tool testing)

---

## Phase 2: Incremental Tool Testing (Future)

Once baseline is established, test impact of additional tools:

### Test Sequence
1. **Baseline** (Phase 1): acfs-enhanced vs vanilla
2. **+mcp_agent_mail**: Add agent messaging & file reservations
3. **+CASS memory**: Add cross-session memory system
4. **+beads_triage**: Add AI-powered task prioritization
5. **+process_triage**: Replace heartbeat timeouts with Bayesian stuck detection

### Evaluation Strategy
Run SWE-bench Lite after each tool addition:
- Measure Δ success rate vs baseline
- Track cost increase (API tokens)
- Calculate ROI: (Δ success rate) / (Δ cost)

### Multi-Agent Scenarios (Phase 2b)
SWE-bench Lite measures single-agent performance. For multi-agent coordination:
- Create custom test suite with concurrent work items
- Measure: file conflicts avoided, messaging overhead, memory hit rate
- Example tasks: "Fix bug while Agent B adds feature" (tests file reservations)

---

## Implementation Checklist

### Phase 1: Baseline
- [ ] Set up SWE-bench Lite environment
- [ ] Create test runner script
- [ ] Run 10-task sample validation
- [ ] Execute full 300-task baseline (vanilla)
- [ ] Execute full 300-task baseline (acfs-enhanced)
- [ ] Generate comparison report
- [ ] Document findings in `BENCHMARK_RESULTS.md`

### Success Criteria for Phase 1 Completion
- ✅ Both configs successfully complete 300 tasks
- ✅ Results are reproducible (re-run shows <2% variance)
- ✅ Statistical significance confirmed (p < 0.05)
- ✅ Clear recommendation: Proceed to Phase 2 or refine PRIME templates

---

## Risk Mitigation

### Risk: Docker Environment Issues
SWE-bench requires Docker for isolated test execution.
**Mitigation**: Test Docker setup in Step 2 (sample run) before full baseline.

### Risk: Agent Timeouts Skew Results
10-minute timeout may be too short/long for some tasks.
**Mitigation**: Analyze timeout distribution in sample run, adjust if needed.

### Risk: Cost Overruns
300 tasks × 2 configs × ~500K tokens/task = ~300M tokens (~$900 at Sonnet 4.5 pricing).
**Mitigation**: Start with 10-task sample, extrapolate costs before full run.

### Risk: Non-Deterministic Results
Agent behavior may vary between runs due to model stochasticity.
**Mitigation**: Run each config 3 times, report mean + std deviation.

---

## Next Steps After Phase 1

1. **If acfs-enhanced wins**: Document improvements, proceed to Phase 2 (tool testing)
2. **If vanilla wins**: Refine PRIME templates, re-run baseline
3. **If inconclusive**: Increase sample size or add secondary metrics

**Target Date for Phase 1 Completion**: [To be determined based on resource availability]

---

## References

- [SWE-bench Paper](https://arxiv.org/abs/2310.06770)
- [SWE-bench GitHub](https://github.com/princeton-nlp/SWE-bench)
- [SWE-bench Leaderboard](https://www.swebench.com/)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)

---

## Appendix: Test Runner Skeleton

```python
# benchmark/run_swebench.py
import json
import subprocess
from pathlib import Path

def run_task(task: dict, config: str, timeout: int = 600):
    """
    Run single SWE-bench task with specified config.

    Args:
        task: SWE-bench task dict (repo, issue, test_patch, etc.)
        config: "vanilla" or "acfs_enhanced"
        timeout: Max seconds per task

    Returns:
        dict: {
            "instance_id": str,
            "resolved": bool,
            "time_seconds": float,
            "error": str | None
        }
    """
    # 1. Clone repo + checkout base commit
    # 2. Apply task environment (install dependencies)
    # 3. Spawn agent with config
    # 4. Wait for agent to produce code changes
    # 5. Apply test patch
    # 6. Run tests
    # 7. Return results
    pass

def main():
    # Parse CLI args
    # Load task instances
    # Run tasks sequentially or in parallel
    # Save results to JSON
    pass

if __name__ == "__main__":
    main()
```
