"""
MEDIUM Task — Add Feature: Word Frequency Counter

The agent is given an existing `TextAnalyzer` class that has basic functionality.
It must add a new `word_frequency(text)` method that returns a dict mapping
each unique word to its count (case-insensitive, punctuation-stripped).

Difficulty: MEDIUM
Files: 2 source files + tests
"""

from __future__ import annotations

from models.task import TaskDefinition, TaskDifficulty, TestCase
from tasks.base import BaseTask


class AddFeatureTask(BaseTask):
    """Multi-file feature addition: implement word_frequency() method."""

    TASK_ID = "medium_add_feature"

    def build(self) -> TaskDefinition:
        return TaskDefinition(
            task_id=self.TASK_ID,
            title="Add Word Frequency Feature",
            difficulty=TaskDifficulty.MEDIUM,
            description=(
                "The `TextAnalyzer` class in `/project/analyzer.py` already has "
                "`word_count(text)` and `char_count(text)` methods.\n\n"
                "**Your goal**: Implement the missing `word_frequency(text)` method "
                "that returns a `dict[str, int]` mapping each **unique word** (lowercase, "
                "punctuation stripped) to its occurrence count.\n\n"
                "You may also need to update `/project/utils.py` with a helper function "
                "`clean_word(word: str) -> str` that strips punctuation and lowercases.\n\n"
                "All tests in `/project/tests/test_analyzer.py` must pass."
            ),
            initial_files={
                "/project/analyzer.py": (
                    "from utils import clean_word\n\n"
                    "class TextAnalyzer:\n"
                    "    def word_count(self, text: str) -> int:\n"
                    "        return len(text.split())\n\n"
                    "    def char_count(self, text: str) -> int:\n"
                    "        return len(text.replace(' ', ''))\n\n"
                    "    def word_frequency(self, text: str) -> dict:\n"
                    "        # TODO: implement this method\n"
                    "        raise NotImplementedError('word_frequency not implemented')\n"
                ),
                "/project/utils.py": (
                    "# TODO: implement clean_word(word: str) -> str\n"
                    "# Should strip punctuation and lowercase the word.\n"
                    "def clean_word(word: str) -> str:\n"
                    "    raise NotImplementedError('clean_word not implemented')\n"
                ),
                "/project/tests/test_analyzer.py": (
                    "import sys, os\n"
                    "sys.path.insert(0, '/project')\n"
                    "from analyzer import TextAnalyzer\n\n"
                    "ta = TextAnalyzer()\n\n"
                    "def test_frequency_basic():\n"
                    "    freq = ta.word_frequency('hello world hello')\n"
                    "    assert freq == {'hello': 2, 'world': 1}, f'Got: {freq}'\n\n"
                    "def test_frequency_case_insensitive():\n"
                    "    freq = ta.word_frequency('Hello HELLO hello')\n"
                    "    assert freq == {'hello': 3}, f'Got: {freq}'\n\n"
                    "def test_frequency_punctuation():\n"
                    "    freq = ta.word_frequency('hi, hi! bye.')\n"
                    "    assert freq.get('hi') == 2, f'hi count wrong: {freq}'\n"
                    "    assert freq.get('bye') == 1, f'bye count wrong: {freq}'\n\n"
                    "def test_frequency_empty():\n"
                    "    assert ta.word_frequency('') == {}\n"
                ),
            },
            entry_point="/project/tests/test_analyzer.py",
            seed=2,
            max_steps=30,
            test_cases=[
                TestCase(
                    id="tc_basic_freq",
                    description="Basic word frequency counting",
                    expected_output={"hello": 2, "world": 1},
                    weight=1.0,
                ),
                TestCase(
                    id="tc_case_insensitive",
                    description="Case-insensitive counting",
                    expected_output={"hello": 3},
                    weight=1.0,
                ),
                TestCase(
                    id="tc_punctuation",
                    description="Punctuation stripped correctly",
                    weight=1.5,
                ),
                TestCase(
                    id="tc_empty",
                    description="Empty string returns {}",
                    expected_output={},
                    weight=0.5,
                    is_hidden=True,
                ),
            ],
            hints=[
                "Use str.translate() or re.sub() to strip punctuation.",
                "Remember: clean_word should handle edge cases like empty strings after stripping.",
            ],
            tags=["feature-addition", "strings", "medium"],
        )
