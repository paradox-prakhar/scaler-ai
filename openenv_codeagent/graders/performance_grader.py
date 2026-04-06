"""
PerformanceGrader — measures runtime of agent's solution against thresholds.

Works alongside TestGrader: TestGrader checks correctness,
PerformanceGrader checks efficiency.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

from execution.sandbox import RestrictedExecutor, ExecutionResult
from graders.base import BaseGrader, GraderResult
from models.task import TaskDefinition, PerformanceThreshold


# Code template injected to benchmark runtime
_PERF_TEMPLATE = """
import time as _time_module

def _benchmark(fn, *args, **kwargs):
    start = _time_module.perf_counter()
    result = fn(*args, **kwargs)
    elapsed_ms = (_time_module.perf_counter() - start) * 1000
    return result, elapsed_ms
"""


class PerformanceGrader(BaseGrader):
    """
    Measure and validate runtime/memory performance of the agent's solution.

    Currently supports ``runtime_ms`` metric with lt/lte/gt/gte operators.

    Parameters
    ----------
    task : TaskDefinition
        Provides performance_thresholds to check against.
    executor : RestrictedExecutor, optional
        Custom executor (defaults to 30s timeout for perf tests).
    """

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
        Run performance benchmarks from the test file and compare against thresholds.

        The test file itself must contain the timing assertions (as in the hard task).
        We re-run the full test suite and look for timing output.
        """
        if not self.task.performance_thresholds:
            return GraderResult(
                passed=0,
                total=0,
                details=["No performance thresholds defined for this task."],
            )

        test_path = self.task.entry_point
        test_source = vfs_files.get(test_path)
        if test_source is None:
            return GraderResult(
                error=f"Test file not found in VFS: '{test_path}'"
            )

        subject_parts = []
        for path, content in sorted(vfs_files.items()):
            if path == test_path or "/tests/" in path:
                continue
            if path.endswith(".py"):
                subject_parts.append(content)

        subject_source = "\n".join(subject_parts)

        # Extract only performance-related test functions
        perf_tests = self._extract_perf_tests(test_source)
        if not perf_tests:
            return GraderResult(
                passed=0,
                total=len(self.task.performance_thresholds),
                details=["No performance test functions found (looked for 'test_*_performance' or 'test_large_*')."],
            )

        exec_result = self.executor.run_pytest_style(
            test_source=perf_tests,
            subject_source=subject_source,
        )

        raw_output = exec_result.combined_output()
        passed = raw_output.count("PASS:")
        failed = raw_output.count("FAIL:") + raw_output.count("ERROR:")
        total = passed + failed

        details = []
        for line in raw_output.splitlines():
            if line.startswith("PASS:") or line.startswith("FAIL:") or line.startswith("ERROR:"):
                details.append(line)

        if exec_result.timed_out:
            return GraderResult(
                total=len(self.task.performance_thresholds),
                raw_output=raw_output,
                error="Performance test timed out.",
                metadata={"execution_time_ms": exec_result.execution_time_ms},
            )

        return GraderResult(
            passed=passed,
            total=max(total, len(self.task.performance_thresholds)),
            details=details,
            raw_output=raw_output,
            metadata={"execution_time_ms": exec_result.execution_time_ms},
        )

    @staticmethod
    def _extract_perf_tests(test_source: str) -> str:
        """Extract only performance-related test functions from a test file."""
        lines = test_source.splitlines(keepends=True)
        perf_funcs = []
        in_func = False
        current_func: list[str] = []
        is_perf = False

        for line in lines:
            if line.startswith("def test_"):
                if in_func and is_perf:
                    perf_funcs.extend(current_func)
                current_func = [line]
                in_func = True
                func_name = line.split("(")[0].replace("def ", "").strip()
                is_perf = "perf" in func_name or "large" in func_name or "performance" in func_name
            elif in_func:
                current_func.append(line)

        if in_func and is_perf:
            perf_funcs.extend(current_func)

        return "".join(perf_funcs)
