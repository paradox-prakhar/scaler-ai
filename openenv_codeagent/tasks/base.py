"""
BaseTask — abstract base class for all OpenEnv benchmark tasks.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from models.task import TaskDefinition


class BaseTask(ABC):
    """
    Abstract base class for a benchmark task.

    Subclasses must implement:
    - ``build()`` — returns a fully-populated ``TaskDefinition``.

    Usage
    -----
    >>> task = MyTask()
    >>> defn = task.build()
    >>> env.reset(task=defn)
    """

    @abstractmethod
    def build(self) -> TaskDefinition:
        """Construct and return the TaskDefinition for this task."""
        ...

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def initial_files(self) -> Dict[str, str]:
        """Shortcut to access the task's initial file set."""
        return self.build().initial_files

    def description(self) -> str:
        """Shortcut to access the task's description."""
        return self.build().description
