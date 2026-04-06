"""
BaseGrader — abstract grader interface for OpenEnv CodeAgent.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GraderResult:
    """
    Unified result returned by every grader.

    Attributes
    ----------
    passed :        Number of test cases that passed.
    total :         Total number of test cases evaluated.
    pass_rate :     Fraction of tests passed (0.0–1.0).
    details :       Per-test outcome strings for logging/UI.
    raw_output :    Full stdout/stderr from execution, if available.
    error :         Top-level error message if grading itself failed.
    metadata :      Arbitrary extra data (execution time, etc.).
    """

    passed: int = 0
    total: int = 0
    pass_rate: float = 0.0
    details: List[str] = field(default_factory=list)
    raw_output: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.total > 0:
            self.pass_rate = self.passed / self.total

    @property
    def all_passed(self) -> bool:
        return self.passed == self.total and self.total > 0

    def summary(self) -> str:
        lines = [f"Passed: {self.passed}/{self.total} ({self.pass_rate:.0%})"]
        lines.extend(f"  {d}" for d in self.details)
        if self.error:
            lines.append(f"[ERROR] {self.error}")
        return "\n".join(lines)


class BaseGrader(ABC):
    """
    Abstract base class for all task graders.

    Subclasses must implement ``grade()``.
    """

    @abstractmethod
    def grade(
        self,
        task_files: Dict[str, str],
        vfs_files: Dict[str, str],
    ) -> GraderResult:
        """
        Grade the agent's solution.

        Parameters
        ----------
        task_files :
            The original task's initial files (read-only reference).
        vfs_files :
            Current state of the VFS (agent's edits).

        Returns
        -------
        GraderResult
        """
        ...
