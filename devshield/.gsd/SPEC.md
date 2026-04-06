# DevShield — Project Specification
**Status: FINALIZED**

---

## Project Overview

**DevShield** is a dual-purpose hackathon platform that:
1. **Benchmarks AI coding agents** — gives AI a broken codebase, scores its fix
2. **Trains humans in cybersecurity** — interactive phishing/malware scenario trainer

Both tools share a unified dashboard showing skill progression.

---

## Target Users

- **Developers** who want to evaluate AI coding tools
- **Students / Employees** who need security awareness training
- **Hackathon judges** — need a compelling live demo

---

## Core Value Proposition

> One platform to benchmark AI coding quality AND train humans in cybersecurity.

---

## Tech Stack (DECIDED)

### Frontend
- **React** via **Vite**
- **Tailwind CSS** for styling
- **Monaco Editor** for code editing
- **Framer Motion** for animations
- **Axios** for HTTP calls

### Backend
- **Node.js + Express**
- Structure: `/routes`, `/controllers`, `/services`, `/sandbox`, `/models`

### Database
- **MongoDB** (via Mongoose)
- Collections: `User`, `TaskResult`, `ScenarioResult`

### Auth
- **JWT** (JSON Web Tokens) — login + register

---

## Features by Phase

### Phase 0 — Foundation
- Vite + React + Tailwind scaffold
- Express server with folder structure
- MongoDB connection + schemas
- JWT auth (register/login)
- `.env` config

### Phase 1 — Coding Benchmark (MVP)
- Task panel: description + Monaco editor + file explorer
- Run Tests button → sandbox execution → score output
- Task stored as JSON with test cases
- Scoring: passed/failed/logs

### Phase 2 — Cyber Attack Trainer
- Phishing email mockup UI
- Malware alert screen UI
- System logs view
- Decision engine (multiple choice)
- Score: 0–100 based on correctness
- AI-generated explanation (optional)

### Phase 3 — Unified Dashboard
- Profile page: Coding Score + Security Score
- Progress bars for skill areas
- Activity history
- Optional: Leaderboard

### Phase 4 — AI Enhancement (optional)
- AI code quality review
- Dynamic scenario generation
- Personalized feedback suggestions

---

## Hackathon Demo Flow (Minimum Viable Demo)

1. Open coding task → edit code → run tests → see score
2. Open phishing scenario → choose action → get feedback
3. View dashboard → compare both skills

---

## Non-Goals (for hackathon scope)
- Real Docker sandboxing (use child_process instead)
- OAuth / social login
- Mobile responsiveness (desktop-first)
- Real-time collaboration

---

## Success Metrics
- All 3 demo flows work end-to-end
- UI is polished and impressive to judges
- No crashes during 5-minute demo
