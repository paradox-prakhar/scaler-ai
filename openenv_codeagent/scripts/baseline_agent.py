"""
Baseline Agent — GPT-4 powered agent for OpenEnv CodeAgent benchmark.

Runs a full episode on a given task using the OpenAI API (temperature=0).
Logs all actions + observations, outputs final score + episode log.

Usage
-----
    python scripts/baseline_agent.py --task easy_fix_sum_bug
    python scripts/baseline_agent.py --task medium_add_feature --max-steps 30
    python scripts/baseline_agent.py --task hard_optimize_sort --output episode.json

Environment Variables
---------------------
    OPENAI_API_KEY : Required. Your OpenAI API key.
    OPENAI_MODEL   : Optional. Default: gpt-4o (fallback: gpt-4-turbo).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Project root on sys.path ──────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.environment import CodeAgentEnv
from models.action import Action, ActionType, ActionPayload
from models.observation import Observation
from models.task import TaskDefinition
from tasks.easy.fix_sum_bug import FixSumBugTask
from tasks.medium.add_feature import AddFeatureTask
from tasks.hard.optimize_sort import OptimizeSortTask


# ── Task registry ─────────────────────────────────────────────────────────────
TASK_REGISTRY: Dict[str, TaskDefinition] = {
    "easy_fix_sum_bug": FixSumBugTask().build(),
    "medium_add_feature": AddFeatureTask().build(),
    "hard_optimize_sort": OptimizeSortTask().build(),
}


# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an expert software engineer working inside a virtual coding environment.
You are given a programming task and must solve it by taking actions one at a time.

AVAILABLE ACTIONS (respond with valid JSON):
- {"type": "list_files"}
- {"type": "open_file", "payload": {"path": "/project/file.py"}}
- {"type": "edit_file", "payload": {"path": "/project/file.py", "content": "NEW CONTENT HERE"}}
- {"type": "create_file", "payload": {"path": "/project/new_file.py", "content": "CONTENT"}}
- {"type": "run_tests"}
- {"type": "execute_code", "payload": {"code_snippet": "print('hello')"}}
- {"type": "submit_solution"}

IMPORTANT RULES:
1. Take EXACTLY ONE action per response.
2. Respond with ONLY the raw JSON — no markdown, no explanation.
3. Always run_tests before submitting to confirm your fix works.
4. Do not repeat the same action twice in a row.
5. When you are confident all tests pass, call submit_solution.
""".strip()


def obs_to_prompt(obs: Observation) -> str:
    """Convert an Observation to a user message for the LLM."""
    parts = [
        f"=== STEP {obs.step_count} ===",
        f"TASK:\n{obs.task_description}",
        f"PREVIOUS ACTION: {obs.previous_action}",
    ]
    if obs.console_output:
        parts.append(f"CONSOLE:\n{obs.console_output}")
    if obs.test_results:
        parts.append(f"TEST RESULTS:\n{obs.test_results}")
    if obs.open_file_path and obs.open_file_content:
        parts.append(f"FILE: {obs.open_file_path}\n```python\n{obs.open_file_content}\n```")
    if obs.file_tree:
        file_paths = _flatten_tree(obs.file_tree.root, [])
        parts.append("FILES:\n" + "\n".join(f"  {p}" for p in file_paths))
    return "\n\n".join(parts)


def _flatten_tree(node: Any, paths: List[str]) -> List[str]:
    if not node.is_dir:
        paths.append(node.path)
    for child in (node.children or []):
        _flatten_tree(child, paths)
    return paths


def parse_action(response_text: str) -> Optional[Action]:
    """Parse JSON text into an Action. Returns None on failure."""
    text = response_text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        data = json.loads(text)
        action_type = ActionType(data["type"])
        payload_data = data.get("payload", {})
        payload = ActionPayload(**payload_data)
        return Action(type=action_type, payload=payload)
    except Exception as exc:
        print(f"[parse_action] Failed: {exc} | Raw: {response_text[:200]}")
        return None


def run_episode(
    task: TaskDefinition,
    model: str = "gpt-4o",
    max_steps: Optional[int] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run a full episode of the baseline agent on ``task``.

    Returns a dict with: task_id, total_steps, final_pass_rate,
    episode_score, solved, action_log, timing_ms.
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package not found. Install with: pip install openai")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set in environment.")

    client = OpenAI(api_key=api_key)
    env = CodeAgentEnv()
    obs = env.reset(task=task)

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    effective_max_steps = max_steps or task.max_steps
    action_log: List[Dict[str, Any]] = []
    episode_start = time.perf_counter()

    for step in range(effective_max_steps):
        user_msg = obs_to_prompt(obs)
        messages.append({"role": "user", "content": user_msg})

        if verbose:
            print(f"\n{'─'*60}")
            print(f"STEP {step + 1}/{effective_max_steps}")
            print(user_msg[:800])

        # LLM call
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=1024,
        )
        assistant_text = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": assistant_text})

        if verbose:
            print(f"\nAGENT → {assistant_text[:500]}")

        action = parse_action(assistant_text)
        if action is None:
            # Inject a fallback list_files action to prevent infinite loop
            action = Action(type=ActionType.LIST_FILES)

        obs, reward, done, info = env.step(action)

        action_log.append({
            "step": step + 1,
            "action": assistant_text,
            "reward": reward,
            "pass_rate": info.get("pass_rate", 0.0),
            "done": done,
        })

        if verbose:
            print(f"REWARD: {reward:.3f} | PASS: {info.get('pass_rate', 0):.0%} | DONE: {done}")

        if done:
            break

    elapsed_ms = (time.perf_counter() - episode_start) * 1000
    final_state = env.state()

    result = {
        "task_id": task.task_id,
        "task_title": task.title,
        "difficulty": task.difficulty.value,
        "total_steps": step + 1,
        "final_pass_rate": info.get("pass_rate", 0.0),
        "episode_score": final_state.get("episode_score", 0.0),
        "solved": info.get("pass_rate", 0.0) >= 1.0,
        "timing_ms": round(elapsed_ms, 1),
        "action_log": action_log,
    }

    if verbose:
        print(f"\n{'='*60}")
        print(f"EPISODE COMPLETE: {task.title}")
        print(f"Score: {result['episode_score']:.3f} | Pass rate: {result['final_pass_rate']:.0%}")
        print(f"Solved: {'✅' if result['solved'] else '❌'} | Steps: {result['total_steps']}")
        print(f"Time: {elapsed_ms:.0f}ms")

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenEnv Baseline Agent (GPT-4)")
    parser.add_argument(
        "--task",
        choices=list(TASK_REGISTRY),
        required=True,
        help="Task ID to run.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        help="OpenAI model name (default: gpt-4o).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Override task max_steps.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to write episode JSON log.",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output.")
    args = parser.parse_args()

    task = TASK_REGISTRY[args.task]
    result = run_episode(
        task=task,
        model=args.model,
        max_steps=args.max_steps,
        verbose=not args.quiet,
    )

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nEpisode log saved to: {out_path}")
    else:
        print("\n--- Episode Summary JSON ---")
        print(json.dumps({k: v for k, v in result.items() if k != "action_log"}, indent=2))


if __name__ == "__main__":
    main()
