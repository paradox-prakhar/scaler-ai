"""
OpenEnv CodeAgent Inference Script.
Compliant with Hackathon submission guidelines.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

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
    parts = [
        f"=== STEP {obs.step_count} ===",
        f"TASK:\n{obs.task_description}",
    ]
    if obs.console_output:
        parts.append(f"CONSOLE:\n{obs.console_output}")
    if obs.test_results:
        parts.append(f"TEST RESULTS:\n{obs.test_results}")
    if obs.open_file_content:
        parts.append(f"FILE: {obs.open_file_path}\n```python\n{obs.open_file_content}\n```")
    return "\n\n".join(parts)


def parse_action(response_text: str) -> Optional[Action]:
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        data = json.loads(text)
        return Action(type=ActionType(data["type"]), payload=ActionPayload(**data.get("payload", {})))
    except:
        return None

def run_episode(task: TaskDefinition, max_steps: Optional[int] = None) -> Dict[str, Any]:
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package not found.")

    api_base = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    api_key = os.environ.get("HF_TOKEN")
    model = os.environ.get("MODEL_NAME", "gpt-4o")

    if not api_key:
        raise EnvironmentError("HF_TOKEN missing from environment.")

    client = OpenAI(base_url=api_base, api_key=api_key)
    env = CodeAgentEnv()
    obs = env.reset(task=task)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    effective_max_steps = max_steps or task.max_steps
    episode_start = time.perf_counter()

    print(f"[START] Task={task.task_id} Model={model}")

    for step in range(effective_max_steps):
        print(f"[STEP] step={step + 1}")
        user_msg = obs_to_prompt(obs)
        messages.append({"role": "user", "content": user_msg})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=1024,
        )
        assistant_text = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": assistant_text})

        action = parse_action(assistant_text)
        if action is None:
            action = Action(type=ActionType.LIST_FILES)

        obs, reward, done, info = env.step(action)

        if done:
            break

    elapsed_ms = (time.perf_counter() - episode_start) * 1000
    final_state = env.state()
    pass_rate = info.get("pass_rate", 0.0)

    result = {
        "task_id": task.task_id,
        "total_steps": step + 1,
        "final_pass_rate": pass_rate,
        "episode_score": final_state.get("episode_score", 0.0),
        "solved": pass_rate >= 1.0,
        "timing_ms": round(elapsed_ms, 1),
    }

    print(f"[END] score={result['episode_score']:.3f} pass_rate={pass_rate:.0%} solved={result['solved']}")
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=list(TASK_REGISTRY), required=True)
    parser.add_argument("--max-steps", type=int, default=None)
    args = parser.parse_args()

    run_episode(TASK_REGISTRY[args.task], args.max_steps)

if __name__ == "__main__":
    main()
