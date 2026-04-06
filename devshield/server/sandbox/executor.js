import fs from 'fs/promises';
import os from 'os';
import path from 'path';
import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

export async function executeCode(userCode, task) {
  // 1. Create OS temp directory
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'ds-run-'));
  const solutionPath = path.join(tmpDir, 'solution.js');
  const runnerPath = path.join(tmpDir, 'runner.js');

  try {
    // 2. Write solution file
    await fs.writeFile(solutionPath, userCode, 'utf8');

    // 3. Build runner script dynamically
    let injectedTests = task.testCases.map((tc) => {
      // Create a string representation of the inputs to pass to the function
      return `
  try {
    const actual = ${task.id === 'palindrome-check' ? 'isPalindrome' : 'sumRange'}(...${JSON.stringify(tc.input)});
    const expected = ${JSON.stringify(tc.expected)};
    const passed = JSON.stringify(actual) === JSON.stringify(expected);
    results.push({ id: "${tc.id}", description: "${tc.description}", passed, actual, expected });
  } catch (err) {
    results.push({ id: "${tc.id}", description: "${tc.description}", passed: false, actual: null, expected: ${JSON.stringify(tc.expected)}, error: err.message });
  }
`;
    }).join('\n');

    let runnerContent = task.testRunner.replace('// test cases injected here', injectedTests);
    
    // Add dummy package.json to enable ES modules in the tmp dir
    await fs.writeFile(path.join(tmpDir, 'package.json'), JSON.stringify({ type: "module" }), 'utf8');
    await fs.writeFile(runnerPath, runnerContent, 'utf8');

    // 5. Execute code
    try {
      const { stdout, stderr } = await execPromise(`node runner.js`, { cwd: tmpDir, timeout: 5000 });
      let results = [];
      try {
        results = JSON.parse(stdout);
      } catch (e) {
        // Output wasn't pure JSON
      }
      
      const passedCount = results.filter(r => r.passed).length;
      return {
        passed: passedCount,
        failed: results.length - passedCount,
        total: results.length,
        results,
        logs: stderr || null
      };

    } catch (execError) {
      // This happens on runtime error or syntax error inside require('./solution')
      return {
        passed: 0,
        failed: task.testCases.length,
        total: task.testCases.length,
        results: task.testCases.map(tc => ({ id: tc.id, description: tc.description, passed: false, error: "Execution Failed" })),
        logs: execError.stderr || execError.message
      };
    }

  } finally {
    // 7. Cleanup
    try {
      await fs.rm(tmpDir, { recursive: true, force: true });
    } catch (e) {
      console.error('Failed to cleanup tmp folder', e);
    }
  }
}
