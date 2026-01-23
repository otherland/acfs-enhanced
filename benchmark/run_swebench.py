#!/usr/bin/env python3
"""
SWE-bench Test Runner for ACFS Benchmark
Evaluates vanilla Claude Code vs acfs-enhanced on SWE-bench Lite tasks.
"""

import argparse
import json
import logging
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import docker
from datasets import load_dataset
from git import Repo
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Setup
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('benchmark.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Result of running a single SWE-bench task."""
    instance_id: str
    config: str
    resolved: bool
    time_seconds: float
    error: Optional[str] = None
    agent_transcript: Optional[str] = None
    patch_applied: bool = False
    tests_passed: int = 0
    tests_failed: int = 0

    def to_dict(self):
        return asdict(self)


class SWEBenchRunner:
    """Runs SWE-bench evaluation with different agent configurations."""

    def __init__(self, config: str, output_dir: Path, timeout: int = 600):
        self.config = config
        self.output_dir = Path(output_dir)
        self.timeout = timeout
        self.docker_client = docker.from_env()

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_file = self.output_dir / "results.jsonl"
        self.transcripts_dir = self.output_dir / "transcripts"
        self.transcripts_dir.mkdir(exist_ok=True)

        logger.info(f"Initialized runner with config={config}, timeout={timeout}s")
        logger.info(f"Output directory: {self.output_dir}")

    def load_config(self) -> dict:
        """Load agent configuration (vanilla or acfs-enhanced)."""
        config_file = Path(__file__).parent / "configs" / f"{self.config}.json"
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_file}, using defaults")
            return self._get_default_config()

        with open(config_file) as f:
            return json.load(f)

    def _get_default_config(self) -> dict:
        """Get default configuration based on config name."""
        if self.config == "vanilla":
            return {
                "name": "vanilla",
                "prime_injection": False,
                "heartbeat_monitoring": False,
                "atomic_claiming": False
            }
        elif self.config == "acfs_enhanced":
            return {
                "name": "acfs_enhanced",
                "prime_injection": True,
                "heartbeat_monitoring": True,
                "atomic_claiming": True,
                "prime_template": "../templates/.beads/PRIME.md.template"
            }
        else:
            raise ValueError(f"Unknown config: {self.config}")

    def prepare_environment(self, instance: dict) -> Path:
        """
        Prepare isolated environment for task execution.

        Args:
            instance: SWE-bench instance dict with repo, base_commit, etc.

        Returns:
            Path to working directory
        """
        # Create temp directory for this task
        work_dir = Path(tempfile.mkdtemp(prefix=f"swebench_{instance['instance_id']}_"))

        # Clone repository
        logger.info(f"Cloning {instance['repo']} to {work_dir}")
        repo = Repo.clone_from(
            f"https://github.com/{instance['repo']}.git",
            work_dir
        )

        # Checkout base commit
        logger.info(f"Checking out {instance['base_commit']}")
        repo.git.checkout(instance['base_commit'])

        # Apply environment setup if needed
        if "environment_setup_commit" in instance:
            # Install dependencies, setup environment
            # This is specific to each repo/task
            pass

        return work_dir

    def run_claude_code(self, work_dir: Path, problem_statement: str) -> tuple[str, float]:
        """
        Run Claude Code agent on the problem.

        Args:
            work_dir: Path to repository
            problem_statement: Issue description

        Returns:
            Tuple of (transcript, execution_time)
        """
        start_time = time.time()

        # Build prompt
        prompt = self._build_prompt(problem_statement)

        # Run Claude Code
        # NOTE: This is a simplified version. In practice, you'd need to:
        # 1. Start a Claude Code session
        # 2. Send the prompt
        # 3. Capture output
        # 4. Wait for completion or timeout

        cmd = [
            "claude",
            "--directory", str(work_dir),
            "--message", prompt
        ]

        # Add config-specific flags
        config = self.load_config()
        if config.get("prime_injection"):
            # Inject PRIME template
            prime_file = work_dir / ".beads" / "PRIME.md"
            prime_file.parent.mkdir(exist_ok=True, parents=True)
            prime_content = self._load_prime_template()
            prime_file.write_text(prime_content)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=work_dir
            )
            transcript = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            transcript = "ERROR: Agent timed out"
        except Exception as e:
            transcript = f"ERROR: {str(e)}"

        elapsed = time.time() - start_time
        return transcript, elapsed

    def _build_prompt(self, problem_statement: str) -> str:
        """Build prompt for Claude Code."""
        return f"""
You are tasked with fixing a bug in this codebase.

Problem Description:
{problem_statement}

Please:
1. Analyze the issue
2. Identify the root cause
3. Implement a fix
4. Verify the fix resolves the issue

Make your changes and ensure all tests pass.
"""

    def _load_prime_template(self) -> str:
        """Load PRIME template for acfs-enhanced config."""
        template_path = Path(__file__).parent.parent / "templates" / ".beads" / "PRIME.md.template"
        if template_path.exists():
            return template_path.read_text()

        # Fallback minimal template
        return """# PRIME: Bug Fix Workflow

## Objective
Fix the reported bug by making minimal, targeted changes.

## Process
1. **Understand**: Read the issue description carefully
2. **Locate**: Find the relevant code causing the bug
3. **Fix**: Make the minimal change needed
4. **Verify**: Run tests to confirm the fix

## Guidelines
- Make focused changes, don't refactor unrelated code
- Preserve existing behavior except for the bug
- Add tests if missing coverage
"""

    def evaluate_solution(self, work_dir: Path, instance: dict) -> tuple[bool, int, int]:
        """
        Evaluate if the agent's solution resolves the issue.

        Args:
            work_dir: Path to repository with agent's changes
            instance: SWE-bench instance with test patch

        Returns:
            Tuple of (resolved, tests_passed, tests_failed)
        """
        # Apply test patch
        test_patch = instance.get("test_patch", "")
        if not test_patch:
            logger.warning(f"No test patch for {instance['instance_id']}")
            return False, 0, 0

        # Apply patch
        try:
            patch_file = work_dir / "test.patch"
            patch_file.write_text(test_patch)

            subprocess.run(
                ["git", "apply", "test.patch"],
                cwd=work_dir,
                check=True,
                capture_output=True
            )
            patch_applied = True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to apply test patch: {e}")
            return False, 0, 0

        # Run tests
        # NOTE: This is highly repo-specific. Each repo has different test commands.
        # In production, you'd use SWE-bench's Docker-based evaluation harness.
        try:
            # Example for Python repos
            result = subprocess.run(
                ["python", "-m", "pytest", "-xvs"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse test results (simplified)
            # Real implementation would parse pytest output properly
            if result.returncode == 0:
                return True, 1, 0  # All tests passed
            else:
                return False, 0, 1  # Tests failed
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return False, 0, 1

    def run_task(self, instance: dict) -> TaskResult:
        """
        Run a single SWE-bench task.

        Args:
            instance: SWE-bench instance dict

        Returns:
            TaskResult with evaluation outcome
        """
        instance_id = instance["instance_id"]
        logger.info(f"Running task: {instance_id}")

        work_dir = None
        try:
            # Prepare environment
            work_dir = self.prepare_environment(instance)

            # Run agent
            transcript, elapsed = self.run_claude_code(
                work_dir,
                instance["problem_statement"]
            )

            # Save transcript
            transcript_file = self.transcripts_dir / f"{instance_id}.txt"
            transcript_file.write_text(transcript)

            # Evaluate solution
            resolved, tests_passed, tests_failed = self.evaluate_solution(work_dir, instance)

            result = TaskResult(
                instance_id=instance_id,
                config=self.config,
                resolved=resolved,
                time_seconds=elapsed,
                agent_transcript=str(transcript_file),
                tests_passed=tests_passed,
                tests_failed=tests_failed
            )

            logger.info(f"Task {instance_id}: {'PASS' if resolved else 'FAIL'} ({elapsed:.1f}s)")
            return result

        except Exception as e:
            logger.error(f"Task {instance_id} failed: {e}")
            return TaskResult(
                instance_id=instance_id,
                config=self.config,
                resolved=False,
                time_seconds=0.0,
                error=str(e)
            )

        finally:
            # Cleanup
            if work_dir and work_dir.exists():
                import shutil
                shutil.rmtree(work_dir, ignore_errors=True)

    def run_benchmark(self, instances: list[dict], sample_size: Optional[int] = None):
        """
        Run benchmark on multiple instances.

        Args:
            instances: List of SWE-bench instances
            sample_size: If set, only run first N instances
        """
        if sample_size:
            instances = instances[:sample_size]
            logger.info(f"Running sample of {sample_size} tasks")

        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(
                f"[cyan]Running {self.config} benchmark...",
                total=len(instances)
            )

            for instance in instances:
                result = self.run_task(instance)
                results.append(result)

                # Save result incrementally
                with open(self.results_file, "a") as f:
                    f.write(json.dumps(result.to_dict()) + "\n")

                progress.advance(task)

        # Generate summary
        self.generate_summary(results)

    def generate_summary(self, results: list[TaskResult]):
        """Generate summary statistics."""
        total = len(results)
        resolved = sum(1 for r in results if r.resolved)
        failed = sum(1 for r in results if not r.resolved and not r.error)
        errors = sum(1 for r in results if r.error)

        avg_time = sum(r.time_seconds for r in results) / total if total > 0 else 0

        summary = {
            "config": self.config,
            "timestamp": datetime.now().isoformat(),
            "total_tasks": total,
            "resolved": resolved,
            "failed": failed,
            "errors": errors,
            "success_rate": (resolved / total * 100) if total > 0 else 0,
            "avg_time_seconds": avg_time
        }

        # Save summary
        summary_file = self.output_dir / "summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        # Print summary
        console.print("\n[bold cyan]Benchmark Summary[/bold cyan]")
        console.print(f"Config: {self.config}")
        console.print(f"Total tasks: {total}")
        console.print(f"Resolved: {resolved} ({summary['success_rate']:.1f}%)")
        console.print(f"Failed: {failed}")
        console.print(f"Errors: {errors}")
        console.print(f"Avg time: {avg_time:.1f}s")
        console.print(f"\nResults saved to: {self.output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Run SWE-bench benchmark")
    parser.add_argument(
        "--config",
        choices=["vanilla", "acfs_enhanced"],
        required=True,
        help="Agent configuration to test"
    )
    parser.add_argument(
        "--dataset",
        default="princeton-nlp/SWE-bench_Lite",
        help="SWE-bench dataset to use (default: Lite)"
    )
    parser.add_argument(
        "--sample",
        type=int,
        help="Run only first N tasks (for testing)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory for results"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout per task in seconds (default: 600)"
    )

    args = parser.parse_args()

    # Load dataset
    console.print(f"[cyan]Loading dataset: {args.dataset}[/cyan]")
    dataset = load_dataset(args.dataset, split="test")
    instances = list(dataset)
    console.print(f"Loaded {len(instances)} instances")

    # Run benchmark
    runner = SWEBenchRunner(
        config=args.config,
        output_dir=args.output,
        timeout=args.timeout
    )

    runner.run_benchmark(instances, sample_size=args.sample)

    console.print("[bold green]Benchmark complete![/bold green]")


if __name__ == "__main__":
    main()
