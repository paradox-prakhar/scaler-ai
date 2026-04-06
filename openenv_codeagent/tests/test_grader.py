"""
Unit tests for the Grader Engine (TestGrader).
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from execution.sandbox import ExecutionResult
from graders.test_grader import TestGrader
from models.task import TaskDefinition, TaskDifficulty, TestCase


def _make_task(entry_point: str = "/project/tests/test_solution.py") -> TaskDefinition:
    return TaskDefinition(
        task_id="test_grader_task",
        title="Test Grader Task",
        difficulty=TaskDifficulty.EASY,
        description="Test task",
        initial_files={},
        entry_point=entry_point,
    )


def _make_grader(task: TaskDefinition, output: str, returncode: int = 0) -> TestGrader:
    """Create a TestGrader with a mocked executor."""
    grader = TestGrader(task=task)
    mock_result = ExecutionResult(
        stdout=output,
        returncode=returncode,
    )
    grader.executor = MagicMock()
    grader.executor.run_pytest_style.return_value = mock_result
    return grader


class TestTestGrader:
    def test_missing_test_file_returns_error(self) -> None:
        task = _make_task()
        grader = TestGrader(task=task)
        result = grader.grade(
            task_files={},
            vfs_files={},  # No test file
        )
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_all_pass(self) -> None:
        task = _make_task()
        output = "PASS: test_a\nPASS: test_b\n\n=== 2/2 tests passed ==="
        grader = _make_grader(task, output, returncode=0)
        result = grader.grade(
            task_files={},
            vfs_files={"/project/tests/test_solution.py": "# tests"},
        )
        assert result.passed == 2
        assert result.total == 2
        assert result.pass_rate == pytest.approx(1.0)
        assert result.all_passed

    def test_partial_pass(self) -> None:
        task = _make_task()
        output = "PASS: test_a\nFAIL: test_b — assertion error\n\n=== 1/2 tests passed ==="
        grader = _make_grader(task, output, returncode=1)
        result = grader.grade(
            task_files={},
            vfs_files={"/project/tests/test_solution.py": "# tests"},
        )
        assert result.passed == 1
        assert result.total == 2
        assert result.pass_rate == pytest.approx(0.5)

    def test_all_fail(self) -> None:
        task = _make_task()
        output = "FAIL: test_x\nFAIL: test_y\n\n=== 0/2 tests passed ==="
        grader = _make_grader(task, output, returncode=1)
        result = grader.grade(
            task_files={},
            vfs_files={"/project/tests/test_solution.py": "# tests"},
        )
        assert result.passed == 0
        assert result.pass_rate == pytest.approx(0.0)

    def test_timeout_returns_error(self) -> None:
        task = _make_task()
        grader = TestGrader(task=task)
        timed_out_result = ExecutionResult(timed_out=True, returncode=124)
        grader.executor = MagicMock()
        grader.executor.run_pytest_style.return_value = timed_out_result
        result = grader.grade(
            task_files={},
            vfs_files={"/project/tests/test_solution.py": "# tests"},
        )
        assert result.error is not None
        assert "timed out" in result.error.lower()

    def test_details_contain_pass_fail_markers(self) -> None:
        task = _make_task()
        output = "PASS: test_sum\nFAIL: test_edge\n\n=== 1/2 tests passed ==="
        grader = _make_grader(task, output, returncode=1)
        result = grader.grade(
            task_files={},
            vfs_files={"/project/tests/test_solution.py": "# tests"},
        )
        assert any("PASS" in d for d in result.details)
        assert any("FAIL" in d for d in result.details)
