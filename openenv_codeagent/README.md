# OpenEnv CodeAgent

> **A production-grade, research-level benchmark environment where AI agents solve real software engineering tasks inside a simulated codebase.**

[![HuggingFace Spaces](https://img.shields.io/badge/🤗-HuggingFace%20Spaces-yellow)](https://huggingface.co/spaces)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch Gradio UI
python app/main.py

# 3. Run baseline agent (requires OPENAI_API_KEY)
export OPENAI_API_KEY=sk-...
python scripts/baseline_agent.py --task easy_fix_sum_bug

# 4. Run full benchmark
python scripts/evaluate.py --output results/benchmark.json
```

---

## 🏗️ Architecture

```
openenv_codeagent/
├── models/              # Pydantic schemas (Observation, Action, Reward, Task)
├── filesystem/          # In-memory VFS with version tracking + rollback
├── execution/           # RestrictedPython sandbox (subprocess-isolated)
├── tasks/               # Benchmark task definitions
│   ├── easy/            # fix_sum_bug.py
│   ├── medium/          # add_feature.py
│   └── hard/            # optimize_sort.py
├── graders/             # TestGrader + PerformanceGrader
├── rewards/             # Shaped reward engine
├── core/                # CodeAgentEnv (gym-style)
├── scripts/             # baseline_agent.py + evaluate.py
├── app/                 # Gradio UI (HF Spaces deployable)
└── tests/               # Unit test suite
```

---

## 🎯 Benchmark Tasks

| ID | Difficulty | Description |
|----|-----------|-------------|
| `easy_fix_sum_bug` | 🟢 Easy | Fix an off-by-one bug in `sum_range()` |
| `medium_add_feature` | 🟡 Medium | Implement `word_frequency()` in a multi-file project |
| `hard_optimize_sort` | 🔴 Hard | Fix a sort bug + optimize from O(n²) to O(n log n) |

---

## 🤖 Agent API

```python
from core.environment import CodeAgentEnv
from models.action import Action, ActionType, ActionPayload
from tasks.easy.fix_sum_bug import FixSumBugTask

env = CodeAgentEnv()
obs = env.reset(task=FixSumBugTask().build())

# Take a step
action = Action(
    type=ActionType.EDIT_FILE,
    payload=ActionPayload(
        path="/project/solution.py",
        content='def sum_range(start, end):\n    return sum(range(start, end + 1))\n'
    )
)
obs, reward, done, info = env.step(action)

print(f"Reward: {reward:.3f} | Pass: {info['pass_rate']:.0%} | Done: {done}")
```

---

## 🏆 Reward Function

| Component | Formula | Max |
|-----------|---------|-----|
| Test pass rate | `1.0 × pass_rate` | +1.0 |
| Solve bonus | `+0.5` if all pass on submit | +0.5 |
| Step penalty | `−0.01 × steps` | — |
| Loop penalty | `−0.1` if repeated action | — |
| Regression penalty | `−0.2 × Δpass_rate` (if decreased) | — |

---

## 🧪 Running Tests

```bash
cd Newscaler/openenv_codeagent
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## 🐳 Docker / HuggingFace Spaces Deployment

```bash
docker build -t openenv .
docker run -p 7860:7860 -e OPENAI_API_KEY=sk-... openenv
```

Or push directly to a HuggingFace Space with `sdk: docker`.

---

## 📄 License

MIT © 2024 OpenEnv CodeAgent Contributors
