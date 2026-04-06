"""
Task definition models — schema for benchmark tasks.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TestCase(BaseModel):
    """A single test case with optional visibility flag."""

    id: str
    description: str
    input_data: Optional[Any] = None
    expected_output: Optional[Any] = None
    is_hidden: bool = False  # hidden tests are excluded from agent observation
    weight: float = 1.0     # relative weight in scoring


class PerformanceThreshold(BaseModel):
    """Performance criteria for hard tasks."""

    metric: str  # e.g. "runtime_ms", "memory_kb"
    operator: str  # "lt", "lte", "gt", "gte"
    value: float
    weight: float = 0.2  # fraction of score attributed to perf


class TaskDefinition(BaseModel):
    """
    Complete specification for one benchmark task.

    Parameters
    ----------
    task_id:         Unique identifier, e.g. 'easy_fix_sum_bug'.
    title:           Short human-readable title.
    difficulty:      TaskDifficulty enum.
    description:     Full problem statement shown to the agent.
    initial_files:   Mapping of path → content for the starting codebase.
    entry_point:     File path (and optionally function) where tests are run.
    seed:            Fixed integer seed for deterministic setup.
    max_steps:       Hard step limit before forced termination.
    test_cases:      All test cases (visible + hidden combined internally).
    performance_thresholds: Optional performance requirements.
    hints:           Optional hints (for UI display, not agent input).
    tags:            Free-form tags for filtering/grouping.
    """

    task_id: str
    title: str
    difficulty: TaskDifficulty
    description: str
    initial_files: Dict[str, str] = Field(default_factory=dict)
    entry_point: str = "/project/tests/test_main.py"
    seed: int = 42
    max_steps: int = 30
    test_cases: List[TestCase] = Field(default_factory=list)
    performance_thresholds: List[PerformanceThreshold] = Field(default_factory=list)
    hints: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    @property
    def visible_tests(self) -> List[TestCase]:
        return [t for t in self.test_cases if not t.is_hidden]

    @property
    def hidden_tests(self) -> List[TestCase]:
        return [t for t in self.test_cases if t.is_hidden]

    @property
    def total_weight(self) -> float:
        return sum(t.weight for t in self.test_cases) or 1.0
