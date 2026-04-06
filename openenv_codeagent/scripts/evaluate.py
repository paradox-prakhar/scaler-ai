"""
Benchmark Evaluator — runs the baseline agent on all tasks and produces a summary table.

Usage
-----
    python scripts/evaluate.py
    python scripts/evaluate.py --model gpt-4o --output results/benchmark.json
    python scripts/evaluate.py --tasks easy_fix_sum_bug medium_add_feature

Environment Variables
---------------------
    OPENAI_API_KEY : Required.
    OPENAI_MODEL   : Optional. Default: gpt-4o.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for baseline_agent import

from baseline_agent import TASK_REGISTRY, run_episode


def print_table(results: List[Dict]) -> None:
    """Print a formatted benchmark results table."""
    header = f"{'Task ID':<30} {'Difficulty':<10} {'Pass%':>6} {'Score':>7} {'Steps':>6} {'Solved':>7} {'ms':>8}"
    print("\n" + "=" * 80)
    print("OpenEnv Baseline Benchmark Results")
    print("=" * 80)
    print(header)
    print("-" * 80)
    for r in results:
        solved_mark = "✅" if r["solved"] else "❌"
        print(
            f"{r['task_id']:<30} {r['difficulty']:<10} "
            f"{r['final_pass_rate']:>5.0%} "
            f"{r['episode_score']:>7.3f} "
            f"{r['total_steps']:>6} "
            f"{solved_mark:>7} "
            f"{r['timing_ms']:>8.0f}"
        )
    print("=" * 80)

    # Aggregate stats
    n = len(results)
    solved = sum(1 for r in results if r["solved"])
    avg_pass = sum(r["final_pass_rate"] for r in results) / n if n else 0
    avg_score = sum(r["episode_score"] for r in results) / n if n else 0
    total_ms = sum(r["timing_ms"] for r in results)
    print(f"\nSummary: {solved}/{n} tasks solved | Avg pass: {avg_pass:.0%} | Avg score: {avg_score:.3f} | Total: {total_ms:.0f}ms\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenEnv Benchmark Evaluator")
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=list(TASK_REGISTRY),
        default=list(TASK_REGISTRY),
        help="Task IDs to evaluate (default: all).",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        help="OpenAI model name.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to write JSON results.",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    results: List[Dict] = []
    for task_id in args.tasks:
        task = TASK_REGISTRY[task_id]
        print(f"\n▶ Running: {task.title} ({task.difficulty.value})")
        try:
            result = run_episode(task=task, model=args.model, verbose=not args.quiet)
            results.append(result)
        except Exception as exc:
            print(f"  ⚠ Failed: {exc}")
            results.append({
                "task_id": task_id,
                "task_title": task.title,
                "difficulty": task.difficulty.value,
                "total_steps": 0,
                "final_pass_rate": 0.0,
                "episode_score": 0.0,
                "solved": False,
                "timing_ms": 0.0,
                "error": str(exc),
                "action_log": [],
            })

    print_table(results)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {out}")


if __name__ == "__main__":
    main()
