---
phase: 0
plan: 3
wave: 2
---

# Plan 0.3: Database Schemas + JWT Auth

## Objective
Create MongoDB schemas (User, TaskResult, ScenarioResult) and implement
JWT-based register/login API endpoints with password hashing.

## Context
- .gsd/SPEC.md
- devshield/server/index.js (Plan 0.2)

## Tasks

<task type="auto">
  <name>Create MongoDB schemas</name>
  <files>
    devshield/server/models/User.js
    devshield/server/models/TaskResult.js
    devshield/server/models/ScenarioResult.js
  </files>
  <action>
    models/User.js — Mongoose schema:
      username: { type: String, required: true, unique: true }
      email: { type: String, required: true, unique: true }
      password: { type: String, required: true }  // hashed
      codingScore: { type: Number, default: 0 }
      securityScore: { type: Number, default: 0 }
      createdAt: { type: Date, default: Date.now }

    models/TaskResult.js:
      userId: { type: ObjectId, ref: 'User' }
      taskId: String
      taskTitle: String
      passed: Number
      failed: Number
      totalTests: Number
      scorePercent: Number
      code: String
      submittedAt: { type: Date, default: Date.now }

    models/ScenarioResult.js:
      userId: { type: ObjectId, ref: 'User' }
      scenarioId: String
      scenarioType: String  // 'phishing' | 'malware' | 'logs'
      userChoice: String
      correctChoice: String
      score: Number        // 0-100
      riskLevel: String
      completedAt: { type: Date, default: Date.now }
  </action>
  <verify>
    node -e "const m = require('./models/User'); console.log(m.schema.paths)"
    → prints schema paths without error
  </verify>
  <done>
    - All 3 model files exist and export Mongoose models
    - No syntax errors on require
    - Foreign key refs correct (ObjectId)
  </done>
</task>

<task type="auto">
  <name>Implement JWT auth endpoints</name>
  <files>
    devshield/server/routes/auth.js
    devshield/server/controllers/authController.js
    devshield/server/services/authService.js
    devshield/server/middleware/authMiddleware.js
    devshield/server/index.js (add route)
  </files>
  <action>
    services/authService.js:
      hashPassword(plain) → bcrypt.hash(plain, 10)
      comparePassword(plain, hash) → bcrypt.compare
      generateToken(userId) → jwt.sign({ userId }, JWT_SECRET, { expiresIn: '7d' })
      verifyToken(token) → jwt.verify(token, JWT_SECRET)

    controllers/authController.js:
      register(req, res):
        - Validate: username, email, password required
        - Check User.findOne({ email }) → 409 if exists
        - hash password, create user, generate token
        - Return: { token, user: { id, username, email, codingScore, securityScore } }

      login(req, res):
        - Find user by email → 401 if not found
        - Compare password → 401 if wrong
        - Generate token
        - Return: { token, user: { id, username, email, codingScore, securityScore } }

    middleware/authMiddleware.js:
      - Extract Bearer token from Authorization header
      - Verify with authService.verifyToken
      - Attach req.userId if valid → call next()
      - 401 if missing or invalid

    routes/auth.js:
      POST /register → authController.register
      POST /login → authController.login

    In index.js: app.use('/api/auth', authRouter)

    In client/src/ create:
      services/api.js — axios instance with baseURL http://localhost:3001/api
        Include interceptor: attach Authorization header from localStorage token

      context/AuthContext.jsx — React context:
        user state, login(token, user), logout()
        Persist token to localStorage

    Wrap App in AuthContext provider in main.jsx.
  </action>
  <verify>
    # Register:
    curl -X POST http://localhost:3001/api/auth/register \
      -H "Content-Type: application/json" \
      -d '{"username":"test","email":"test@test.com","password":"pass123"}'
    → { token: "...", user: { username: "test", ... } }

    # Login:
    curl -X POST http://localhost:3001/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"test@test.com","password":"pass123"}'
    → { token: "...", user: { ... } }

    # Wrong password:
    curl ... with wrong password → 401
  </verify>
  <done>
    - POST /api/auth/register creates user + returns JWT
    - POST /api/auth/login validates + returns JWT
    - Wrong credentials → 401
    - authMiddleware correctly gates protected routes
    - Frontend AuthContext persists token in localStorage
  </done>
</task>
