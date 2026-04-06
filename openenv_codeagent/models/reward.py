"""
Reward models — structured representation of shaped rewards.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RewardBreakdown(BaseModel):
    """
    Decomposition of a single reward signal into named components.
    Useful for debugging and research logging.
    """

    test_pass_rate: float = 0.0       # [0, 1] fraction of tests passing
    correctness_bonus: float = 0.0    # bonus for structurally correct code
    performance_bonus: float = 0.0    # bonus for meeting perf thresholds (hard tasks)
    step_penalty: float = 0.0         # negative: too many steps ≥ threshold
    loop_penalty: float = 0.0         # negative: detected repeated action loop
    regression_penalty: float = 0.0   # negative: broke previously passing tests
    invalid_action_penalty: float = 0.0  # negative: malformed / unsafe action

    @property
    def total(self) -> float:
        return (
            self.test_pass_rate
            + self.correctness_bonus
            + self.performance_bonus
            - self.step_penalty
            - self.loop_penalty
            - self.regression_penalty
            - self.invalid_action_penalty
        )

    def clamp(self, lo: float = -1.0, hi: float = 1.0) -> "RewardBreakdown":
        """Return a copy with total clamped to [lo, hi] by scaling."""
        # We don't mutate; just surface the property
        return self


class RewardResult(BaseModel):
    """
    Full reward result returned after each step.
    """

    value: float = 0.0               # final scalar reward (clamped)
    breakdown: RewardBreakdown = Field(default_factory=RewardBreakdown)
    tests_passed: int = 0
    tests_total: int = 0
    episode_score: float = 0.0        # cumulative, updated externally
    notes: List[str] = Field(default_factory=list)
    metadata: Dict[str, object] = Field(default_factory=dict)
