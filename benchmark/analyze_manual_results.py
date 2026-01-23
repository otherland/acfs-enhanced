#!/usr/bin/env python3
"""
Analyze manual benchmark results from scorecard and CASS transcripts.
"""

import argparse
import csv
import json
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def load_scorecard(scorecard_file):
    """Load results from scorecard CSV."""
    results = defaultdict(list)

    with open(scorecard_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['outcome']:  # Skip empty rows
                results[row['config']].append(row)

    return results


def calculate_metrics(results):
    """Calculate metrics for a configuration."""
    total = len(results)
    if total == 0:
        return {}

    passed = sum(1 for r in results if r['outcome'] == 'PASS')
    failed = sum(1 for r in results if r['outcome'] == 'FAIL')
    timeout = sum(1 for r in results if r['outcome'] == 'TIMEOUT')

    times = [float(r['time_seconds']) for r in results if r['time_seconds'] and r['outcome'] == 'PASS']

    metrics = {
        'total': total,
        'passed': passed,
        'failed': failed,
        'timeout': timeout,
        'success_rate': (passed / total * 100) if total > 0 else 0,
        'avg_time': statistics.mean(times) if times else 0,
        'median_time': statistics.median(times) if times else 0,
        'std_time': statistics.stdev(times) if len(times) > 1 else 0,
        'min_time': min(times) if times else 0,
        'max_time': max(times) if times else 0,
    }

    return metrics


def print_comparison(results):
    """Print comparison table."""
    table = Table(title="Manual Benchmark Results")

    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Vanilla", style="yellow", justify="right")
    table.add_column("acfs-enhanced", style="green", justify="right")
    table.add_column("Delta", style="magenta", justify="right")

    vanilla_metrics = calculate_metrics(results.get('vanilla', []))
    acfs_metrics = calculate_metrics(results.get('acfs', []))

    if not vanilla_metrics or not acfs_metrics:
        console.print("[red]Error: Missing data for vanilla or acfs configuration[/red]")
        return

    # Success rate
    table.add_row(
        "Success Rate",
        f"{vanilla_metrics['success_rate']:.1f}%",
        f"{acfs_metrics['success_rate']:.1f}%",
        f"{acfs_metrics['success_rate'] - vanilla_metrics['success_rate']:+.1f}%"
    )

    # Tasks
    table.add_row(
        "Tasks Passed",
        f"{vanilla_metrics['passed']}/{vanilla_metrics['total']}",
        f"{acfs_metrics['passed']}/{acfs_metrics['total']}",
        f"{acfs_metrics['passed'] - vanilla_metrics['passed']:+d}"
    )

    # Avg time
    table.add_row(
        "Avg Time (s)",
        f"{vanilla_metrics['avg_time']:.0f}",
        f"{acfs_metrics['avg_time']:.0f}",
        f"{acfs_metrics['avg_time'] - vanilla_metrics['avg_time']:+.0f}"
    )

    # Median time
    table.add_row(
        "Median Time (s)",
        f"{vanilla_metrics['median_time']:.0f}",
        f"{acfs_metrics['median_time']:.0f}",
        f"{acfs_metrics['median_time'] - vanilla_metrics['median_time']:+.0f}"
    )

    # Timeouts
    table.add_row(
        "Timeouts",
        f"{vanilla_metrics['timeout']}",
        f"{acfs_metrics['timeout']}",
        f"{acfs_metrics['timeout'] - vanilla_metrics['timeout']:+d}"
    )

    console.print(table)

    return vanilla_metrics, acfs_metrics


def analyze_transcripts(transcript_dir):
    """Analyze CASS transcripts for patterns."""
    if not transcript_dir or not Path(transcript_dir).exists():
        console.print("[yellow]Skipping transcript analysis (directory not found)[/yellow]")
        return {}

    transcript_dir = Path(transcript_dir)
    analysis = defaultdict(lambda: {'vanilla': [], 'acfs': []})

    for config in ['vanilla', 'acfs']:
        transcripts = list(transcript_dir.glob(f"*-{config}.json"))

        for transcript_file in transcripts:
            try:
                with open(transcript_file) as f:
                    data = json.load(f)

                # Count tool uses
                tool_uses = len([m for m in data if m.get('type') == 'tool_use'])
                analysis['tool_uses'][config].append(tool_uses)

                # Count errors
                errors = len([m for m in data if 'error' in str(m).lower()])
                analysis['errors'][config].append(errors)

                # Message count
                analysis['messages'][config].append(len(data))

            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse {transcript_file}: {e}[/yellow]")

    return analysis


def generate_markdown_report(results, vanilla_metrics, acfs_metrics, transcript_analysis, output_file):
    """Generate markdown report."""
    delta_success = acfs_metrics['success_rate'] - vanilla_metrics['success_rate']
    delta_time = acfs_metrics['avg_time'] - vanilla_metrics['avg_time']

    report = f"""# Manual Benchmark Results

**Test Date:** {Path().cwd()}
**Tasks Tested:** {vanilla_metrics['total']} SWE-bench Lite issues

## Summary

Manually solved {vanilla_metrics['total']} real GitHub issues using two configurations:
- **Vanilla**: Stock Claude Code, no templates
- **acfs-enhanced**: With PRIME templates and workflow guidance

## Key Findings

### Success Rate
- **Vanilla:** {vanilla_metrics['passed']}/{vanilla_metrics['total']} tasks ({vanilla_metrics['success_rate']:.1f}%)
- **acfs-enhanced:** {acfs_metrics['passed']}/{acfs_metrics['total']} tasks ({acfs_metrics['success_rate']:.1f}%)
- **Delta:** {delta_success:+.1f}% {'✅ IMPROVEMENT' if delta_success > 0 else '❌ REGRESSION' if delta_success < 0 else '⚠️ NO CHANGE'}

### Time to Solution
- **Vanilla avg:** {vanilla_metrics['avg_time']:.0f}s ({vanilla_metrics['avg_time']/60:.1f} min)
- **acfs-enhanced avg:** {acfs_metrics['avg_time']:.0f}s ({acfs_metrics['avg_time']/60:.1f} min)
- **Delta:** {delta_time:+.0f}s ({'faster' if delta_time < 0 else 'slower' if delta_time > 0 else 'same'})

### Timeouts (gave up after 30min)
- **Vanilla:** {vanilla_metrics['timeout']} tasks
- **acfs-enhanced:** {acfs_metrics['timeout']} tasks

## Detailed Comparison

| Metric | Vanilla | acfs-enhanced | Delta |
|--------|---------|---------------|-------|
| Success Rate | {vanilla_metrics['success_rate']:.1f}% | {acfs_metrics['success_rate']:.1f}% | **{delta_success:+.1f}%** |
| Tasks Passed | {vanilla_metrics['passed']}/{vanilla_metrics['total']} | {acfs_metrics['passed']}/{acfs_metrics['total']} | {acfs_metrics['passed'] - vanilla_metrics['passed']:+d} |
| Avg Time | {vanilla_metrics['avg_time']:.0f}s | {acfs_metrics['avg_time']:.0f}s | {delta_time:+.0f}s |
| Median Time | {vanilla_metrics['median_time']:.0f}s | {acfs_metrics['median_time']:.0f}s | {acfs_metrics['median_time'] - vanilla_metrics['median_time']:+.0f}s |
| Timeouts | {vanilla_metrics['timeout']} | {acfs_metrics['timeout']} | {acfs_metrics['timeout'] - vanilla_metrics['timeout']:+d} |

"""

    # Transcript analysis
    if transcript_analysis:
        report += f"""
## Transcript Analysis (from CASS logs)

"""
        for metric, values in transcript_analysis.items():
            if values['vanilla'] and values['acfs']:
                vanilla_avg = statistics.mean(values['vanilla'])
                acfs_avg = statistics.mean(values['acfs'])
                report += f"**{metric.replace('_', ' ').title()}:**\n"
                report += f"- Vanilla: {vanilla_avg:.1f} avg\n"
                report += f"- acfs-enhanced: {acfs_avg:.1f} avg\n"
                report += f"- Delta: {acfs_avg - vanilla_avg:+.1f}\n\n"

    # Interpretation
    report += f"""
## Interpretation

"""

    if delta_success > 5:
        report += f"""### ✅ acfs-enhanced Shows Clear Improvement

The {delta_success:.1f}% improvement in success rate indicates that PRIME templates and workflow guidance provide tangible value:

- **Better focus:** Templates kept work on-track
- **Fewer mistakes:** Structured approach reduces errors
- **More completions:** Fewer timeouts

**Recommendation:** Proceed to Phase 2 - test additional tools (mcp_agent_mail, CASS memory, beads_triage) to measure their incremental impact.

"""
    elif delta_success < -5:
        report += f"""### ❌ Vanilla Outperformed acfs-enhanced

The {abs(delta_success):.1f}% regression suggests PRIME templates may be adding overhead without benefit:

- Templates too verbose?
- Guidance too restrictive?
- Workflow doesn't match task types?

**Recommendation:** Refine PRIME templates:
1. Simplify: Remove unnecessary instructions
2. Focus: Target common failure modes
3. Test minimal PRIME vs full PRIME

"""
    else:
        report += f"""### ⚠️ Similar Performance

The {abs(delta_success):.1f}% difference is marginal. Could indicate:

- Templates don't impact single-session work
- Sample size too small to detect difference
- Tasks well-suited to both approaches

**Recommendation:**
- If time delta shows acfs is faster → Templates help with efficiency
- If quality is better with acfs → Focus on multi-agent coordination features
- Consider testing with harder tasks or larger sample

"""

    # Task-by-task breakdown
    report += """
## Task-by-Task Breakdown

| Task ID | Vanilla | acfs-enhanced | Winner |
|---------|---------|---------------|--------|
"""

    # Group by task
    task_results = defaultdict(lambda: {'vanilla': None, 'acfs': None})
    for config in ['vanilla', 'acfs']:
        for result in results.get(config, []):
            task_id = result['task_id']
            task_results[task_id][config] = result

    for task_id in sorted(task_results.keys()):
        v = task_results[task_id]['vanilla']
        a = task_results[task_id]['acfs']

        if v and a:
            v_outcome = v['outcome']
            a_outcome = a['outcome']

            if v_outcome == 'PASS' and a_outcome == 'FAIL':
                winner = 'Vanilla ✓'
            elif v_outcome == 'FAIL' and a_outcome == 'PASS':
                winner = 'acfs ✓'
            elif v_outcome == 'PASS' and a_outcome == 'PASS':
                # Both passed - compare time
                v_time = float(v['time_seconds']) if v['time_seconds'] else 9999
                a_time = float(a['time_seconds']) if a['time_seconds'] else 9999
                winner = f"acfs (faster)" if a_time < v_time else f"Vanilla (faster)" if v_time < a_time else "Tie"
            else:
                winner = "Both failed"

            report += f"| {task_id} | {v_outcome} | {a_outcome} | {winner} |\n"

    report += """
## Observations from Notes

"""

    # Extract notable observations
    for config in ['vanilla', 'acfs']:
        report += f"\n### {config.capitalize()} Patterns\n\n"
        for result in results.get(config, []):
            if result.get('notes'):
                report += f"- **{result['task_id']}:** {result['notes']}\n"

    report += """
## Next Steps

"""

    if delta_success > 5:
        report += """1. **Phase 2:** Test mcp_agent_mail integration
   - Solve same 14 tasks with agent messaging enabled
   - Measure impact on coordination (even in single-agent, file reservations prevent mistakes)

2. **Phase 3:** Add CASS memory
   - Enable cross-session learning
   - Measure if agents learn patterns across tasks

3. **Phase 4:** Multi-agent scenarios
   - Create tasks requiring concurrent work
   - Test full stack (PRIME + mail + CASS + triage)

"""
    else:
        report += """1. **Refine PRIME templates:**
   - Review failing tasks to identify issues
   - Simplify templates, remove overhead
   - Test minimal version

2. **Re-run baseline:**
   - Verify improvements
   - If still no benefit, reconsider approach

3. **Alternative hypotheses:**
   - Maybe PRIME helps multi-agent work but not single-agent?
   - Test coordination features (mail, reservations) directly

"""

    report += f"""
---

*Generated from manual testing on {vanilla_metrics['total']} SWE-bench Lite tasks*
*CASS transcripts available for detailed review*
"""

    with open(output_file, 'w') as f:
        f.write(report)

    console.print(f"\n[green]✓ Report saved to {output_file}[/green]")


def main():
    parser = argparse.ArgumentParser(description="Analyze manual benchmark results")
    parser.add_argument(
        '--scorecard',
        type=Path,
        required=True,
        help="Path to scorecard CSV"
    )
    parser.add_argument(
        '--transcripts',
        type=Path,
        help="Path to directory with CASS transcript exports (optional)"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('manual_benchmark_report.md'),
        help="Output markdown file"
    )

    args = parser.parse_args()

    # Load results
    console.print("[cyan]Loading scorecard...[/cyan]")
    results = load_scorecard(args.scorecard)

    console.print(f"Loaded {len(results['vanilla'])} vanilla results")
    console.print(f"Loaded {len(results['acfs'])} acfs results\n")

    # Print comparison
    vanilla_metrics, acfs_metrics = print_comparison(results)

    # Analyze transcripts
    console.print("\n[cyan]Analyzing CASS transcripts...[/cyan]")
    transcript_analysis = analyze_transcripts(args.transcripts)

    # Generate report
    console.print("\n[cyan]Generating report...[/cyan]")
    generate_markdown_report(
        results,
        vanilla_metrics,
        acfs_metrics,
        transcript_analysis,
        args.output
    )

    console.print("\n[bold green]✓ Analysis complete![/bold green]")


if __name__ == "__main__":
    main()
