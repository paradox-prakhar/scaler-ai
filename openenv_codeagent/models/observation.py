"""
Observation model — what the agent sees at each step.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FileNode(BaseModel):
    """Single node in the file tree (file or directory)."""

    name: str
    path: str
    is_dir: bool = False
    children: List["FileNode"] = Field(default_factory=list)
    size_bytes: Optional[int] = None

    model_config = {"frozen": True}


FileNode.model_rebuild()


class FileTree(BaseModel):
    """Full virtual file system snapshot."""

    root: FileNode
    total_files: int = 0
    total_dirs: int = 0

    model_config = {"frozen": True}


class Observation(BaseModel):
    """
    Complete observation returned to the agent at each step.

    Attributes
    ----------
    step_count:     Current step number (0-indexed on reset).
    file_tree:      Snapshot of the virtual file system.
    open_file_path: Path of the currently opened file, if any.
    open_file_content: Content of the currently opened file.
    console_output: Aggregated stdout/stderr from last execution.
    test_results:   Raw test output string from last test run.
    previous_action: Human-readable summary of the last action taken.
    task_description: Full problem statement (always visible).
    done:           Whether the episode has terminated.
    info:           Arbitrary metadata dict (for debugging/logging).
    """

    step_count: int = 0
    file_tree: Optional[FileTree] = None
    open_file_path: Optional[str] = None
    open_file_content: Optional[str] = None
    console_output: str = ""
    test_results: str = ""
    previous_action: str = "None"
    task_description: str = ""
    done: bool = False
    info: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": False}
