"""
CodeAgentEnv — Main OpenEnv environment.

Wires together:
  - VirtualFileSystem (filesystem layer)
  - RestrictedExecutor (sandbox)
  - TestGrader + PerformanceGrader (graders)
  - RewardEngine (shaped rewards)

API
---
>>> env = CodeAgentEnv()
>>> obs = env.reset(task=FixSumBugTask().build())
>>> obs, reward, done, info = env.step(Action(type=ActionType.EDIT_FILE, payload=...))
>>> state = env.state()
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Tuple

from execution.sandbox import RestrictedExecutor
from filesystem.vfs import VirtualFileSystem
from graders.performance_grader import PerformanceGrader
from graders.test_grader import TestGrader
from models.action import Action, ActionType
from models.observation import Observation
from models.reward import RewardResult
from models.task import TaskDefinition
from rewards.reward_engine import RewardConfig, RewardEngine


class CodeAgentEnv:
    """
    OpenEnv — Production-grade benchmark environment for AI code agents.

    Parameters
    ----------
    executor_timeout : float
        Seconds before the sandbox kills a running process.
    reward_config : RewardConfig, optional
        Custom reward shaping weights.
    max_output_chars : int
        Truncation limit for sandbox stdout/stderr.
    """

    def __init__(
        self,
        executor_timeout: float = 15.0,
        reward_config: Optional[RewardConfig] = None,
        max_output_chars: int = 8192,
    ) -> None:
        self._executor = RestrictedExecutor(
            timeout_seconds=executor_timeout,
            max_output_chars=max_output_chars,
        )
        self._reward_engine = RewardEngine(config=reward_config)

        # State (populated on reset)
        self._task: Optional[TaskDefinition] = None
        self._vfs: Optional[VirtualFileSystem] = None
        self._test_grader: Optional[TestGrader] = None
        self._perf_grader: Optional[PerformanceGrader] = None

        self._step_count: int = 0
        self._done: bool = False
        self._episode_score: float = 0.0
        self._prev_pass_rate: float = 0.0
        self._last_action_summary: str = "None"
        self._prev_action: Optional[Action] = None
        self._action_history: List[str] = []
        self._console_output: str = ""
        self._test_results: str = ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self, task: Optional[TaskDefinition] = None) -> Observation:
        """
        Reset the environment to the initial state for ``task``.

        If ``task`` is None, resets the current task from scratch.
        """
        if task is not None:
            self._task = task

        if self._task is None:
            raise RuntimeError("No task set. Pass a TaskDefinition to reset().")

        # Re-initialise VFS
        self._vfs = VirtualFileSystem()
        self._vfs.load_initial_files(self._task.initial_files)

        # Re-create graders (they hold a task reference)
        self._test_grader = TestGrader(task=self._task, executor=self._executor)
        self._perf_grader = PerformanceGrader(task=self._task, executor=self._executor)

        # Reset episode state
        self._step_count = 0
        self._done = False
        self._episode_score = 0.0
        self._prev_pass_rate = 0.0
        self._last_action_summary = "None"
        self._prev_action = None
        self._action_history = []
        self._console_output = ""
        self._test_results = ""

        return self._make_observation()

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """
        Apply ``action`` and advance the environment by one step.

        Returns
        -------
        observation : Observation
        reward      : float
        done        : bool
        info        : dict
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        if self._task is None or self._vfs is None:
            raise RuntimeError("Environment not initialised. Call reset() first.")

        self._step_count += 1

        # Detect repeated actions (loop detection)
        repeated = (
            self._prev_action is not None
            and self._prev_action.type == action.type
            and self._prev_action.payload == action.payload
        )

        # Execute the action
        self._console_output = ""
        self._test_results = ""
        error_info: Optional[str] = None

        try:
            self._dispatch(action)
        except Exception as exc:
            error_info = str(exc)
            self._console_output = f"[ActionError] {exc}"

        self._last_action_summary = action.to_summary()
        self._action_history.append(self._last_action_summary)
        self._prev_action = action

        # Grade current state
        vfs_files = self._dump_vfs()
        grade = self._test_grader.grade(self._task.initial_files, vfs_files)
        pass_rate = grade.pass_rate
        self._test_results = grade.summary()

        # Check terminal conditions
        submit = action.type == ActionType.SUBMIT_SOLUTION
        max_steps = self._step_count >= self._task.max_steps
        self._done = submit or max_steps or (pass_rate >= 1.0 and submit)

        # Compute reward
        reward_result: RewardResult = self._reward_engine.compute(
            pass_rate=pass_rate,
            prev_pass_rate=self._prev_pass_rate,
            step_count=self._step_count,
            tests_passed=grade.passed,
            tests_total=grade.total,
            repeated_action=repeated,
            done=self._done,
            episode_score=self._episode_score,
        )

        self._episode_score = reward_result.episode_score
        self._prev_pass_rate = pass_rate

        obs = self._make_observation()

        info: Dict[str, Any] = {
            "step": self._step_count,
            "pass_rate": pass_rate,
            "tests_passed": grade.passed,
            "tests_total": grade.total,
            "episode_score": self._episode_score,
            "reward_breakdown": reward_result.breakdown.model_dump(),
            "grader_details": grade.details,
            "action_history": list(self._action_history),
            "error": error_info,
        }

        return obs, reward_result.value, self._done, info

    def state(self) -> Dict[str, Any]:
        """Return a full snapshot of the current environment state (read-only)."""
        return {
            "task_id": self._task.task_id if self._task else None,
            "step_count": self._step_count,
            "done": self._done,
            "episode_score": self._episode_score,
            "prev_pass_rate": self._prev_pass_rate,
            "action_history": list(self._action_history),
            "vfs_files": self._dump_vfs() if self._vfs else {},
        }

    # ------------------------------------------------------------------
    # Action dispatch
    # ------------------------------------------------------------------

    def _dispatch(self, action: Action) -> None:
        """Route action to the appropriate VFS / executor handler."""
        t = action.type
        p = action.payload

        if t == ActionType.OPEN_FILE:
            content = self._vfs.read_file(p.path)
            # Content is surfaced via observation.open_file_content
            self._console_output = f"Opened: {p.path}"

        elif t == ActionType.EDIT_FILE:
            self._vfs.write_file(p.path, p.content)
            self._console_output = f"Edited: {p.path}"

        elif t == ActionType.CREATE_FILE:
            self._vfs.write_file(p.path, p.content)
            self._console_output = f"Created: {p.path}"

        elif t == ActionType.DELETE_FILE:
            self._vfs.delete_file(p.path)
            self._console_output = f"Deleted: {p.path}"

        elif t == ActionType.RUN_TESTS:
            vfs_files = self._dump_vfs()
            grade = self._test_grader.grade(self._task.initial_files, vfs_files)
            self._test_results = grade.raw_output
            self._console_output = grade.summary()

        elif t == ActionType.EXECUTE_CODE:
            snippet = p.code_snippet or p.content or ""
            result = self._executor.execute(snippet)
            self._console_output = result.combined_output()

        elif t == ActionType.LIST_FILES:
            files = self._vfs.list_files()
            self._console_output = "\n".join(files) or "(empty)"

        elif t == ActionType.SUBMIT_SOLUTION:
            self._console_output = "Solution submitted. Episode ending."

        elif t == ActionType.RESET:
            self.reset()
            self._console_output = "Environment reset."

    # ------------------------------------------------------------------
    # Observation helpers
    # ------------------------------------------------------------------

    def _make_observation(self) -> Observation:
        """Construct an Observation from current state."""
        file_tree = self._vfs.to_file_tree() if self._vfs else None

        # Resolve open file content
        open_path: Optional[str] = None
        open_content: Optional[str] = None
        if (
            self._prev_action is not None
            and self._prev_action.type == ActionType.OPEN_FILE
            and self._prev_action.payload.path
        ):
            open_path = self._prev_action.payload.path
            try:
                open_content = self._vfs.read_file(open_path)
            except FileNotFoundError:
                open_content = f"[File not found: {open_path}]"

        return Observation(
            step_count=self._step_count,
            file_tree=file_tree,
            open_file_path=open_path,
            open_file_content=open_content,
            console_output=self._console_output,
            test_results=self._test_results,
            previous_action=self._last_action_summary,
            task_description=self._task.description if self._task else "",
            done=self._done,
            info={
                "episode_score": self._episode_score,
                "pass_rate": self._prev_pass_rate,
            },
        )

    def _dump_vfs(self) -> Dict[str, str]:
        """Dump all VFS files as a path→content dict."""
        if self._vfs is None:
            return {}
        files: Dict[str, str] = {}
        for path in self._vfs.list_files():
            try:
                files[path] = self._vfs.read_file(path)
            except Exception:
                pass
        return files
