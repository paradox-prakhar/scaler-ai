---
phase: 2
plan: 2
wave: 2
---

# Plan 2.2: Security Trainer UI (Frontend)

## Objective
Build the SecurityTrainerPage with 3 distinct scenario UIs: phishing email,
malware alert, and log viewer. Each renders its scenario type appropriately,
collects the user's decision, and shows animated feedback.

## Context
- .gsd/SPEC.md
- devshield/client/src/App.jsx
- Phase 2 Plan 2.1 (scenario API)

## Tasks

<task type="auto">
  <name>Build SecurityTrainerPage with scenario UIs and feedback</name>
  <files>
    devshield/client/src/pages/SecurityTrainerPage.jsx
    devshield/client/src/components/security/ScenarioSelector.jsx
    devshield/client/src/components/security/PhishingEmailView.jsx
    devshield/client/src/components/security/MalwareAlertView.jsx
    devshield/client/src/components/security/LogsView.jsx
    devshield/client/src/components/security/DecisionPanel.jsx
    devshield/client/src/components/security/FeedbackPanel.jsx
    devshield/client/src/services/api.js (extend)
  </files>
  <action>
    services/api.js — add scenario methods:
      getScenarios() → GET /api/scenarios
      getScenario(id) → GET /api/scenarios/:id
      submitDecision(id, choice) → POST /api/scenarios/:id/submit with { choice }

    SecurityTrainerPage.jsx:
      State: scenarios[], selectedScenario, currentView (null | 'scenario' | 'feedback'),
             userChoice, result, isSubmitting

      Layout:
        Left panel (w-1/3): ScenarioSelector — list of scenarios with type badges
        Right panel (w-2/3):
          if currentView === null → welcome screen "Choose a scenario to begin"
          if currentView === 'scenario' → render scenario-specific component + DecisionPanel
          if currentView === 'feedback' → FeedbackPanel

      On scenario select: fetch full scenario data → show in right panel

    ScenarioSelector.jsx:
      List of scenarios with:
        Icon: 📧 phishing, ⚠️ malware, 📜 logs
        Title
        Risk badge: critical=red, high=orange, medium=yellow
        Glow border on hover (Framer Motion)

    PhishingEmailView.jsx:
      Render a REALISTIC email client mockup:
        Gray/white email container (on dark page — contrast!)
        Header row: From field, Subject line, timestamp
        Email body text (as HTML-safe text)
        "Suspicious link" rendered as a blue underlined text (NOT a real link)
        Red indicator dots over the phishing clues (hover reveals what the clue is)
        Label above: "⚠️ Security Scenario — This email may be suspicious"

    MalwareAlertView.jsx:
      Full-width warning popup mockup:
        Red border, flashing/pulsing effect (Framer Motion pulse animation)
        Warning icon ⚠️ big
        Alert type bold header in red
        Message text
        Fake "Call Now" button (greyed out, not clickable, label "DO NOT CLICK")
        Source shown at bottom

    LogsView.jsx:
      Terminal-style log viewer:
        Black background, monospace font
        Each log line rendered as text
        Suspicious lines highlighted in red/orange (lines with 'Failed', 'shadow', 'passwd')
        Timestamp, log level, message columns

    DecisionPanel.jsx:
      Below the scenario view:
        "What would you do?" header
        4 option buttons (A, B, C, D) with the option text
        Clicking selects it (highlights in purple), other options dim
        Confirm Choice button → calls submitDecision → sets FeedbackPanel
        Animate buttons in with stagger (Framer Motion)

    FeedbackPanel.jsx:
      Animated reveal (scale in):
        Score circle: big number (0–100) with color (green ≥ 80, orange 40-79, red < 40)
        Grade label: "Excellent" / "Partial" / "Incorrect"
        isCorrect banner: ✅ Correct Choice! or ❌ Incorrect Choice
        Correct answer shown: "The best action was: C — [option text]"
        Explanation card: full explanation text
        Risk level badge
        "Try Another Scenario" button → reset state
  </action>
  <verify>
    npm run dev → navigate to /security
    1. Scenario list on left loads
    2. Click "Suspicious Bank Email" → phishing email UI renders on right
    3. Select option C → confirm → FeedbackPanel shows score 90, "Excellent"
    4. Select option A on another attempt → FeedbackPanel shows score 15, "Incorrect"
    5. Click malware alert scenario → MalwareAlertView renders with pulse animation
    6. Click logs scenario → terminal-style log view renders
  </verify>
  <done>
    - All 3 scenario types render distinct, realistic UIs
    - DecisionPanel collects choice and submits to API
    - FeedbackPanel shows score, grade, explanation
    - Correct → green score, Incorrect → red score
    - Animations work (scale-in, stagger on buttons)
    - No page reload needed between scenarios
  </done>
</task>
