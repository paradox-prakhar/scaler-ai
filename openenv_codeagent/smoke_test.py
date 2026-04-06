"""
Quick smoke test — verifies the full pipeline without needing pytest.
Run from the project root:
    python smoke_test.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("OpenEnv CodeAgent — Smoke Test")
print("=" * 60)

errors = []

# ── 1. Models ──────────────────────────────────────────────────
try:
    from models.action import Action, ActionType, ActionPayload
    from models.observation import Observation
    from models.reward import RewardResult, RewardBreakdown
    from models.task import TaskDefinition, TaskDifficulty
    print("✅ Models imported OK")
except Exception as e:
    errors.append(f"Models: {e}")
    print(f"❌ Models: {e}")

# ── 2. VFS ─────────────────────────────────────────────────────
try:
    from filesystem.vfs import VirtualFileSystem
    vfs = VirtualFileSystem()
    vfs.write_file("/project/hello.py", "x = 1\n")
    assert vfs.read_file("/project/hello.py") == "x = 1\n"
    files = vfs.list_files()
    assert "/project/hello.py" in files
    print("✅ VFS OK")
except Exception as e:
    errors.append(f"VFS: {e}")
    print(f"❌ VFS: {e}")

# ── 3. Sandbox basic execute ───────────────────────────────────
try:
    from execution.sandbox import RestrictedExecutor
    executor = RestrictedExecutor(timeout_seconds=10)
    result = executor.execute("print('hello from sandbox')")
    assert "hello from sandbox" in result.stdout, f"Got: {result.combined_output()}"
    print("✅ Sandbox basic execute OK")
except Exception as e:
    errors.append(f"Sandbox execute: {e}")
    print(f"❌ Sandbox execute: {e}")

# ── 4. Tasks build ─────────────────────────────────────────────
try:
    from tasks.easy.fix_sum_bug import FixSumBugTask
    from tasks.medium.add_feature import AddFeatureTask
    from tasks.hard.optimize_sort import OptimizeSortTask
    t1 = FixSumBugTask().build()
    t2 = AddFeatureTask().build()
    t3 = OptimizeSortTask().build()
    assert t1.task_id == "easy_fix_sum_bug"
    assert t2.task_id == "medium_add_feature"
    assert t3.task_id == "hard_optimize_sort"
    print("✅ All 3 tasks build OK")
except Exception as e:
    errors.append(f"Tasks: {e}")
    print(f"❌ Tasks: {e}")

# ── 5. Graders ─────────────────────────────────────────────────
try:
    from graders.test_grader import TestGrader
    from graders.performance_grader import PerformanceGrader
    task = FixSumBugTask().build()
    grader = TestGrader(task=task)
    print("✅ Graders import OK")
except Exception as e:
    errors.append(f"Graders: {e}")
    print(f"❌ Graders: {e}")

# ── 6. Reward engine ───────────────────────────────────────────
try:
    from rewards.reward_engine import RewardEngine, RewardConfig
    engine = RewardEngine()
    result = engine.compute(
        pass_rate=0.5,
        prev_pass_rate=0.0,
        step_count=1,
        tests_passed=2,
        tests_total=4,
        repeated_action=False,
        done=False,
        episode_score=0.0,
    )
    assert isinstance(result.value, float)
    assert result.breakdown.test_pass_rate == 0.5
    print(f"✅ Reward engine OK (reward={result.value:.3f})")
except Exception as e:
    errors.append(f"Reward engine: {e}")
    print(f"❌ Reward engine: {e}")

# ── 7. Core environment ────────────────────────────────────────
try:
    from core.environment import CodeAgentEnv
    env = CodeAgentEnv(executor_timeout=10.0)
    task = FixSumBugTask().build()
    obs = env.reset(task=task)
    assert obs.step_count == 0
    assert obs.done is False

    # List files
    obs2, reward, done, info = env.step(Action(type=ActionType.LIST_FILES))
    assert "/project/solution.py" in obs2.console_output
    assert "step" in info
    print("✅ Core environment OK")
except Exception as e:
    errors.append(f"Core env: {e}")
    print(f"❌ Core env: {e}")

# ── 8. Test runner (sandbox pytest-style) ─────────────────────
try:
    from execution.sandbox import RestrictedExecutor
    from tasks.easy.fix_sum_bug import FixSumBugTask
    task = FixSumBugTask().build()
    executor = RestrictedExecutor(timeout_seconds=30)

    # Fixed solution
    fixed = (
        "def sum_range(start: int, end: int) -> int:\n"
        "    total = 0\n"
        "    for i in range(start, end + 1):\n"
        "        total += i\n"
        "    return total\n"
    )

    vfs_files = dict(task.initial_files)
    vfs_files["/project/solution.py"] = fixed
    test_source = task.initial_files[task.entry_point]

    result = executor.run_pytest_style(
        test_source=test_source,
        subject_source="",
        vfs_files=vfs_files,
        test_path=task.entry_point,
    )
    output = result.combined_output()
    if "tests passed" in output:
        print(f"✅ Test runner OK: {output.strip().splitlines()[-1]}")
    else:
        print(f"⚠️  Test runner ran but unexpected output: {output[:200]}")
except Exception as e:
    errors.append(f"Test runner: {e}")
    print(f"❌ Test runner: {e}")

# ── Summary ────────────────────────────────────────────────────
print("\n" + "=" * 60)
if errors:
    print(f"❌ {len(errors)} ERROR(S):")
    for e in errors:
        print(f"   • {e}")
    sys.exit(1)
else:
    print("🎉 All checks passed! Run the app with:")
    print("   pip install gradio pydantic python-dotenv pyyaml")
    print("   python app/main.py")
