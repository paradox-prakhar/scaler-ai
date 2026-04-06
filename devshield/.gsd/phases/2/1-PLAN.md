---
phase: 2
plan: 1
wave: 1
---

# Plan 2.1: Scenario Data + Engine (Backend)

## Objective
Build the cyber scenario engine: seed scenario data (phishing, malware, logs),
create GET/POST API endpoints, and implement the decision scoring logic.

## Context
- .gsd/SPEC.md
- devshield/server/ (Phase 0)

## Tasks

<task type="auto">
  <name>Create scenario data and scoring engine</name>
  <files>
    devshield/server/data/scenarios.js
    devshield/server/services/scenarioService.js
    devshield/server/controllers/scenarioController.js
    devshield/server/routes/scenarios.js
  </files>
  <action>
    data/scenarios.js — export array of scenario objects:

      Scenario 1 (phishing):
        id: 'phishing-bank'
        type: 'phishing'
        riskLevel: 'high'
        title: 'Suspicious Bank Email'
        content:
          from: 'security@bank-secure-alert.com'
          subject: 'URGENT: Your account has been compromised!'
          body: 'Dear Customer, We detected unusual activity. Click HERE immediately to verify your account or it will be suspended in 24 hours. [Verify Account]'
          timestamp: '2024-01-15 09:42'
          indicators: ['urgent language', 'suspicious sender domain', 'generic greeting', 'suspicious link']
        options: [
          { id: 'A', text: 'Click the link and verify your account' },
          { id: 'B', text: 'Delete the email and ignore it' },
          { id: 'C', text: 'Forward to IT security and mark as phishing' },
          { id: 'D', text: 'Reply asking for more information' },
        ]
        correctAction: 'C'
        partialActions: ['B']  // gets partial credit
        explanation: 'This is a phishing email. Red flags: suspicious domain (bank-secure-alert.com is NOT your bank), urgent/threatening language, generic greeting. Always report to IT — deleting is better than clicking but reporting helps protect others.'

      Scenario 2 (malware):
        id: 'malware-alert'
        type: 'malware'
        riskLevel: 'critical'
        title: 'Antivirus Alert Popup'
        content:
          alertType: 'CRITICAL SYSTEM WARNING'
          message: 'Your computer is infected with 47 viruses! Call Microsoft Support NOW: 1-800-XXX-XXXX to fix immediately!'
          source: 'Pop-up window (browser)'
        options: [
          { id: 'A', text: 'Call the phone number immediately' },
          { id: 'B', text: 'Close the browser tab / window' },
          { id: 'C', text: 'Download the "fix" software shown' },
          { id: 'D', text: 'Run a scan with your actual antivirus' },
        ]
        correctAction: 'D'
        partialActions: ['B']
        explanation: 'This is a scareware/tech support scam. Microsoft never contacts you via browser popups with phone numbers. Close the browser first (don\'t call the number), then run your real antivirus software.'

      Scenario 3 (logs):
        id: 'suspicious-logs'
        type: 'logs'
        riskLevel: 'medium'
        title: 'Review These System Logs'
        content:
          logs: [
            '2024-01-15 02:14:22 [AUTH] Failed login for user admin from 185.220.101.5',
            '2024-01-15 02:14:23 [AUTH] Failed login for user admin from 185.220.101.5',
            '2024-01-15 02:14:24 [AUTH] Failed login for user admin from 185.220.101.5',
            '2024-01-15 02:14:25 [AUTH] Successful login for user admin from 185.220.101.5',
            '2024-01-15 02:14:26 [FILE] admin accessed /etc/passwd',
            '2024-01-15 02:14:27 [FILE] admin accessed /etc/shadow',
          ]
        options: [
          { id: 'A', text: 'This is normal activity, no action needed' },
          { id: 'B', text: 'Reset the admin password' },
          { id: 'C', text: 'Block the IP, reset admin credentials, and alert security team' },
          { id: 'D', text: 'Delete the logs to hide the breach' },
        ]
        correctAction: 'C'
        explanation: 'This shows a brute-force attack followed by successful unauthorized access. The attacker accessed sensitive system files (/etc/passwd, /etc/shadow). Full incident response is required: block IP, reset credentials, alert security team, preserve logs for forensics.'

    services/scenarioService.js:
      getAllScenarios() → scenarios.map(s => ({ id, type, riskLevel, title }))
      getScenarioById(id) → scenarios.find(s => s.id === id) || null
      scoreDecision(scenario, userChoice):
        if userChoice === scenario.correctAction → { score: 90, grade: 'Excellent' }
        if scenario.partialActions.includes(userChoice) → { score: 55, grade: 'Partial' }
        else → { score: 15, grade: 'Incorrect' }
        return { score, grade, isCorrect, explanation: scenario.explanation, correctAction, riskLevel }

    controllers/scenarioController.js:
      listScenarios(req, res) → scenarioService.getAllScenarios()
      getScenario(req, res):
        - fetch by id, 404 if not found
        - return scenario WITHOUT correctAction and partialActions exposed
      submitDecision(req, res):
        - get scenario by id
        - validate req.body.choice is A/B/C/D
        - call scenarioService.scoreDecision
        - save ScenarioResult to DB if authenticated
        - return { score, grade, isCorrect, explanation, correctAction, riskLevel }

    routes/scenarios.js:
      GET  /          → listScenarios
      GET  /:id       → getScenario
      POST /:id/submit → submitDecision

    In index.js: app.use('/api/scenarios', scenariosRouter)
  </action>
  <verify>
    curl http://localhost:3001/api/scenarios
    → 3 scenario summaries

    curl http://localhost:3001/api/scenarios/phishing-bank
    → full scenario WITHOUT correctAction field

    curl -X POST http://localhost:3001/api/scenarios/phishing-bank/submit \
      -H "Content-Type: application/json" -d '{"choice":"C"}'
    → { score: 90, grade: 'Excellent', isCorrect: true, explanation: '...', riskLevel: 'high' }

    curl ... with choice "A"
    → { score: 15, grade: 'Incorrect', isCorrect: false, ... }
  </verify>
  <done>
    - GET /api/scenarios returns 3 items
    - correctAction NOT exposed in getScenario response
    - Correct answer → score 90, wrong → score 15, partial → score 55
    - All scenarios have explanation returned after submit
  </done>
</task>
