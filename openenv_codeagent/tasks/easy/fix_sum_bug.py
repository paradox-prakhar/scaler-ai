"""
EASY Task — Fix Sum Bug

The agent is given a Python file with an intentional off-by-one bug in a
``sum_range`` function. It must identify and fix the bug so all tests pass.

Difficulty: EASY
Files: 1 source + 1 test
"""

from __future__ import annotations

from models.task import TaskDefinition, TaskDifficulty, TestCase
from tasks.base import BaseTask


class FixSumBugTask(BaseTask):
    """Single-file bug fix: fix an off-by-one error in sum_range()."""

    TASK_ID = "easy_fix_sum_bug"

    def build(self) -> TaskDefinition:
        return TaskDefinition(
            task_id=self.TASK_ID,
            title="Fix the Sum Bug",
            difficulty=TaskDifficulty.EASY,
            description=(
                "The function `sum_range(start, end)` in `/project/solution.py` "
                "is supposed to return the sum of all integers from `start` to `end` "
                "(inclusive). However, it has a bug causing it to produce wrong results.\n\n"
                "**Your goal**: Edit `/project/solution.py` to fix the bug so that all "
                "test cases pass.\n\n"
                "**Hint**: Check the loop boundary carefully."
            ),
            initial_files={
                "/project/solution.py": (
                    "def sum_range(start: int, end: int) -> int:\n"
                    "    \"\"\"Return sum of integers from start to end (inclusive).\"\"\"\n"
                    "    total = 0\n"
                    "    for i in range(start, end):  # BUG: should be range(start, end + 1)\n"
                    "        total += i\n"
                    "    return total\n"
                ),
                "/project/tests/test_solution.py": (
                    "import sys, os\n"
                    "sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))\n"
                    "sys.path.insert(0, '/project')\n"
                    "from solution import sum_range\n\n"
                    "def test_basic():\n"
                    "    assert sum_range(1, 5) == 15\n\n"
                    "def test_single():\n"
                    "    assert sum_range(3, 3) == 3\n\n"
                    "def test_zero_start():\n"
                    "    assert sum_range(0, 10) == 55\n\n"
                    "def test_negative():\n"
                    "    assert sum_range(-3, 3) == 0\n"
                ),
            },
            entry_point="/project/tests/test_solution.py",
            seed=1,
            max_steps=20,
            test_cases=[
                TestCase(
                    id="tc_basic",
                    description="sum_range(1, 5) == 15",
                    input_data={"start": 1, "end": 5},
                    expected_output=15,
                    weight=1.0,
                ),
                TestCase(
                    id="tc_single",
                    description="sum_range(3, 3) == 3 (single element)",
                    input_data={"start": 3, "end": 3},
                    expected_output=3,
                    weight=1.0,
                ),
                TestCase(
                    id="tc_zero_start",
                    description="sum_range(0, 10) == 55",
                    input_data={"start": 0, "end": 10},
                    expected_output=55,
                    weight=1.0,
                ),
                TestCase(
                    id="tc_negative",
                    description="sum_range(-3, 3) == 0 (negative range)",
                    input_data={"start": -3, "end": 3},
                    expected_output=0,
                    weight=1.0,
                    is_hidden=True,
                ),
            ],
            hints=[
                "Look at the range() call in the for loop.",
                "Python's range(a, b) excludes b. What should it be?",
            ],
            tags=["bug-fix", "loops", "easy"],
        )
