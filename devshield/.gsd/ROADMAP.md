# DevShield — Roadmap

## Milestone 1: Hackathon MVP

---

### Phase 0: Project Setup (Foundation)
**Status**: ⏳ Planned
**Goal**: Initialize full-stack project with scalable architecture

**Must-Haves**:
- [ ] React + Vite + Tailwind frontend scaffold running on port 5173
- [ ] Node.js + Express backend running on port 3001
- [ ] MongoDB connection with User, TaskResult, ScenarioResult schemas
- [ ] JWT register/login endpoints working
- [ ] `.env` config for both frontend and backend

---

### Phase 1: Coding Benchmark (MVP)
**Status**: ⏳ Planned
**Goal**: Full coding task flow — edit code → run tests → get score
**Depends on**: Phase 0

**Must-Haves**:
- [ ] Task engine: tasks stored as JSON with title, description, starterCode, testCases
- [ ] Monaco Editor rendering starter code, editable
- [ ] POST /api/tasks/:id/run → executes user code against test cases → returns { passed, failed, logs }
- [ ] Score display: pass/fail count + percentage
- [ ] child_process sandbox (temp file → node execution → capture output)

---

### Phase 2: Cyber Attack Trainer
**Status**: ⏳ Planned
**Goal**: Interactive decision-based security training
**Depends on**: Phase 0

**Must-Haves**:
- [ ] Phishing email mockup UI (realistic looking email template)
- [ ] Malware alert screen UI
- [ ] System logs view UI
- [ ] Scenario data structure: type, content, correctAction, explanation, riskLevel
- [ ] Multiple-choice decision flow
- [ ] Score assigned: 80-100 correct, 40-70 partial, 0-30 wrong
- [ ] Explanation + risk level shown after choice

---

### Phase 3: Unified Dashboard
**Status**: ⏳ Planned
**Goal**: Combined view of all skills
**Depends on**: Phase 1, Phase 2

**Must-Haves**:
- [ ] Profile page with Coding Score + Security Score
- [ ] Progress bars per skill area
- [ ] Activity history (last 5 coding attempts + last 5 scenarios)
- [ ] Navigation between all sections

---

### Phase 4: AI Enhancement (Optional)
**Status**: ⏳ Planned
**Goal**: Add intelligence layer
**Depends on**: Phase 1, Phase 2

**Must-Haves** (stretch goals):
- [ ] AI code quality review endpoint (calls LLM with user code)
- [ ] Dynamic phishing email generation via LLM
- [ ] Personalized feedback messages
