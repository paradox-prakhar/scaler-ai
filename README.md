# 🛡️ DevShield — Hackathon Platform

![React Badge](https://img.shields.io/badge/Frontend-React%20%7C%20Vite-blue)
![Node Badge](https://img.shields.io/badge/Backend-Node.js%20%7C%20Express-green)
![MongoDB Badge](https://img.shields.io/badge/Database-MongoDB-brightgreen)
![Python Sandbox](https://img.shields.io/badge/Sandbox-Python%20%7C%20OpenEnv-yellow)

**DevShield** is a dual-purpose hackathon platform built simultaneously to benchmark AI coding agents against vulnerable codebases and train humans in interactive cybersecurity threat detection.

---

## 🌟 Core Value Proposition

> **One unified platform to benchmark AI coding quality AND train humans in cybersecurity.**

The DevShield ecosystem comprises two distinct yet deeply integrated engines:
1. **`openenv_codeagent`**: A robust, headless AI benchmarking suite configured to restrict evaluation to a 0.0–1.0 reward scale with precise execution isolation.
2. **`devshield` (MERN Stack)**: The full-stack platform managing users, interactive phishing/malware simulations, coding task IDE wrappers, and cross-discipline scoring.

---

## 🛠️ Key Features

### 1. Coding Benchmark (MVP)
Evaluate AI coding efficiency or test yourself with an integrated sandbox environment:
- **Monaco Editor Widget**: Integrated code viewing and manipulation.
- **Automated Grading Sandbox**: Executes user/AI submissions invisibly.
- **Standardized Execution**: Wraps code execution inside `child_process` and Python restricted environments for safe evaluation.

### 2. Cyber Attack Trainer (Security Scenarios)
A gamified human-evaluation mode to detect non-coding vulnerabilities:
- **Phishing Mockups**: Realistic malicious email templates designed to test user vigilance.
- **Malware Alerts & Logs View**: Dive deep into system execution logs to verify legitimacy.
- **Dynamic Decision Scoring**: Assigns point-weighted rewards based on threat remediation accuracy.

### 3. Unified Developer Dashboard
- **Consolidated Scoring**: Profiles merge an AI Coding rating with a Human Security rating.
- **Skill Progressions**: Track individual skill improvement across disparate vulnerability vectors.
- **History Analytics**: View logs of automated baseline test attempts alongside human task scores.

---

## 🏗️ Technology Stack

### Application Layer (`devshield`)
* **Frontend**: React (via Vite) optimized for speed, styled with Tailwind CSS, and powered by Framer Motion and Monaco.
* **Backend**: Node.js + Express with modular routing (`/sandbox`, `/services`, `/models`).
* **Database**: MongoDB (Mongoose) storing `User`, `TaskResult`, and `ScenarioResult` logs.
* **Security**: JWT-based authentication protocol for user profiles.

### Benchmarking Layer (`openenv_codeagent`)
* **Execution**: Secure Python restricted execution environment with VFS mapping for task repositories.
* **LLM Engine**: OpenAI Client integrated baseline agent (`inference.py`) passing structured logs via `[START]`, `[STEP]`, and `[END]`.

---

## 🚀 Getting Started

Follow these steps to deploy the full dual-engine stack locally.

### Prerequisites
* Node.js (v18+)
* npm or yarn
* Python (3.9+)
* MongoDB connection string (local or Atlas)

### 1. Running the Backend Server
```bash
cd devshield/server
npm install
npm run dev
```
*(Runs on `localhost:3001` - ensure you configure your `.env` with `MONGO_URI` and `JWT_SECRET`).*

### 2. Running the Frontend Dashboard
```bash
cd devshield/client
npm install
npm run dev
```
*(Runs on `localhost:5173`).*

### 3. Validating the Sandbox (OpenEnv)
```bash
cd openenv_codeagent
pip install -r requirements.txt
python smoke_test.py
```
*(Verify that `API_BASE_URL` and `HF_TOKEN` are set in your `.env`).*

---

## 🎯 Hackathon Demo Flow (For Judges)

1. **Authentication**: Register/Login to the system to load your personalized Dashboard.
2. **Benchmark Task**: Open the coding task view, edit the broken Python/JS code in the Monaco editor, and hit "Run Tests" to capture a 0.0-1.0 sandbox score.
3. **Security Trainer**: Navigate to the Phishing Scenario interface. Review the mock email, analyze the risk vectors, and choose an action.
4. **Compare & Review**: Return to the Unified Dashboard to see both your Coding Score and Security Score updated in real-time on your progress indicators.

---

*Authored for the DevShield Hackathon.*
