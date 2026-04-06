"""
OpenEnv CodeAgent — Gradio Web UI

Deployable to Hugging Face Spaces.

Features
--------
- Task selector (easy / medium / hard)
- File tree explorer
- Code editor for any VFS file
- Terminal output panel
- Action history feed
- Step-by-step control OR full auto-run
- Reward / score display

Run locally
-----------
    pip install gradio
    python app/main.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gradio as gr

from core.environment import CodeAgentEnv
from models.action import Action, ActionPayload, ActionType
from models.task import TaskDefinition
from tasks.easy.fix_sum_bug import FixSumBugTask
from tasks.hard.optimize_sort import OptimizeSortTask
from tasks.medium.add_feature import AddFeatureTask

# ── Task Registry ─────────────────────────────────────────────────────────────
TASKS: Dict[str, TaskDefinition] = {
    "🟢 Easy — Fix Sum Bug": FixSumBugTask().build(),
    "🟡 Medium — Add Word Frequency": AddFeatureTask().build(),
    "🔴 Hard — Optimize Sort": OptimizeSortTask().build(),
}

# ── Global env state (Gradio is single-threaded for demos) ───────────────────
_env: Optional[CodeAgentEnv] = None
_current_task: Optional[TaskDefinition] = None
_obs = None
_done = False
_action_log: List[str] = []


def _get_env() -> CodeAgentEnv:
    """Return the global env, creating it if needed."""
    global _env
    if _env is None:
        _env = CodeAgentEnv()
    return _env


def _task_label(task: TaskDefinition) -> str:
    return task.description[:300] + ("..." if len(task.description) > 300 else "")


def _format_file_tree(vfs_files: Dict[str, str]) -> str:
    if not vfs_files:
        return "(empty)"
    lines = []
    for path in sorted(vfs_files.keys()):
        indent = "  " * (path.count("/") - 2)
        lines.append(f"{indent}📄 {path.split('/')[-1]}")
    return "\n".join(lines)


def _format_action_log(log: List[str]) -> str:
    if not log:
        return "(no actions yet)"
    return "\n".join(f"[{i+1}] {a}" for i, a in enumerate(log[-20:]))


# ── Handlers ──────────────────────────────────────────────────────────────────

def reset_env(task_label: str) -> Tuple[str, str, str, str, str, str]:
    """Reset the environment for the selected task."""
    global _env, _current_task, _obs, _done, _action_log

    task = TASKS[task_label]
    _current_task = task
    _env = CodeAgentEnv()
    _obs = _env.reset(task=task)
    _done = False
    _action_log = []

    vfs = _env.state()["vfs_files"]
    return (
        _task_label(task),                      # task description
        _format_file_tree(vfs),                 # file tree
        "",                                     # code editor (cleared)
        "Environment reset. Ready to act.",     # terminal
        _format_action_log(_action_log),        # action log
        f"Step: 0 | Score: 0.000 | Pass: 0%",  # status
    )


def open_file_ui(path: str) -> Tuple[str, str]:
    """Open a file in the code editor panel."""
    global _obs
    if not path.strip():
        return "Please enter a file path.", ""
    env = _get_env()
    if env is None or _current_task is None:
        return "No task loaded. Please reset first.", ""
    try:
        action = Action(type=ActionType.OPEN_FILE, payload=ActionPayload(path=path.strip()))
        _obs, _, _, info = env.step(action)
        _action_log.append(action.to_summary())
        return _obs.open_file_content or "(empty file)", _obs.console_output
    except Exception as exc:
        return f"Error: {exc}", ""


def edit_file_ui(path: str, content: str) -> Tuple[str, str, str]:
    """Save edited content back to VFS."""
    global _obs, _done
    env = _get_env()
    if not path.strip():
        return "Please enter a file path.", _format_action_log(_action_log), _make_status()
    try:
        action = Action(
            type=ActionType.EDIT_FILE,
            payload=ActionPayload(path=path.strip(), content=content),
        )
        _obs, reward, _done, info = env.step(action)
        _action_log.append(f"edit_file({path.strip()}) -> reward={reward:.3f}")
        terminal = f"Saved {path.strip()}\n\nReward: {reward:+.3f}"
        return terminal, _format_action_log(_action_log), _make_status(info)
    except Exception as exc:
        return f"Error: {exc}", _format_action_log(_action_log), _make_status()


def run_tests_ui() -> Tuple[str, str, str]:
    """Run tests and show results."""
    global _obs, _done
    env = _get_env()
    try:
        action = Action(type=ActionType.RUN_TESTS)
        _obs, reward, _done, info = env.step(action)
        _action_log.append(f"run_tests() -> reward={reward:.3f} | pass={info.get('pass_rate', 0):.0%}")
        terminal = _obs.test_results or _obs.console_output or "(no output)"
        return terminal, _format_action_log(_action_log), _make_status(info)
    except Exception as exc:
        return f"Error: {exc}", _format_action_log(_action_log), _make_status()


def submit_ui() -> Tuple[str, str, str]:
    """Submit the solution."""
    global _obs, _done
    env = _get_env()
    try:
        action = Action(type=ActionType.SUBMIT_SOLUTION)
        _obs, reward, _done, info = env.step(action)
        pass_rate = info.get("pass_rate", 0)
        solved = pass_rate >= 1.0
        _action_log.append(f"submit_solution() -> score={info.get('episode_score', 0):.3f}")
        terminal = (
            f"{'Solved!' if solved else 'Not fully solved.'}\n"
            f"Final Pass Rate: {pass_rate:.0%}\n"
            f"Episode Score: {info.get('episode_score', 0):.3f}\n"
            f"Steps Used: {info.get('step', '?')}"
        )
        return terminal, _format_action_log(_action_log), _make_status(info)
    except Exception as exc:
        return f"Error: {exc}", _format_action_log(_action_log), _make_status()


def list_files_ui() -> Tuple[str, str]:
    """List all VFS files."""
    env = _get_env()
    try:
        state = env.state()
        vfs = state.get("vfs_files", {})
        tree = _format_file_tree(vfs)
        detail = "\n".join(sorted(vfs.keys()))
        return tree, detail
    except Exception as exc:
        return f"Error: {exc}", ""


def execute_snippet_ui(snippet: str) -> str:
    """Execute a code snippet in the sandbox."""
    global _obs
    env = _get_env()
    if not snippet.strip():
        return "Enter code to execute."
    try:
        action = Action(
            type=ActionType.EXECUTE_CODE,
            payload=ActionPayload(code_snippet=snippet),
        )
        _obs, _, _, _ = env.step(action)
        _action_log.append("execute_code(snippet)")
        return _obs.console_output or "(no output)"
    except Exception as exc:
        return f"Error: {exc}"


def _make_status(info: Optional[Dict[str, Any]] = None) -> str:
    env = _get_env()
    step = info.get("step", env.state().get("step_count", 0) if env._task is not None else 0) if info else 0
    score = info.get("episode_score", 0.0) if info else 0.0
    pr = info.get("pass_rate", 0.0) if info else 0.0
    done_str = " DONE" if _done else ""
    return f"Step: {step} | Score: {score:.3f} | Pass: {pr:.0%}{done_str}"


# ── Gradio UI Layout ──────────────────────────────────────────────────────────

CSS = """
body { font-family: 'Inter', sans-serif; background: #0f0f17; color: #e0e0f0; }
.gr-button-primary { background: #6c63ff !important; border-radius: 8px !important; }
.gr-button { border-radius: 8px !important; }
.gr-text-input, .gr-textbox { font-family: 'Fira Code', monospace !important; }
.gr-panel { border-radius: 12px !important; }
footer { display: none !important; }
"""

with gr.Blocks(
    title="OpenEnv CodeAgent",
    css=CSS,
    theme=gr.themes.Base(
        primary_hue="purple",
        neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter"),
    ),
) as demo:

    gr.Markdown(
        """
        # 🤖 OpenEnv CodeAgent
        *A production-grade benchmark environment where AI agents solve real software engineering tasks.*
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            task_dd = gr.Dropdown(
                choices=list(TASKS.keys()),
                value=list(TASKS.keys())[0],
                label="Select Task",
            )
            reset_btn = gr.Button("🔄 Reset Environment", variant="primary")
            task_desc = gr.Textbox(label="Task Description", lines=6, interactive=False)
            file_tree_box = gr.Textbox(label="📁 File Tree", lines=8, interactive=False)
            status_box = gr.Textbox(label="📊 Status", interactive=False)

        with gr.Column(scale=2):
            with gr.Tab("📝 Code Editor"):
                file_path_input = gr.Textbox(
                    label="File Path", placeholder="/project/solution.py"
                )
                open_file_btn = gr.Button("📂 Open File")
                code_editor = gr.Code(
                    label="File Content",
                    language="python",
                    lines=20,
                    interactive=True,
                )
                with gr.Row():
                    save_btn = gr.Button("💾 Save File", variant="primary")
                    run_tests_btn = gr.Button("🧪 Run Tests", variant="secondary")
                    submit_btn = gr.Button("🚀 Submit Solution", variant="stop")

            with gr.Tab("💻 Terminal"):
                terminal_box = gr.Textbox(
                    label="Output",
                    lines=20,
                    interactive=False,
                    elem_classes=["gr-text-input"],
                )
                snippet_input = gr.Code(
                    label="Execute Code Snippet",
                    language="python",
                    lines=5,
                )
                exec_btn = gr.Button("▶ Execute Snippet")

            with gr.Tab("📜 Action History"):
                action_log_box = gr.Textbox(
                    label="Action Log (last 20)",
                    lines=20,
                    interactive=False,
                )
                list_files_btn = gr.Button("📁 Refresh File Tree")

    # ── Event bindings ────────────────────────────────────────────────────────

    reset_btn.click(
        fn=reset_env,
        inputs=[task_dd],
        outputs=[task_desc, file_tree_box, code_editor, terminal_box, action_log_box, status_box],
    )

    open_file_btn.click(
        fn=open_file_ui,
        inputs=[file_path_input],
        outputs=[code_editor, terminal_box],
    )

    save_btn.click(
        fn=edit_file_ui,
        inputs=[file_path_input, code_editor],
        outputs=[terminal_box, action_log_box, status_box],
    )

    run_tests_btn.click(
        fn=run_tests_ui,
        inputs=[],
        outputs=[terminal_box, action_log_box, status_box],
    )

    submit_btn.click(
        fn=submit_ui,
        inputs=[],
        outputs=[terminal_box, action_log_box, status_box],
    )

    exec_btn.click(
        fn=execute_snippet_ui,
        inputs=[snippet_input],
        outputs=[terminal_box],
    )

    list_files_btn.click(
        fn=list_files_ui,
        inputs=[],
        outputs=[file_tree_box, terminal_box],
    )

    # Auto-reset on load
    demo.load(
        fn=reset_env,
        inputs=[task_dd],
        outputs=[task_desc, file_tree_box, code_editor, terminal_box, action_log_box, status_box],
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
