import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getTasks, getTask, runTask } from '../services/api';
import Editor from '@monaco-editor/react';
import AIReviewPanel from '../components/code/AIReviewPanel';

export default function CodeBenchmark() {
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [code, setCode] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);

  useEffect(() => {
    getTasks().then(setTasks).catch(console.error);
  }, []);

  const handleSelectTask = async (taskId) => {
    setResults(null);
    const fullTask = await getTask(taskId);
    setSelectedTask(fullTask);
    setCode(fullTask.starterCode);
  };

  const handleRunTask = async () => {
    if (!selectedTask) return;
    setIsRunning(true);
    try {
      const res = await runTask(selectedTask.id, code);
      setResults(res);
    } catch (err) {
      console.error(err);
      setResults({ error: 'Execution failed or timed out.' });
    }
    setIsRunning(false);
  };

  return (
    <div className="h-[calc(100vh-64px)] w-full flex bg-[#0f111a] text-gray-200">
      
      {/* LEFT PANEL: Task Description */}
      <div className="w-1/4 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <label className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-2 block">
            Select Challenge
          </label>
          <select 
            className="w-full bg-[#1b1e2e] text-white p-2 rounded border border-gray-700 outline-none"
            onChange={(e) => handleSelectTask(e.target.value)}
            defaultValue=""
          >
            <option value="" disabled>-- Select a task --</option>
            {tasks.map(t => (
              <option key={t.id} value={t.id}>{t.title} ({t.difficulty})</option>
            ))}
          </select>
        </div>

        {selectedTask ? (
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="p-6 flex-1 overflow-y-auto">
            <h2 className="text-2xl font-bold text-white mb-2">{selectedTask.title}</h2>
            <span className={`text-xs px-2 py-1 rounded ${selectedTask.difficulty === 'easy' ? 'bg-green-900/50 text-green-400' : 'bg-yellow-900/50 text-yellow-400'}`}>
              {selectedTask.difficulty.toUpperCase()}
            </span>
            <div className="mt-6 text-gray-300 leading-relaxed text-sm format-markdown">
              {selectedTask.description}
            </div>
            
            <div className="mt-8">
              <h3 className="text-xs text-gray-500 font-bold uppercase tracking-widest mb-3">File Explorer</h3>
              <div className="bg-[#1b1e2e] rounded p-2 text-sm font-mono text-gray-400">
                📁 project/<br/>
                &nbsp;&nbsp;📄 <span className="text-blue-400">solution.js</span>
              </div>
            </div>
          </motion.div>
        ) : (
          <div className="p-6 text-gray-500 text-sm">Select a task above to begin.</div>
        )}
      </div>

      {/* CENTER PANEL: Code Editor */}
      <div className="w-1/2 flex flex-col relative">
        <div className="h-10 border-b border-gray-800 bg-[#161925] flex items-center px-4">
          <span className="text-xs text-gray-400 font-mono">solution.js</span>
        </div>
        <div className="flex-1 bg-[#1b1e2e]">
          {selectedTask ? (
            <Editor
              height="100%"
              defaultLanguage="javascript"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value)}
              options={{ minimap: { enabled: false }, fontSize: 14 }}
            />
          ) : (
            <div className="h-full flex items-center justify-center text-gray-600 font-mono text-sm">
              // Awaiting assignment...
            </div>
          )}
        </div>
        
        {/* Actions Footer */}
        <div className="h-16 border-t border-gray-800 bg-[#0f111a] flex items-center justify-end px-6 gap-4">
          <button 
            onClick={handleRunTask}
            disabled={!selectedTask || isRunning}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isRunning ? '⏳ Running...' : '▶ Run Tests'}
          </button>
          <button 
            disabled={!results || results.failed > 0}
            className="px-6 py-2 bg-green-600 hover:bg-green-500 text-white rounded font-bold transition-all disabled:opacity-20 disabled:cursor-not-allowed"
          >
            Submit Score
          </button>
        </div>
      </div>

      {/* RIGHT PANEL: Test Results */}
      <div className="w-1/4 border-l border-gray-800 bg-[#161925] flex flex-col p-4">
        <h3 className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-4">Execution Results</h3>
        
        {!results && !isRunning && (
          <div className="text-gray-600 text-sm italic text-center mt-20">
            Run your code to see the test results here.
          </div>
        )}

        {isRunning && (
          <div className="flex justify-center mt-20">
            <span className="animate-spin text-4xl">⚙️</span>
          </div>
        )}

        {results && !isRunning && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex-1 overflow-y-auto">
            {results.error ? (
              <div className="p-4 bg-red-900/30 border border-red-800 rounded font-mono text-xs text-red-400 whitespace-pre-wrap">
                {results.error}
              </div>
            ) : (
              <>
                <div className="text-center mb-6">
                  <h1 className={`text-5xl font-black ${results.failed === 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {results.passed}/{results.total}
                  </h1>
                  <span className="text-gray-400 text-sm uppercase tracking-widest mt-2 block">Tests Passed</span>
                </div>

                <div className="space-y-3">
                  {results.results.map((r, i) => (
                    <div key={i} className={`p-3 rounded text-sm ${r.passed ? 'bg-green-900/20 border border-green-800' : 'bg-red-900/20 border border-red-800'}`}>
                      <div className="font-bold mb-1 flex items-center gap-2">
                        {r.passed ? '✅' : '❌'} {r.description}
                      </div>
                      {!r.passed && r.error && (
                        <div className="font-mono text-xs text-red-300 ml-6 bg-black/30 p-2 rounded">
                          {r.error}
                        </div>
                      )}
                      {!r.passed && !r.error && (
                        <div className="font-mono text-xs text-red-300 ml-6">
                          Expected: {JSON.stringify(r.expected)} <br/>
                          Actual: {JSON.stringify(r.actual)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                
                {results.logs && (
                  <div className="mt-8">
                    <h4 className="text-xs text-gray-500 font-bold uppercase mb-2">Console / Stderr</h4>
                    <pre className="bg-[#0f111a] p-3 rounded border border-gray-800 text-xs text-gray-400 overflow-x-auto">
                      {results.logs}
                    </pre>
                  </div>
                )}

                {/* AI Code Review Panel - Show only if tests passed (or always to give feedback) */}
                <div className="mt-8 pb-8">
                   <AIReviewPanel 
                     code={code} 
                     taskId={selectedTask.id} 
                     testResults={{ passed: results.passed, failed: results.failed, total: results.total }} 
                   />
                </div>
              </>
            )}
          </motion.div>
        )}
      </div>

    </div>
  );
}
