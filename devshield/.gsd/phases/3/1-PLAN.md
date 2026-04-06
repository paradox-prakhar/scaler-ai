---
phase: 3
plan: 1
wave: 1
---

# Plan 3.1: Dashboard + Profile Page

## Objective
Build the unified DashboardPage showing combined coding + security scores,
progress visualization, and activity history. Also build the Login/Register UI.

## Context
- .gsd/SPEC.md
- devshield/client/src/ (Phase 0, 1, 2)
- devshield/server/models/ (User, TaskResult, ScenarioResult)

## Tasks

<task type="auto">
  <name>Build Dashboard API endpoints</name>
  <files>
    devshield/server/routes/users.js
    devshield/server/controllers/userController.js
    devshield/server/services/userService.js
  </files>
  <action>
    services/userService.js:
      getProfile(userId):
        - Find user by id
        - Get last 5 TaskResults for userId
        - Get last 5 ScenarioResults for userId
        - Compute avgCodingScore from TaskResults: (passed/total * 100) avg
        - Compute avgSecurityScore from ScenarioResults: avg of score field
        - Return: { user: {username,email,codingScore,securityScore}, 
                    recentTasks: [...], recentScenarios: [...],
                    stats: { avgCodingScore, avgSecurityScore, totalTasksAttempted, totalScenariosAttempted } }

      getLeaderboard():
        - Find top 10 users by (codingScore + securityScore) DESC
        - Return: [{ username, codingScore, securityScore, total }]

    controllers/userController.js:
      getProfile(req, res):
        - Requires auth (authMiddleware)
        - Call userService.getProfile(req.userId)
        - Return profile data

      getLeaderboard(req, res):
        - Call userService.getLeaderboard()
        - Return array

    routes/users.js:
      GET /me          → authMiddleware → getProfile
      GET /leaderboard → getLeaderboard

    In index.js: app.use('/api/users', usersRouter)
  </action>
  <verify>
    # Login first to get token
    TOKEN=$(curl -s -X POST http://localhost:3001/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"test@test.com","password":"pass123"}' | node -e "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>console.log(JSON.parse(d).token))")

    # Get profile
    curl -H "Authorization: Bearer $TOKEN" http://localhost:3001/api/users/me
    → { user: {...}, recentTasks: [], recentScenarios: [], stats: {...} }

    curl http://localhost:3001/api/users/leaderboard
    → array (may be empty if no results yet)
  </verify>
  <done>
    - GET /api/users/me requires auth and returns profile object
    - GET /api/users/leaderboard returns array
    - No auth → 401 for /me
  </done>
</task>

<task type="auto">
  <name>Build DashboardPage + Login/Register UI</name>
  <files>
    devshield/client/src/pages/DashboardPage.jsx
    devshield/client/src/pages/LoginPage.jsx
    devshield/client/src/components/dashboard/ScoreCard.jsx
    devshield/client/src/components/dashboard/ProgressBar.jsx
    devshield/client/src/components/dashboard/ActivityFeed.jsx
    devshield/client/src/components/dashboard/Leaderboard.jsx
    devshield/client/src/components/ui/SkillRadar.jsx
  </files>
  <action>
    LoginPage.jsx:
      Two-tab form: Login | Register (Framer Motion tab indicator)
      Login form: email, password → POST /api/auth/login → save token to AuthContext
      Register form: username, email, password, confirm password → POST /api/auth/register
      On success: redirect to /dashboard
      Error messages shown inline
      Dark glassmorphism card style: bg-dark-card, backdrop-blur

    DashboardPage.jsx:
      If not logged in → show "Please login to view your dashboard" + Link to /login
      If logged in → fetch /api/users/me on mount

      Layout:
        TOP ROW: 2 ScoreCards side by side
          Left: "💻 Coding Score" — big number with trend arrow
          Right: "🛡 Security Score" — big number with trend arrow

        MIDDLE ROW: 2 ProgressBars
          Coding skill breakdown:
            "Code Correctness" bar (based on avgCodingScore)
            "Tasks Completed" bar
          Security skill:
            "Threat Detection" bar (based on avgSecurityScore)
            "Scenarios Completed" bar

        BOTTOM ROW: 2 panels
          Left: ActivityFeed — recent tasks + scenarios
          Right: Leaderboard

    ScoreCard.jsx:
      Props: title, score, icon, color, subtitle
      Animated counter (count up from 0 to score on mount)
      Glassmorphism card with colored glow border

    ProgressBar.jsx:
      Props: label, value (0-100), color
      Animated fill (spring animation via Framer Motion)
      Shows percentage label at right end

    ActivityFeed.jsx:
      Props: recentTasks, recentScenarios
      Merged, sorted by date list
      Each item: icon + title + score + date
      Coding item: 💻 Task name — X/Y passed
      Security item: 🛡 Scenario name — score%

    Leaderboard.jsx:
      Props: leaderboard array
      Table with: Rank | Username | Coding | Security | Total
      Top 3 get 🥇🥈🥉 emoji
      Current user's row highlighted

    Update Navbar:
      If logged in: show "👤 username" + "Logout" button
      If not: show "Login" button
  </action>
  <verify>
    npm run dev
    1. Navigate to /login → login form renders
    2. Register a new user → redirected to /dashboard
    3. Dashboard shows score cards (0,0 for new user)
    4. Progress bars render and animate on load
    5. Complete a coding task → refresh dashboard → scores update
    6. Leaderboard shows registered users
  </verify>
  <done>
    - Login and register both work end-to-end
    - Dashboard shows real data from API
    - Score cards animate (count-up effect)
    - Progress bars animate on load
    - Navbar shows username when logged in
    - Logout clears auth state
  </done>
</task>
