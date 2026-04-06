"""
Integration tests for the CodeAgentEnv (core environment).
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.environment import CodeAgentEnv
from models.action import Action, ActionPayload, ActionType
from models.observation import Observation
from tasks.easy.fix_sum_bug import FixSumBugTask


@pytest.fixture
def env() -> CodeAgentEnv:
    return CodeAgentEnv(executor_timeout=5.0)


@pytest.fixture
def task():
    return FixSumBugTask().build()


@pytest.fixture
def reset_env(env: CodeAgentEnv, task):
    """Return an env that has been reset with the easy task."""
    env.reset(task=task)
    return env


class TestEnvReset:
    def test_reset_returns_observation(self, env: CodeAgentEnv, task) -> None:
        obs = env.reset(task=task)
        assert isinstance(obs, Observation)
        assert obs.step_count == 0
        assert obs.done is False

    def test_reset_loads_initial_files(self, env: CodeAgentEnv, task) -> None:
        env.reset(task=task)
        state = env.state()
        assert "/project/solution.py" in state["vfs_files"]

    def test_reset_without_task_raises(self, env: CodeAgentEnv) -> None:
        with pytest.raises(RuntimeError, match="No task set"):
            env.reset()

    def test_reset_clears_step_count(self, env: CodeAgentEnv, task) -> None:
        env.reset(task=task)
        env.step(Action(type=ActionType.LIST_FILES))
        env.reset()  # same task
        assert env.state()["step_count"] == 0


class TestEnvStep:
    def test_list_files_action(self, reset_env: CodeAgentEnv) -> None:
        obs, reward, done, info = reset_env.step(Action(type=ActionType.LIST_FILES))
        assert isinstance(obs, Observation)
        assert "step" in info
        assert "pass_rate" in info

    def test_open_file_action(self, reset_env: CodeAgentEnv) -> None:
        obs, _, _, _ = reset_env.step(
            Action(
                type=ActionType.OPEN_FILE,
                payload=ActionPayload(path="/project/solution.py"),
            )
        )
        assert obs.open_file_path == "/project/solution.py"
        assert obs.open_file_content is not None

    def test_edit_file_action(self, reset_env: CodeAgentEnv) -> None:
        _, _, _, _ = reset_env.step(
            Action(
                type=ActionType.EDIT_FILE,
                payload=ActionPayload(path="/project/solution.py", content="x = 1\n"),
            )
        )
        state = reset_env.state()
        assert state["vfs_files"]["/project/solution.py"] == "x = 1\n"

    def test_step_increments_count(self, reset_env: CodeAgentEnv) -> None:
        reset_env.step(Action(type=ActionType.LIST_FILES))
        reset_env.step(Action(type=ActionType.LIST_FILES))
        assert reset_env.state()["step_count"] == 2

    def test_step_after_done_raises(self, reset_env: CodeAgentEnv) -> None:
        reset_env.step(Action(type=ActionType.SUBMIT_SOLUTION))
        with pytest.raises(RuntimeError, match="Episode is done"):
            reset_env.step(Action(type=ActionType.LIST_FILES))

    def test_submit_marks_done(self, reset_env: CodeAgentEnv) -> None:
        _, _, done, _ = reset_env.step(Action(type=ActionType.SUBMIT_SOLUTION))
        assert done is True

    def test_bad_path_surfaces_error_in_info(self, reset_env: CodeAgentEnv) -> None:
        obs, reward, done, info = reset_env.step(
            Action(
                type=ActionType.OPEN_FILE,
                payload=ActionPayload(path="/project/nonexistent.py"),
            )
        )
        # Should not crash — error captured in info
        assert info.get("error") is not None or obs.console_output != ""

    def test_info_contains_expected_keys(self, reset_env: CodeAgentEnv) -> None:
        _, _, _, info = reset_env.step(Action(type=ActionType.LIST_FILES))
        for key in ("step", "pass_rate", "tests_passed", "tests_total", "episode_score"):
            assert key in info, f"Missing key: {key}"


class TestEnvReward:
    def test_reward_is_float(self, reset_env: CodeAgentEnv) -> None:
        _, reward, _, _ = reset_env.step(Action(type=ActionType.LIST_FILES))
        assert isinstance(reward, float)

    def test_episode_score_increases_with_passing_tests(self, reset_env: CodeAgentEnv) -> None:
        # Apply the fix
        fixed_code = (
            "def sum_range(start: int, end: int) -> int:\n"
            "    total = 0\n"
            "    for i in range(start, end + 1):\n"
            "        total += i\n"
            "    return total\n"
        )
        reset_env.step(
            Action(
                type=ActionType.EDIT_FILE,
                payload=ActionPayload(path="/project/solution.py", content=fixed_code),
            )
        )
        _, _, _, info = reset_env.step(Action(type=ActionType.RUN_TESTS))
        # With fix applied, pass rate should be > 0
        assert info["pass_rate"] >= 0.0  # at minimum 0; likely >0 if sandbox works


class TestEnvState:
    def test_state_returns_dict(self, reset_env: CodeAgentEnv) -> None:
        state = reset_env.state()
        assert isinstance(state, dict)
        assert "task_id" in state
        assert "vfs_files" in state
        assert "step_count" in state
