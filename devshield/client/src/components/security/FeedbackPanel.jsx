import React from 'react';
import { motion } from 'framer-motion';

export default function FeedbackPanel({ result, onReset }) {
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-500 border-green-500 shadow-[0_0_30px_rgba(34,197,94,0.3)]';
    if (score >= 50) return 'text-yellow-500 border-yellow-500 shadow-[0_0_30px_rgba(234,179,8,0.3)]';
    return 'text-red-500 border-red-500 shadow-[0_0_30px_rgba(239,68,68,0.3)]';
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="p-8 h-full overflow-y-auto flex flex-col items-center justify-center"
    >
      <div className={`w-32 h-32 rounded-full border-4 flex items-center justify-center mb-6 bg-[#0f111a] ${getScoreColor(result.score)}`}>
        <span className="text-5xl font-black">{result.score}</span>
      </div>

      <h2 className="text-3xl font-bold text-white mb-2">{result.grade}</h2>
      
      <div className={`px-4 py-1 rounded font-bold uppercase tracking-wider mb-8 ${
        result.isCorrect ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'
      }`}>
        {result.isCorrect ? '✅ Correct Choice!' : '❌ Incorrect Choice'}
      </div>

      <div className="w-full max-w-2xl bg-[#1b1e2e] border border-gray-700 rounded-lg p-6 space-y-4 shadow-xl">
        {!result.isCorrect && (
          <div className="bg-blue-900/20 border border-blue-900/50 p-4 rounded">
            <h4 className="text-xs font-bold text-blue-400 uppercase mb-1">The Best Action Was:</h4>
            <div className="text-gray-200 font-medium">Option {result.correctAction}</div>
          </div>
        )}

        <div>
          <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Explanation</h4>
          <p className="text-gray-300 leading-relaxed">
            {result.explanation}
          </p>
        </div>
      </div>

      <button
        onClick={onReset}
        className="mt-8 bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 px-8 rounded-full transition-colors border border-gray-600"
      >
        Try Another Scenario
      </button>
    </motion.div>
  );
}
