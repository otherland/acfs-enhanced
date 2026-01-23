# ACFS Benchmark System

Measure acfs-enhanced performance improvements using SWE-bench Lite tasks.

**Two approaches:**
1. **Manual Testing** (Recommended) - Solve tasks yourself with CASS logging
2. **Automated Testing** (Future) - Fully automated agent evaluation

## Manual Testing (Recommended)

**Best for:** Getting real data quickly, understanding what actually helps

See **[QUICKSTART.md](QUICKSTART.md)** and **[MANUAL_TESTING.md](MANUAL_TESTING.md)** for complete guide.

### Quick Start (Manual)

```bash
# 1. Select test tasks
python select_tasks.py

# 2. Test one task (vanilla vs acfs-enhanced)
# Follow QUICKSTART.md

# 3. After testing 14 tasks, analyze results
python analyze_manual_results.py \
  --scorecard results/scorecard.csv \
  --output results/report.md
```

**Time:** 1-2 days for baseline (14 tasks × 2 configs)
**Cost:** Free (uses your Claude Code subscription)
**Value:** Real feedback on what helps/hurts

---

## Automated Testing (Future)

**Note:** The automated runner (below) is infrastructure for future use. Not needed for manual baseline.

### 1. Setup

```bash
# Install dependencies
./scripts/setup.sh

# Activate environment
source venv/bin/activate
```

### 2. Run Sample Benchmark (10 tasks, ~5-10 minutes)

```bash
./scripts/run_sample.sh
```

This will:
- Run 10 SWE-bench Lite tasks with vanilla Claude Code
- Run same 10 tasks with acfs-enhanced
- Generate comparison report

### 3. View Results

```bash
cat results/sample_comparison.md
```

## Directory Structure

```
benchmark/
├── README.md                  # This file
├── run_swebench.py           # Main test runner
├── analyze_results.py        # Results analysis script
├── venv/                     # Python virtual environment
├── swe-bench/                # SWE-bench repository (cloned)
├── configs/                  # Agent configurations
│   ├── vanilla.json         # Baseline config
│   └── acfs_enhanced.json   # acfs-enhanced config
├── scripts/                  # Helper scripts
│   ├── setup.sh             # Environment setup
│   ├── run_sample.sh        # Run 10-task sample
│   └── run_full.sh          # Run full 300-task benchmark
└── results/                  # Benchmark results
    ├── sample_vanilla/      # Vanilla results
    ├── sample_acfs/         # acfs-enhanced results
    └── sample_comparison.md # Comparison report
```

## Usage

### Running Custom Benchmarks

```bash
# Run with specific config and sample size
python run_swebench.py \
  --config vanilla \
  --sample 20 \
  --output results/test_vanilla \
  --timeout 300

# Run full benchmark (300 tasks)
python run_swebench.py \
  --config acfs_enhanced \
  --output results/full_acfs \
  --timeout 600
```

### Analyzing Results

```bash
python analyze_results.py \
  --vanilla results/sample_vanilla \
  --acfs results/sample_acfs \
  --output comparison.md
```

### Full Benchmark (WARNING: Expensive!)

```bash
./scripts/run_full.sh
```

**Cost estimate:**
- **300 tasks** × 2 configs × ~500K tokens/task = ~300M tokens
- **~$900** at Sonnet 4.5 pricing ($3/MTok input)
- **2-4 hours** runtime

## Configurations

### Vanilla Claude Code

- Stock Claude Code CLI with no modifications
- No PRIME templates
- No workflow optimizations
- **Purpose:** Baseline for comparison

### acfs-enhanced

- PRIME template injection at session start
- Heartbeat monitoring
- Atomic work claiming
- Brand voice enforcement
- **Purpose:** Measure impact of workflow optimizations

## Understanding Results

### Success Rate

Primary metric: Percentage of tasks where agent produces code that passes all tests.

Example:
- Vanilla: 42.3% (127/300 resolved)
- acfs-enhanced: 47.7% (143/300 resolved)
- **Delta: +5.4%** (16 more tasks resolved)

### Statistical Significance

We calculate a z-score to determine if differences are meaningful:

- ***** p < 0.01 (99% confidence) - Highly significant
- **** p < 0.05 (95% confidence) - Significant
- * p < 0.10 (90% confidence) - Marginally significant
- **ns** Not significant - Could be random variation

### Time Metrics

- **Avg Time:** Mean time to complete task
- **Median Time:** 50th percentile (less affected by outliers)
- **Std Dev:** Variability in completion times

## Interpreting Results

### If acfs-enhanced wins significantly (+5% or more, p < 0.05):

✅ **Success!** PRIME templates and workflow optimizations provide measurable value.

**Next steps:**
1. Document which features contributed most
2. Proceed to Phase 2: Test additional tools (mcp_agent_mail, CASS, etc.)
3. Optimize PRIME templates based on failure analysis

### If vanilla wins:

❌ **Refinement needed.** Current optimizations may add overhead.

**Next steps:**
1. Analyze failure modes in transcripts
2. Simplify PRIME templates
3. Test minimal PRIME vs full PRIME
4. Re-run baseline

### If results are similar (< 2% difference):

⚠️ **Inconclusive.** Features don't impact single-agent performance.

**Next steps:**
1. Focus on multi-agent coordination benefits (not captured by SWE-bench)
2. Create custom benchmarks for multi-agent scenarios
3. Test features that target coordination (mcp_agent_mail, beads_triage)

## Example Results

### Sample Output (10 tasks)

```
Benchmark Comparison: vanilla vs acfs-enhanced

┌─────────────────────┬─────────┬───────────────┬──────────┐
│ Metric              │ Vanilla │ acfs-enhanced │ Delta    │
├─────────────────────┼─────────┼───────────────┼──────────┤
│ Success Rate        │   40.0% │         50.0% │   +10.0% │
│ Tasks Resolved      │    4/10 │          5/10 │       +1 │
│ Avg Time (s)        │   287.3 │         301.2 │   +13.9  │
│ Median Time (s)     │   265.0 │         289.0 │   +24.0  │
└─────────────────────┴─────────┴───────────────┴──────────┘

Statistical Significance:
Z-score: 0.632
Significance: ns

⚠ Difference is not statistically significant
(Sample size too small - run full benchmark for significance)
```

## SWE-bench Lite Details

- **Size:** 300 verified GitHub issues
- **Sources:** Django, Flask, matplotlib, requests, scikit-learn, etc.
- **Difficulty:** Pre-filtered for solvability (human-verified)
- **Format:** Each task includes:
  - Repository URL
  - Base commit
  - Problem statement (issue description)
  - Test patch (verification tests)
  - Expected solution

## Requirements

- **Python:** 3.10+
- **Docker:** Required for isolated test execution
- **Disk:** ~10GB for repos and Docker images
- **API Keys:** Anthropic API key in environment (`ANTHROPIC_API_KEY`)

## Troubleshooting

### Docker Permission Issues

```bash
# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Out of Memory

SWE-bench clones many repos. If running out of disk:

```bash
# Clean up Docker
docker system prune -a

# Clean up temp directories
rm -rf /tmp/swebench_*
```

### Agent Timeouts

If agents frequently timeout, increase the timeout:

```bash
python run_swebench.py --timeout 900  # 15 minutes
```

## Advanced Usage

### Testing Tool Integrations (Phase 2)

After establishing baseline, test incremental tool additions:

1. **Baseline:** acfs-enhanced
2. **+mcp_agent_mail:** Add agent messaging
3. **+CASS:** Add cross-session memory
4. **+beads_triage:** Add AI-powered prioritization

```bash
# Create new config: acfs_plus_agent_mail.json
python run_swebench.py --config acfs_plus_agent_mail --output results/with_agent_mail

# Compare
python analyze_results.py \
  --vanilla results/baseline_acfs \
  --acfs results/with_agent_mail \
  --output phase2_agent_mail_impact.md
```

### Custom Datasets

Test on different subsets:

```python
# In run_swebench.py, modify dataset loading:
dataset = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")

# Filter by repo
python_tasks = [t for t in dataset if "python" in t["repo"].lower()]
```

## References

- [SWE-bench Paper](https://arxiv.org/abs/2310.06770)
- [SWE-bench GitHub](https://github.com/princeton-nlp/SWE-bench)
- [SWE-bench Leaderboard](https://www.swebench.com/)
- [Benchmark Plan](../docs/BENCHMARK_PLAN.md)

## License

MIT - Same as acfs-enhanced

---

**Pro tip:** Start with sample benchmarks (10 tasks) to validate setup before committing to expensive full runs!
