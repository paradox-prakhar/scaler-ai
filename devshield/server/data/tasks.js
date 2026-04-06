const tasks = [
  {
    id: 'fix-sum-bug',
    title: 'Fix the Sum Bug',
    difficulty: 'easy',
    description: 'The `sumRange` function has an off-by-one error. Fix it so all tests pass.',
    starterCode: `export function sumRange(start, end) {
  let total = 0;
  for (let i = start; i < end; i++) { // BUG: should be <= end
    total += i;
  }
  return total;
}`,
    testCases: [
      { id: 'tc1', input: [1, 5], expected: 15, description: 'sumRange(1,5) == 15' },
      { id: 'tc2', input: [3, 3], expected: 3, description: 'sumRange(3,3) == 3' },
      { id: 'tc3', input: [0, 10], expected: 55, description: 'sumRange(0,10) == 55' },
    ],
    testRunner: `import { sumRange } from './solution.js';
const results = [];
// test cases injected here
console.log(JSON.stringify(results));`
  },
  {
    id: 'palindrome-check',
    title: 'Palindrome Checker',
    difficulty: 'medium',
    description: 'Implement `isPalindrome(str)` that returns true if `str` is a palindrome (ignore case, ignore spaces).',
    starterCode: `export function isPalindrome(str) {
  // TODO: implement
  return false;
}`,
    testCases: [
      { id: 'tc1', input: ["racecar"], expected: true, description: "isPalindrome('racecar')" },
      { id: 'tc2', input: ["hello"], expected: false, description: "isPalindrome('hello')" },
      { id: 'tc3', input: ["A man a plan a canal Panama"], expected: true, description: "isPalindrome('A man a plan a canal Panama')" },
      { id: 'tc4', input: [""], expected: true, description: "isPalindrome('')" },
    ],
    testRunner: `import { isPalindrome } from './solution.js';
const results = [];
// test cases injected here
console.log(JSON.stringify(results));`
  }
];

export default tasks;
