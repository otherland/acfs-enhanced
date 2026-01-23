#!/usr/bin/env python3
"""
Select representative tasks from SWE-bench Lite for manual testing.

Picks 10-20 tasks that are:
- Diverse across repositories
- Varied in complexity
- Clear success criteria
- Reasonable to solve manually (<30 min each)
"""

import json
from collections import defaultdict
from pathlib import Path

from datasets import load_dataset
from rich.console import Console
from rich.table import Table

console = Console()


def analyze_tasks(dataset):
    """Analyze task distribution across repos and problem types."""
    repo_counts = defaultdict(int)

    for task in dataset:
        repo = task['repo'].split('/')[-1]  # Get repo name without org
        repo_counts[repo] += 1

    return repo_counts


def select_representative_tasks(dataset, num_tasks=15):
    """
    Select diverse, representative tasks.

    Strategy:
    - Pick 2-3 tasks per popular repo
    - Ensure variety in problem types
    - Prefer tasks with clear, focused issues
    """

    # Group by repo
    tasks_by_repo = defaultdict(list)
    for task in dataset:
        repo = task['repo']
        tasks_by_repo[repo].append(task)

    # Sort repos by popularity (number of tasks)
    popular_repos = sorted(tasks_by_repo.items(), key=lambda x: len(x[1]), reverse=True)

    selected = []
    tasks_per_repo = max(2, num_tasks // len(popular_repos[:7]))  # Target 7 different repos

    # Select from top repos
    for repo, tasks in popular_repos[:7]:
        # Take first N tasks from each repo
        selected.extend(tasks[:tasks_per_repo])

        if len(selected) >= num_tasks:
            break

    return selected[:num_tasks]


def save_task_list(tasks, output_file):
    """Save selected tasks to JSON."""
    task_data = []

    for i, task in enumerate(tasks, 1):
        task_data.append({
            "task_id": f"TASK-{i:02d}",
            "instance_id": task["instance_id"],
            "repo": task["repo"],
            "problem_statement": task["problem_statement"][:200] + "..." if len(task["problem_statement"]) > 200 else task["problem_statement"],
            "full_problem": task["problem_statement"],
            "base_commit": task["base_commit"],
            "test_patch": task["test_patch"],
            "hints_text": task.get("hints_text", ""),
        })

    with open(output_file, "w") as f:
        json.dump(task_data, f, indent=2)

    console.print(f"[green]✓ Saved {len(tasks)} tasks to {output_file}[/green]")


def print_task_summary(tasks):
    """Print summary table of selected tasks."""
    table = Table(title="Selected SWE-bench Tasks for Manual Testing")

    table.add_column("ID", style="cyan", width=8)
    table.add_column("Repository", style="yellow", width=20)
    table.add_column("Instance ID", style="green", width=30)
    table.add_column("Problem Preview", style="white", width=50)

    for i, task in enumerate(tasks, 1):
        repo_name = task["repo"].split('/')[-1]
        problem_preview = task["problem_statement"][:80] + "..." if len(task["problem_statement"]) > 80 else task["problem_statement"]

        table.add_row(
            f"TASK-{i:02d}",
            repo_name,
            task["instance_id"],
            problem_preview
        )

    console.print(table)

    # Repo distribution
    console.print("\n[bold cyan]Repository Distribution:[/bold cyan]")
    repo_counts = defaultdict(int)
    for task in tasks:
        repo_counts[task["repo"]] += 1

    for repo, count in sorted(repo_counts.items(), key=lambda x: x[1], reverse=True):
        console.print(f"  {repo}: {count} tasks")


def main():
    console.print("[cyan]Loading SWE-bench Lite dataset...[/cyan]")
    dataset = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")

    console.print(f"Total tasks available: {len(dataset)}\n")

    # Analyze distribution
    console.print("[cyan]Analyzing task distribution...[/cyan]")
    repo_counts = analyze_tasks(dataset)

    console.print(f"Tasks span {len(repo_counts)} repositories\n")
    console.print("Top repositories:")
    for repo, count in sorted(repo_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        console.print(f"  {repo}: {count} tasks")

    # Select representative tasks
    console.print("\n[cyan]Selecting 15 representative tasks...[/cyan]\n")
    selected_tasks = select_representative_tasks(dataset, num_tasks=15)

    # Print summary
    print_task_summary(selected_tasks)

    # Save to file
    output_file = Path(__file__).parent / "manual_test_tasks.json"
    save_task_list(selected_tasks, output_file)

    console.print("\n[bold green]✓ Task selection complete![/bold green]")
    console.print(f"\nNext steps:")
    console.print(f"1. Review tasks: cat {output_file}")
    console.print(f"2. Start testing: see benchmark/MANUAL_TESTING.md")


if __name__ == "__main__":
    main()
