"""
Reward Engine — shaped reward computation for OpenEnv CodeAgent.

Reward components
-----------------
1. test_pass_rate  : +1.0 × pass_rate  (max +1.0)
2. bonus_all_pass  : +0.5 if all tests pass (as correctness_bonus)
3. step_penalty    : −0.01 per step taken
4. loop_penalty    : −0.1 per repeated identical action
5. regression_penalty: applied if pass_rate decreased from previous step
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.reward import RewardBreakdown, RewardResult


@dataclass
class RewardConfig:
    """Tunable weights for the reward function."""

    test_pass_weight: float = 1.0
    bonus_all_pass: float = 0.5
    step_penalty: float = 0.01
    loop_penalty: float = 0.1
    regression_penalty: float = 0.2
    max_reward: float = 1.0   # theoretical max
    min_reward: float = 0.0   # floor


class RewardEngine:
    """
    Computes shaped rewards from grader results and state info.

    Parameters
    ----------
    config : RewardConfig
        Reward weights. Defaults are research-calibrated.
    """

    def __init__(self, config: Optional[RewardConfig] = None) -> None:
        self.config = config or RewardConfig()

    def compute(
        self,
        *,
        pass_rate: float,
        prev_pass_rate: float = 0.0,
        step_count: int = 0,
        tests_passed: int = 0,
        tests_total: int = 0,
        repeated_action: bool = False,
        done: bool = False,
        episode_score: float = 0.0,
    ) -> RewardResult:
        """
        Compute the reward for one environment step.

        Parameters
        ----------
        pass_rate :        Current fraction of tests passing (0–1).
        prev_pass_rate :   Pass rate from the previous step.
        step_count :       Current step number (for step penalty).
        tests_passed :     Raw count of passed tests.
        tests_total :      Raw total test count.
        repeated_action :  True if agent repeated the same action as last step.
        done :             True if the episode is terminal.
        episode_score :    Cumulative score to carry forward.

        Returns
        -------
        RewardResult
        """
        cfg = self.config

        # Component 1 — test pass rate (main signal)
        test_rate_component = cfg.test_pass_weight * pass_rate

        # Component 2 — bonus for solving task completely
        correctness_bonus = cfg.bonus_all_pass if (pass_rate >= 1.0 and done) else 0.0

        # Component 3 — per-step penalty
        step_pen = cfg.step_penalty * max(0, step_count)

        # Component 4 — loop detection penalty
        loop_pen = cfg.loop_penalty if repeated_action else 0.0

        # Component 5 — regression penalty
        regression_pen = (
            cfg.regression_penalty * (prev_pass_rate - pass_rate)
            if pass_rate < prev_pass_rate
            else 0.0
        )

        raw_reward = test_rate_component + correctness_bonus - step_pen - loop_pen - regression_pen
        clipped = max(cfg.min_reward, min(cfg.max_reward, raw_reward))

        breakdown = RewardBreakdown(
            test_pass_rate=round(test_rate_component, 4),
            correctness_bonus=round(correctness_bonus, 4),
            step_penalty=round(step_pen, 4),
            loop_penalty=round(loop_pen, 4),
            regression_penalty=round(regression_pen, 4),
        )

        return RewardResult(
            value=round(clipped, 4),
            breakdown=breakdown,
            tests_passed=tests_passed,
            tests_total=tests_total,
            episode_score=round(episode_score + clipped, 4),
        )

    def terminal_reward(
        self,
        pass_rate: float,
        step_count: int,
        tests_passed: int = 0,
        tests_total: int = 0,
        episode_score: float = 0.0,
    ) -> RewardResult:
        """Terminal reward at episode end (no regression, bonus applied if solved)."""
        return self.compute(
            pass_rate=pass_rate,
            prev_pass_rate=pass_rate,
            step_count=step_count,
            tests_passed=tests_passed,
            tests_total=tests_total,
            repeated_action=False,
            done=True,
            episode_score=episode_score,
        )
