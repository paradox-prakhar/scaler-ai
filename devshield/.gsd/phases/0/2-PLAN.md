---
phase: 0
plan: 2
wave: 1
---

# Plan 0.2: Backend Scaffold

## Objective
Initialize the Node.js + Express backend with the full folder structure,
basic health check, and CORS + JSON middleware ready for API routes.

## Context
- .gsd/SPEC.md

## Tasks

<task type="auto">
  <name>Scaffold Express server with folder structure</name>
  <files>
    devshield/server/
    devshield/server/index.js
    devshield/server/routes/
    devshield/server/controllers/
    devshield/server/services/
    devshield/server/sandbox/
    devshield/server/models/
    devshield/server/.env
    devshield/server/package.json
  </files>
  <action>
    In devshield/server/:
      npm init -y
      npm install express mongoose dotenv cors bcryptjs jsonwebtoken

    Create devshield/server/.env:
      PORT=3001
      MONGO_URI=mongodb://localhost:27017/devshield
      JWT_SECRET=devshield_secret_change_in_prod
      NODE_ENV=development

    Create devshield/server/index.js:
      - import express, cors, dotenv, mongoose
      - dotenv.config()
      - const app = express()
      - app.use(cors({ origin: 'http://localhost:5173' }))
      - app.use(express.json())
      - GET /api/health → { status: 'ok', timestamp: new Date() }
      - mongoose.connect(process.env.MONGO_URI) with console log
      - app.listen(process.env.PORT)

    Create empty index.js files in each folder:
      routes/, controllers/, services/, sandbox/, models/

    Add to package.json scripts:
      "dev": "node --watch index.js"
      "start": "node index.js"
  </action>
  <verify>
    cd devshield/server && npm run dev
    curl http://localhost:3001/api/health
    → should return { status: 'ok', timestamp: '...' }
  </verify>
  <done>
    - Server starts on port 3001 without errors
    - /api/health returns 200 JSON
    - All 5 subdirectories exist
    - .env loaded (PORT used correctly)
  </done>
</task>
