"""
Action model — typed set of operations the agent can perform.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, model_validator


class ActionType(str, Enum):
    """Enumeration of all valid agent actions."""

    OPEN_FILE = "open_file"
    EDIT_FILE = "edit_file"
    CREATE_FILE = "create_file"
    DELETE_FILE = "delete_file"
    RUN_TESTS = "run_tests"
    EXECUTE_CODE = "execute_code"
    SUBMIT_SOLUTION = "submit_solution"
    RESET = "reset"
    LIST_FILES = "list_files"


class ActionPayload(BaseModel):
    """
    Flexible payload for any action variant.

    Only the fields relevant to the chosen ActionType need to be set.
    """

    # Shared
    path: Optional[str] = None
    content: Optional[str] = None

    # Execute-specific
    code_snippet: Optional[str] = None  # one-off code execution (not file-based)

    # Metadata (optional, for logging)
    comment: Optional[str] = None

    model_config = {"extra": "allow"}  # forward-compatible


class Action(BaseModel):
    """
    A fully-typed agent action.

    Examples
    --------
    >>> Action(type=ActionType.OPEN_FILE, payload=ActionPayload(path="/project/main.py"))
    >>> Action(type=ActionType.EDIT_FILE, payload=ActionPayload(path="/project/main.py", content="..."))
    >>> Action(type=ActionType.RUN_TESTS)
    >>> Action(type=ActionType.SUBMIT_SOLUTION)
    """

    type: ActionType
    payload: ActionPayload = Field(default_factory=ActionPayload)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_payload(self) -> "Action":
        """Enforce required payload fields per action type."""
        t = self.type
        p = self.payload

        if t in (ActionType.OPEN_FILE, ActionType.DELETE_FILE) and not p.path:
            raise ValueError(f"Action '{t}' requires payload.path")

        if t in (ActionType.EDIT_FILE, ActionType.CREATE_FILE):
            if not p.path:
                raise ValueError(f"Action '{t}' requires payload.path")
            if p.content is None:
                raise ValueError(f"Action '{t}' requires payload.content")

        return self

    def to_summary(self) -> str:
        """Short human-readable summary for the observation feed."""
        if self.payload.path:
            return f"{self.type.value}({self.payload.path})"
        return f"{self.type.value}()"
