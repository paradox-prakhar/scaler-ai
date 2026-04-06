"""
TestGrader — runs unit tests against current VFS state.

Strategy
--------
1. Extract test file(s) from VFS.
2. Write all VFS files to a temp directory via RestrictedExecutor.run_pytest_style.
3. Parse stdout to count PASS/FAIL/ERROR lines.
4. Return GraderResult with detailed breakdown.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

from execution.sandbox import RestrictedExecutor
from graders.base import BaseGrader, GraderResult
from models.task import TaskDefinition


class TestGrader(BaseGrader):
    """
    Grade a task by executing its test suite against the agent's solution.

    Parameters
    ----------
    task : TaskDefinition
        The task being graded (used for entry_point path).
    executor : RestrictedExecutor, optional
        Custom executor. Defaults to one with 15s timeout.
    """

    PASS_PATTERN = re.compile(r"^PASS:\s+(.+)$", re.MULTILINE)
    FAIL_PATTERN = re.compile(r"^FAIL:\s+(.+)$", re.MULTILINE)
    ERROR_PATTERN = re.compile(r"^ERROR:\s+(.+)$", re.MULTILINE)
    SUMMARY_PATTERN = re.compile(r"=== (\d+)/(\d+) tests passed ===")

    def __init__(
        self,
        task: TaskDefinition,
        executor: Optional[RestrictedExecutor] = None,
    ) -> None:
        self.task = task
        self.executor = executor or RestrictedExecutor(timeout_seconds=30.0)

    def grade(
        self,
        task_files: Dict[str, str],
        vfs_files: Dict[str, str],
    ) -> GraderResult:
        """
        Run the task's test file against the current VFS state.

        Parameters
        ----------
        task_files : original task initial files (not used directly here).
        vfs_files  : current VFS path→content mapping.
        """
        test_path = self.task.entry_point  # e.g. /project/tests/test_solution.py

        # Extract test source from VFS (may have been modified by agent)
        test_source = vfs_files.get(test_path)
        if test_source is None:
            # Fallback to task's original test
            test_source = task_files.get(test_path)
        if test_source is None:
            return GraderResult(
                error=f"Test file not found in VFS: '{test_path}'",
            )

        # Run via sandbox with full VFS files for proper import resolution
        exec_result = self.executor.run_pytest_style(
            test_source=test_source,
            subject_source="",  # not used when vfs_files is provided
            vfs_files=vfs_files,
            test_path=test_path,
        )

        raw_output = exec_result.combined_output()

        # Parse results
        if exec_result.timed_out:
            return GraderResult(
                raw_output=raw_output,
                error="Test execution timed out.",
            )

        passes = self.PASS_PATTERN.findall(raw_output)
        fails = self.FAIL_PATTERN.findall(raw_output)
        errors = self.ERROR_PATTERN.findall(raw_output)

        # Try summary line first for totals
        summary_match = self.SUMMARY_PATTERN.search(raw_output)
        if summary_match:
            passed = int(summary_match.group(1))
            total = int(summary_match.group(2))
        else:
            passed = len(passes)
            total = passed + len(fails) + len(errors)

        details: list[str] = []
        details.extend(f"✅ PASS: {t}" for t in passes)
        details.extend(f"❌ FAIL: {t}" for t in fails)
        details.extend(f"💥 ERROR: {t}" for t in errors)

        if exec_result.error and not details:
            details.append(f"Execution error: {exec_result.error}")

        return GraderResult(
            passed=passed,
            total=total,
            details=details,
            raw_output=raw_output,
            metadata={"execution_time_ms": exec_result.execution_time_ms},
        )
