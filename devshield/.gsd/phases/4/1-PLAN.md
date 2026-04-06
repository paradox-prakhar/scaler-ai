---
phase: 4
plan: 1
wave: 1
---

# Plan 4.1: AI Enhancement (Stretch Goal)

## Objective
Add an AI layer: code quality review using an LLM (OpenAI/Groq),
dynamic phishing email generation, and personalized feedback messages.
Only attempt if Phases 0-3 are demo-ready with time remaining.

## Context
- .gsd/SPEC.md
- devshield/server/ (Phase 0-3)

## Tasks

<task type="auto">
  <name>AI code review endpoint</name>
  <files>
    devshield/server/services/aiService.js
    devshield/server/routes/ai.js
    devshield/server/controllers/aiController.js
    devshield/client/src/components/code/AIReviewPanel.jsx
  </files>
  <action>
    npm install openai (in server/)
    Add to .env: OPENAI_API_KEY=your_key_here  (or use GROQ_API_KEY with groq-sdk)

    services/aiService.js:
      reviewCode(code, taskDescription, testResults):
        Build prompt:
          "You are a code reviewer. The user attempted this task: {taskDescription}.
           Their code: ```js\n{code}\n```
           Test results: passed {passed}/{total}.
           Give CONCISE feedback (3-4 bullet points max):
           1. What they did right
           2. What could be improved (efficiency, readability, edge cases)
           3. One specific tip
           Format as JSON: { strengths: [...], improvements: [...], tip: '...' }"
        Call OpenAI chat completion (gpt-3.5-turbo for speed/cost)
        Parse JSON response → return { strengths, improvements, tip }

      generatePhishingEmail():
        Prompt: "Generate a realistic phishing email scenario for security training.
                 Return JSON: { from, subject, body, indicators: [list of red flags],
                 correctAction: 'C', explanation: '...' }"
        Return parsed JSON

    controllers/aiController.js:
      reviewCode(req, res):
        - Get code, taskId, testResults from body
        - Get task from taskService
        - Call aiService.reviewCode
        - Return { review: { strengths, improvements, tip } }

      generateScenario(req, res):
        - Call aiService.generatePhishingEmail
        - Format as scenario object
        - Return it

    routes/ai.js:
      POST /review → reviewCode
      POST /generate-scenario → generateScenario

    In index.js: app.use('/api/ai', aiRouter)

    AIReviewPanel.jsx (client):
      Shown below TestResultPanel after tests pass
      "🤖 Get AI Review" button
      Loading spinner while fetching
      Shows:
        ✅ Strengths section (green bullets)
        💡 Improvements section (yellow bullets)
        🎯 Pro Tip (purple card)
      Animate in with Framer Motion slide-up
  </action>
  <verify>
    curl -X POST http://localhost:3001/api/ai/review \
      -H "Content-Type: application/json" \
      -d '{"code":"function sumRange(s,e){let t=0;for(let i=s;i<=e;i++)t+=i;return t;}","taskId":"fix-sum-bug","testResults":{"passed":3,"failed":0}}'
    → { review: { strengths: [...], improvements: [...], tip: '...' } }
  </verify>
  <done>
    - POST /api/ai/review returns structured feedback
    - AIReviewPanel renders after tests pass
    - Feedback has 3 sections: strengths, improvements, tip
    - Graceful error if API key missing (show "AI review unavailable")
  </done>
</task>
