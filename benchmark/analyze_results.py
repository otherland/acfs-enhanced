#!/usr/bin/env python3
"""
Results Analysis Script for SWE-bench Benchmark
Compares vanilla Claude Code vs acfs-enhanced performance.
"""

import argparse
import json
import statistics
from pathlib import Path
from typing import List, Dict

from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown


console = Console()


def load_results(results_file: Path) -> List[Dict]:
    """Load results from JSONL file."""
    results = []
    with open(results_file) as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    return results


def load_summary(summary_file: Path) -> Dict:
    """Load summary JSON."""
    with open(summary_file) as f:
        return json.load(f)


def calculate_statistics(results: List[Dict]) -> Dict:
    """Calculate detailed statistics from results."""
    resolved = [r for r in results if r["resolved"]]
    failed = [r for r in results if not r["resolved"] and not r.get("error")]
    errors = [r for r in results if r.get("error")]

    times = [r["time_seconds"] for r in results if r["time_seconds"] > 0]

    stats = {
        "total": len(results),
        "resolved": len(resolved),
        "failed": len(failed),
        "errors": len(errors),
        "success_rate": len(resolved) / len(results) * 100 if results else 0,
        "avg_time": statistics.mean(times) if times else 0,
        "median_time": statistics.median(times) if times else 0,
        "std_time": statistics.stdev(times) if len(times) > 1 else 0,
        "min_time": min(times) if times else 0,
        "max_time": max(times) if times else 0,
    }

    return stats


def compare_configs(vanilla_results: List[Dict], acfs_results: List[Dict]) -> Dict:
    """Compare two configurations."""
    vanilla_stats = calculate_statistics(vanilla_results)
    acfs_stats = calculate_statistics(acfs_results)

    comparison = {
        "vanilla": vanilla_stats,
        "acfs_enhanced": acfs_stats,
        "delta": {
            "success_rate": acfs_stats["success_rate"] - vanilla_stats["success_rate"],
            "avg_time": acfs_stats["avg_time"] - vanilla_stats["avg_time"],
            "resolved_count": acfs_stats["resolved"] - vanilla_stats["resolved"],
        }
    }

    return comparison


def calculate_significance(vanilla_results: List[Dict], acfs_results: List[Dict]) -> Dict:
    """Calculate statistical significance using simple z-test for proportions."""
    n1 = len(vanilla_results)
    n2 = len(acfs_results)

    p1 = sum(1 for r in vanilla_results if r["resolved"]) / n1
    p2 = sum(1 for r in acfs_results if r["resolved"]) / n2

    # Pooled proportion
    p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)

    # Standard error
    se = (p_pool * (1 - p_pool) * (1/n1 + 1/n2)) ** 0.5

    # Z-score
    z = (p2 - p1) / se if se > 0 else 0

    # Approximate p-value (two-tailed)
    # For simplicity, using z-score thresholds
    # z > 1.96 ≈ p < 0.05 (95% confidence)
    # z > 2.576 ≈ p < 0.01 (99% confidence)

    if abs(z) > 2.576:
        significance = "***"  # p < 0.01
        significant = True
    elif abs(z) > 1.96:
        significance = "**"   # p < 0.05
        significant = True
    elif abs(z) > 1.645:
        significance = "*"    # p < 0.10
        significant = False
    else:
        significance = "ns"   # not significant
        significant = False

    return {
        "z_score": z,
        "significance": significance,
        "is_significant": significant,
        "p1": p1,
        "p2": p2
    }


def print_comparison_table(comparison: Dict, significance: Dict):
    """Print comparison table."""
    table = Table(title="Benchmark Comparison: vanilla vs acfs-enhanced", show_header=True)

    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Vanilla", style="yellow", justify="right")
    table.add_column("acfs-enhanced", style="green", justify="right")
    table.add_column("Delta", style="magenta", justify="right")

    vanilla = comparison["vanilla"]
    acfs = comparison["acfs_enhanced"]
    delta = comparison["delta"]

    # Success rate
    table.add_row(
        "Success Rate",
        f"{vanilla['success_rate']:.1f}%",
        f"{acfs['success_rate']:.1f}%",
        f"{delta['success_rate']:+.1f}%"
    )

    # Resolved count
    table.add_row(
        "Tasks Resolved",
        f"{vanilla['resolved']}/{vanilla['total']}",
        f"{acfs['resolved']}/{acfs['total']}",
        f"{delta['resolved_count']:+d}"
    )

    # Avg time
    table.add_row(
        "Avg Time (s)",
        f"{vanilla['avg_time']:.1f}",
        f"{acfs['avg_time']:.1f}",
        f"{delta['avg_time']:+.1f}"
    )

    # Median time
    table.add_row(
        "Median Time (s)",
        f"{vanilla['median_time']:.1f}",
        f"{acfs['median_time']:.1f}",
        f"{acfs['median_time'] - vanilla['median_time']:+.1f}"
    )

    console.print(table)

    # Statistical significance
    console.print(f"\n[bold]Statistical Significance:[/bold]")
    console.print(f"Z-score: {significance['z_score']:.3f}")
    console.print(f"Significance: {significance['significance']}")

    if significance['is_significant']:
        console.print(f"[green]✓ Difference is statistically significant (p < 0.05)[/green]")
    else:
        console.print(f"[yellow]⚠ Difference is not statistically significant[/yellow]")


def generate_markdown_report(
    comparison: Dict,
    significance: Dict,
    output_file: Path
):
    """Generate markdown report."""
    vanilla = comparison["vanilla"]
    acfs = comparison["acfs_enhanced"]
    delta = comparison["delta"]

    report = f"""# SWE-bench Benchmark Results

**Date:** {Path(output_file).parent.name}

## Summary

Comparison of vanilla Claude Code vs acfs-enhanced on SWE-bench Lite (300 tasks).

## Results

| Metric | Vanilla | acfs-enhanced | Delta |
|--------|---------|---------------|-------|
| **Success Rate** | {vanilla['success_rate']:.1f}% | {acfs['success_rate']:.1f}% | **{delta['success_rate']:+.1f}%** {significance['significance']} |
| Tasks Resolved | {vanilla['resolved']}/{vanilla['total']} | {acfs['resolved']}/{acfs['total']} | {delta['resolved_count']:+d} |
| Avg Time (s) | {vanilla['avg_time']:.1f} | {acfs['avg_time']:.1f} | {delta['avg_time']:+.1f} |
| Median Time (s) | {vanilla['median_time']:.1f} | {acfs['median_time']:.1f} | {acfs['median_time'] - vanilla['median_time']:+.1f} |

## Statistical Analysis

- **Z-score:** {significance['z_score']:.3f}
- **Significance:** {significance['significance']}
- **Result:** {"Statistically significant difference (p < 0.05)" if significance['is_significant'] else "Not statistically significant"}

## Interpretation

### Success Rate
{"**Winner: acfs-enhanced**" if delta['success_rate'] > 0 else "**Winner: vanilla**" if delta['success_rate'] < 0 else "**Tie**"}

acfs-enhanced {'outperformed' if delta['success_rate'] > 0 else 'underperformed' if delta['success_rate'] < 0 else 'matched'} vanilla by {abs(delta['success_rate']):.1f} percentage points.

- Vanilla: {vanilla['resolved']} tasks resolved ({vanilla['success_rate']:.1f}%)
- acfs-enhanced: {acfs['resolved']} tasks resolved ({acfs['success_rate']:.1f}%)

### Performance
{"acfs-enhanced was faster" if delta['avg_time'] < 0 else "vanilla was faster" if delta['avg_time'] > 0 else "Similar performance"} on average by {abs(delta['avg_time']):.1f} seconds per task.

## Detailed Statistics

### Vanilla
- Total tasks: {vanilla['total']}
- Resolved: {vanilla['resolved']}
- Failed: {vanilla['failed']}
- Errors: {vanilla['errors']}
- Time range: {vanilla['min_time']:.1f}s - {vanilla['max_time']:.1f}s
- Std deviation: {vanilla['std_time']:.1f}s

### acfs-enhanced
- Total tasks: {acfs['total']}
- Resolved: {acfs['resolved']}
- Failed: {acfs['failed']}
- Errors: {acfs['errors']}
- Time range: {acfs['min_time']:.1f}s - {acfs['max_time']:.1f}s
- Std deviation: {acfs['std_time']:.1f}s

## Conclusion

"""

    if significance['is_significant'] and delta['success_rate'] > 0:
        report += f"""✅ **acfs-enhanced shows statistically significant improvement** over vanilla Claude Code.

The {delta['success_rate']:.1f}% improvement in success rate is meaningful and validates the value of PRIME templates and workflow optimizations.

**Recommendation:** Proceed to Phase 2 (incremental tool testing) to evaluate impact of additional tools like mcp_agent_mail, CASS, and beads_triage.
"""
    elif significance['is_significant'] and delta['success_rate'] < 0:
        report += f"""❌ **vanilla outperformed acfs-enhanced** by a statistically significant margin.

This suggests that current PRIME templates or workflow optimizations may be introducing overhead or constraints that hurt performance.

**Recommendation:** Refine PRIME templates and re-run baseline before proceeding to Phase 2.
"""
    else:
        report += f"""⚠️ **No statistically significant difference** between configurations.

The {abs(delta['success_rate']):.1f}% difference could be due to random variation.

**Recommendation:**
- If acfs-enhanced ≈ vanilla: Current features don't impact single-agent performance. Focus on multi-agent coordination features (Phase 2).
- Consider increasing sample size or running multiple iterations for more confidence.
"""

    with open(output_file, "w") as f:
        f.write(report)

    console.print(f"\n[green]Report saved to: {output_file}[/green]")


def main():
    parser = argparse.ArgumentParser(description="Analyze SWE-bench benchmark results")
    parser.add_argument(
        "--vanilla",
        type=Path,
        required=True,
        help="Path to vanilla results directory"
    )
    parser.add_argument(
        "--acfs",
        type=Path,
        required=True,
        help="Path to acfs-enhanced results directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmark_comparison.md"),
        help="Output file for report (default: benchmark_comparison.md)"
    )

    args = parser.parse_args()

    # Load results
    console.print("[cyan]Loading results...[/cyan]")

    vanilla_results = load_results(args.vanilla / "results.jsonl")
    acfs_results = load_results(args.acfs / "results.jsonl")

    console.print(f"Loaded {len(vanilla_results)} vanilla results")
    console.print(f"Loaded {len(acfs_results)} acfs-enhanced results")

    # Compare
    comparison = compare_configs(vanilla_results, acfs_results)
    significance = calculate_significance(vanilla_results, acfs_results)

    # Print table
    print_comparison_table(comparison, significance)

    # Generate report
    generate_markdown_report(comparison, significance, args.output)

    console.print("\n[bold green]Analysis complete![/bold green]")


if __name__ == "__main__":
    main()
