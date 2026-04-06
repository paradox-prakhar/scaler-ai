---
phase: 1
plan: 2
wave: 2
---

# Plan 1.2: Code Editor UI (Frontend)

## Objective
Build the Coding Benchmark page: Monaco editor with starter code,
file explorer panel, Run Tests button, and score output panel.
All with animations and dark theme.

## Context
- .gsd/SPEC.md
- devshield/client/src/App.jsx (routing from Plan 0.1)

## Tasks

<task type="auto">
  <name>Build CodeBenchmarkPage with Monaco editor and task panel</name>
  <files>
    devshield/client/src/pages/CodeBenchmarkPage.jsx
    devshield/client/src/components/code/TaskPanel.jsx
    devshield/client/src/components/code/CodeEditor.jsx
    devshield/client/src/components/code/TestResultPanel.jsx
    devshield/client/src/components/code/FileExplorer.jsx
    devshield/client/src/services/api.js (extend)
  </files>
  <action>
    services/api.js — add task methods:
      getTasks() → GET /api/tasks
      getTask(id) → GET /api/tasks/:id
      runTask(id, code) → POST /api/tasks/:id/run with { code }

    CodeBenchmarkPage.jsx layout (3-column):
      LEFT (w-1/4): TaskPanel + FileExplorer
      CENTER (w-1/2): CodeEditor
      RIGHT (w-1/4): TestResultPanel

      State: tasks[], selectedTask, code, testResults, isRunning, isSubmitting

      On mount: fetch tasks list
      On task select: fetch full task → set code to starterCode

    TaskPanel.jsx:
      Show: task selector dropdown (all tasks)
      Selected task details:
        Title + difficulty badge (color coded: easy=green, medium=yellow, hard=red)
        Description (markdown-like, with newlines)
        Hints collapsible section
      Use Framer Motion: slide-in when task changes

    FileExplorer.jsx:
      Mock file tree showing:
        📁 project
           📄 solution.js (clickable, opens in editor)
           📄 package.json (read-only)
      Style: VS Code dark sidebar feel
      Clicking solution.js sets editor to task code

    CodeEditor.jsx:
      Use @monaco-editor/react <Editor>:
        defaultLanguage="javascript"
        theme="vs-dark"
        value={code}
        onChange={(val) => setCode(val)}
        options: fontSize 14, minimap disabled, scrollBeyondLastLine false
      Toolbar above editor:
        Language badge: "JavaScript"
        Keyboard shortcut hint: Ctrl+Enter to run

    TestResultPanel.jsx:
      Shows before run: "Click 'Run Tests' to execute your code"
      After run:
        Score header: "3 / 3 Tests Passed" with big colored number
        Progress bar (green = passed fraction)
        Per-test results list:
          ✅ PASS: sumRange(1,5) = 15
          ❌ FAIL: sumRange(3,3) — Expected 3, got 2
        Console output / stderr in collapsible "Logs" section
      Animate results in with Framer Motion stagger

    Bottom toolbar (below editor, full width):
      Left: "← Select Task"
      Right:
        🧪 Run Tests button (primary, shows spinner when isRunning)
        🚀 Submit button (success variant, disabled until all pass)

    Handle Ctrl+Enter keyboard shortcut → trigger Run Tests

    Add to VITE .env: VITE_API_URL=http://localhost:3001/api
  </action>
  <verify>
    npm run dev
    1. Navigate to /code
    2. Select "Fix the Sum Bug" from dropdown
    3. Monaco editor shows starter code
    4. Click Run Tests → TestResultPanel shows FAIL results
    5. Fix the code (i <= end), click Run Tests → 3/3 PASS
    6. Submit button enables
  </verify>
  <done>
    - Page loads with task list
    - Monaco editor renders and is editable
    - Run Tests calls API and shows results
    - Score panel animates in
    - Buggy code shows failures, fixed code shows 3/3 pass
    - No console errors
  </done>
</task>
