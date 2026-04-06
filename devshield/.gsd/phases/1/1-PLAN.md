---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: Task Engine (Backend)

## Objective
Build the coding task system — seed tasks as JSON, create GET/POST API
endpoints to fetch tasks and execute user code against test cases in a
sandboxed child_process.

## Context
- .gsd/SPEC.md
- devshield/server/index.js

## Tasks

<task type="auto">
  <name>Create task data and engine service</name>
  <files>
    devshield/server/data/tasks.js
    devshield/server/services/taskService.js
    devshield/server/sandbox/executor.js
    devshield/server/routes/tasks.js
    devshield/server/controllers/taskController.js
  </files>
  <action>
    data/tasks.js — export array of task objects:
      Task 1 (easy):
        id: 'fix-sum-bug'
        title: 'Fix the Sum Bug'
        difficulty: 'easy'
        description: 'The sum_range function has an off-by-one error. Fix it so all tests pass.'
        starterCode: |
          function sumRange(start, end) {
            let total = 0;
            for (let i = start; i < end; i++) { // BUG: should be <= end
              total += i;
            }
            return total;
          }
          module.exports = { sumRange };
        testCases: [
          { id: 'tc1', input: [1, 5], expected: 15, description: 'sumRange(1,5) == 15' },
          { id: 'tc2', input: [3, 3], expected: 3, description: 'sumRange(3,3) == 3' },
          { id: 'tc3', input: [0, 10], expected: 55, description: 'sumRange(0,10) == 55' },
        ]
        testRunner: |
          const { sumRange } = require('./solution');
          const results = [];
          // test cases injected here
          module.exports = results;

      Task 2 (medium):
        id: 'palindrome-check'
        title: 'Palindrome Checker'
        difficulty: 'medium'
        description: 'Implement isPalindrome(str) that returns true if str is a palindrome (ignore case, ignore spaces).'
        starterCode: |
          function isPalindrome(str) {
            // TODO: implement
            return false;
          }
          module.exports = { isPalindrome };
        testCases: [
          { input: ['racecar'], expected: true },
          { input: ['hello'], expected: false },
          { input: ['A man a plan a canal Panama'], expected: true },
          { input: [''], expected: true },
        ]

    sandbox/executor.js:
      export async function executeCode(userCode, task):
        1. Create OS temp directory using os.tmpdir()
        2. Write solution file: path.join(tmpDir, 'solution.js') = userCode
        3. Build runner script:
           - require each testCase
           - call the function with testCase.input
           - compare result to expected
           - push { id, passed, actual, expected, error } to results array
           - console.log(JSON.stringify(results))
        4. Write runner.js to tmpDir
        5. Execute: child_process.exec('node runner.js', { cwd: tmpDir, timeout: 5000 })
        6. Parse stdout as JSON → return array of { id, passed, actual, expected }
        7. Clean up temp files
        8. Return { passed: count, failed: count, total: count, results: [...], logs: stderr }
        IMPORTANT: wrap entire execution in try/catch. On SyntaxError or runtime error, 
        return all tests as failed with error message in logs.

    services/taskService.js:
      getAllTasks() → tasks.map(t => ({ id, title, difficulty, description }))
      getTaskById(id) → tasks.find(t => t.id === id) || null

    controllers/taskController.js:
      listTasks(req, res) → res.json(taskService.getAllTasks())
      getTask(req, res) → fetch by id, 404 if not found
      runTask(req, res):
        - get task by id
        - get userCode from req.body.code
        - call executor.executeCode(userCode, task)
        - Save TaskResult to DB (if req.userId set)
        - return result

    routes/tasks.js:
      GET  /              → taskController.listTasks
      GET  /:id           → taskController.getTask
      POST /:id/run       → taskController.runTask (authMiddleware optional)

    In index.js: app.use('/api/tasks', tasksRouter)
  </action>
  <verify>
    # Get tasks list
    curl http://localhost:3001/api/tasks
    → array with 2 tasks

    # Run with correct fix
    curl -X POST http://localhost:3001/api/tasks/fix-sum-bug/run \
      -H "Content-Type: application/json" \
      -d '{"code": "function sumRange(s,e){let t=0;for(let i=s;i<=e;i++)t+=i;return t;} module.exports={sumRange};"}'
    → { passed: 3, failed: 0, total: 3, results: [...] }

    # Run with buggy code (no fix)
    original starter code → { passed: 0 or 1, failed: 2+ }
  </verify>
  <done>
    - GET /api/tasks returns 2 task summaries
    - POST /api/tasks/fix-sum-bug/run with fixed code → passed: 3/3
    - POST with buggy code → some failures
    - Syntax errors in user code → all failed, error in logs
    - No file system residue after execution
  </done>
</task>
