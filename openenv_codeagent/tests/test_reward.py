"""
Unit tests for the Reward Engine.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rewards.reward_engine import RewardConfig, RewardEngine


@pytest.fixture
def engine() -> RewardEngine:
    return RewardEngine()


class TestRewardEngine:
    def test_zero_pass_rate_no_penalty_at_step_zero(self, engine: RewardEngine) -> None:
        result = engine.compute(pass_rate=0.0, step_count=0)
        # 0 test pass, 0 bonus, 0 step pen = 0.0
        assert result.value == pytest.approx(0.0, abs=0.01)

    def test_full_pass_rate_gives_positive_reward(self, engine: RewardEngine) -> None:
        result = engine.compute(pass_rate=1.0, step_count=1)
        assert result.value > 0.0

    def test_solve_bonus_only_at_terminal_with_full_pass(self, engine: RewardEngine) -> None:
        result_done = engine.compute(pass_rate=1.0, step_count=1, done=True)
        result_not_done = engine.compute(pass_rate=1.0, step_count=1, done=False)
        assert result_done.breakdown.correctness_bonus == pytest.approx(0.5, abs=0.001)
        assert result_not_done.breakdown.correctness_bonus == pytest.approx(0.0, abs=0.001)

    def test_step_penalty_accumulates(self, engine: RewardEngine) -> None:
        r1 = engine.compute(pass_rate=0.5, step_count=1)
        r10 = engine.compute(pass_rate=0.5, step_count=10)
        assert r1.value > r10.value

    def test_loop_penalty_reduces_reward(self, engine: RewardEngine) -> None:
        r_normal = engine.compute(pass_rate=0.5, step_count=2, repeated_action=False)
        r_loop = engine.compute(pass_rate=0.5, step_count=2, repeated_action=True)
        assert r_normal.value > r_loop.value

    def test_regression_penalty_applied(self, engine: RewardEngine) -> None:
        r_improved = engine.compute(pass_rate=0.8, prev_pass_rate=0.5, step_count=1)
        r_regressed = engine.compute(pass_rate=0.3, prev_pass_rate=0.8, step_count=1)
        assert r_improved.value > r_regressed.value
        assert r_regressed.breakdown.regression_penalty > 0

    def test_reward_clamped_to_min_max(self, engine: RewardEngine) -> None:
        # Engineer extreme inputs
        r_max = engine.compute(pass_rate=1.0, step_count=0, done=True)
        r_min = engine.compute(pass_rate=0.0, step_count=100, repeated_action=True)
        assert r_max.value <= engine.config.max_reward
        assert r_min.value >= engine.config.min_reward

    def test_episode_score_accumulates(self, engine: RewardEngine) -> None:
        r1 = engine.compute(pass_rate=0.5, step_count=1, episode_score=0.0)
        r2 = engine.compute(pass_rate=0.5, step_count=2, episode_score=r1.episode_score)
        assert r2.episode_score > r1.episode_score

    def test_terminal_reward_marks_done(self, engine: RewardEngine) -> None:
        r = engine.terminal_reward(pass_rate=1.0, step_count=5)
        assert r.breakdown.correctness_bonus == pytest.approx(0.5, abs=0.001)

    def test_custom_config(self) -> None:
        cfg = RewardConfig(test_pass_weight=2.0, bonus_all_pass=0.0)
        eng = RewardEngine(config=cfg)
        r = eng.compute(pass_rate=1.0, step_count=0, done=True)
        # 2.0 * 1.0 + 0.0 = 2.0 (clamped to max_reward=1.5)
        assert r.value == pytest.approx(1.5, abs=0.01)
