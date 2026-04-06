"""
HARD Task — Optimize Sorting Algorithm

The agent is given a naive O(n²) bubble sort implementation. It must:
1. Fix a logic bug causing incorrect sort order in edge cases.
2. Replace the O(n²) implementation with an efficient O(n log n) algorithm.
3. Ensure all correctness tests AND performance thresholds pass.

Difficulty: HARD
Files: 2 source files + tests + performance check
"""

from __future__ import annotations

from models.task import TaskDefinition, TaskDifficulty, TestCase, PerformanceThreshold
from tasks.base import BaseTask


class OptimizeSortTask(BaseTask):
    """Multi-file debug + performance optimization: fix and optimize sort."""

    TASK_ID = "hard_optimize_sort"

    def build(self) -> TaskDefinition:
        return TaskDefinition(
            task_id=self.TASK_ID,
            title="Debug and Optimize the Sorting Algorithm",
            difficulty=TaskDifficulty.HARD,
            description=(
                "The file `/project/sorter.py` contains a `Sorter` class with a "
                "`sort(data: list) -> list` method. It is currently implemented as "
                "bubble sort, and it has **two issues**:\n\n"
                "1. **A logic bug**: The comparison operator is wrong — descending sort "
                "   is produced instead of ascending.\n"
                "2. **Performance**: Bubble sort is O(n²). For large inputs (n=10,000), "
                "   it must complete within 500ms.\n\n"
                "**Your goal**:\n"
                "- Fix the bug so the sort is ascending.\n"
                "- Replace the implementation with an efficient O(n log n) algorithm "
                "  (e.g., merge sort, timsort, heapsort).\n"
                "- You may use only the Python standard library.\n"
                "- All tests in `/project/tests/test_sorter.py` must pass.\n\n"
                "**Files you may edit**: `/project/sorter.py`, `/project/utils.py`"
            ),
            initial_files={
                "/project/sorter.py": (
                    "class Sorter:\n"
                    "    def sort(self, data: list) -> list:\n"
                    "        \"\"\"Sort a list of numbers in ascending order.\"\"\"\n"
                    "        arr = list(data)\n"
                    "        n = len(arr)\n"
                    "        for i in range(n):\n"
                    "            for j in range(0, n - i - 1):\n"
                    "                if arr[j] < arr[j + 1]:  # BUG: should be >\n"
                    "                    arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
                    "        return arr\n"
                ),
                "/project/utils.py": (
                    "# Utility helpers for sorter.py\n"
                    "def generate_random_list(n: int, seed: int = 42) -> list:\n"
                    "    import random\n"
                    "    rng = random.Random(seed)\n"
                    "    return [rng.randint(0, 10_000) for _ in range(n)]\n"
                ),
                "/project/tests/test_sorter.py": (
                    "import sys, time\n"
                    "sys.path.insert(0, '/project')\n"
                    "from sorter import Sorter\n"
                    "from utils import generate_random_list\n\n"
                    "s = Sorter()\n\n"
                    "def test_ascending_basic():\n"
                    "    assert s.sort([3, 1, 2]) == [1, 2, 3]\n\n"
                    "def test_already_sorted():\n"
                    "    assert s.sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]\n\n"
                    "def test_reverse_sorted():\n"
                    "    assert s.sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]\n\n"
                    "def test_duplicates():\n"
                    "    assert s.sort([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]\n\n"
                    "def test_single_element():\n"
                    "    assert s.sort([42]) == [42]\n\n"
                    "def test_empty():\n"
                    "    assert s.sort([]) == []\n\n"
                    "def test_large_performance():\n"
                    "    data = generate_random_list(10_000)\n"
                    "    start = time.perf_counter()\n"
                    "    result = s.sort(data)\n"
                    "    elapsed_ms = (time.perf_counter() - start) * 1000\n"
                    "    assert result == sorted(data), 'Sort output incorrect'\n"
                    "    assert elapsed_ms < 500, f'Too slow: {elapsed_ms:.1f}ms (limit 500ms)'\n"
                ),
            },
            entry_point="/project/tests/test_sorter.py",
            seed=3,
            max_steps=40,
            test_cases=[
                TestCase(id="tc_basic", description="Basic ascending sort", weight=1.0),
                TestCase(id="tc_already_sorted", description="Already sorted list", weight=0.5),
                TestCase(id="tc_reverse", description="Reverse sorted list", weight=1.0),
                TestCase(id="tc_duplicates", description="List with duplicates", weight=1.0),
                TestCase(id="tc_single", description="Single element", weight=0.5),
                TestCase(id="tc_empty", description="Empty list", weight=0.5),
                TestCase(
                    id="tc_performance",
                    description="n=10,000 sorted in <500ms",
                    weight=2.0,
                    is_hidden=False,
                ),
            ],
            performance_thresholds=[
                PerformanceThreshold(
                    metric="runtime_ms",
                    operator="lt",
                    value=500.0,
                    weight=0.3,
                )
            ],
            hints=[
                "Look carefully at the comparison operator in the inner loop.",
                "Python's built-in sorted() is Timsort — you can use it or implement merge sort.",
            ],
            tags=["bug-fix", "optimization", "algorithms", "hard"],
        )
