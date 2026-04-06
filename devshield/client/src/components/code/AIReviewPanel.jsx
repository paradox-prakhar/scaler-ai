import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getAIReview } from '../../services/api';

export default function AIReviewPanel({ code, taskId, testResults }) {
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const fetchReview = async () => {
    setLoading(true);
    setError(false);
    try {
      const data = await getAIReview(code, taskId, testResults);
      if (data && data.review) {
        setReview(data.review);
      }
    } catch (err) {
      console.error(err);
      setError(true);
    }
    setLoading(false);
  };

  if (!review && !loading && !error) {
    return (
      <div className="mt-6 flex justify-center">
        <button 
          onClick={fetchReview}
          className="bg-purple-600 hover:bg-purple-500 text-white font-bold py-3 px-6 rounded-lg transition-colors flex items-center shadow-lg shadow-purple-900/30"
        >
          <span className="mr-2">🤖</span> Request AI Code Review
        </button>
      </div>
    );
  }

  return (
    <div className="mt-6">
      {loading && (
        <div className="flex flex-col items-center justify-center p-8 bg-[#161925] border border-gray-800 rounded-lg">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mb-4"></div>
          <p className="text-gray-400 font-medium">Gemini is analyzing your code...</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-900/30 border border-red-800 rounded-lg text-center text-red-400">
          AI review service is currently unavailable. Please try again later.
        </div>
      )}

      <AnimatePresence>
        {review && !loading && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-[#161925] rounded-xl border border-purple-900/50 shadow-2xl overflow-hidden"
          >
            <div className="bg-gradient-to-r from-purple-900/40 to-blue-900/40 border-b border-gray-800 p-4 flex items-center gap-2">
              <span className="text-2xl">🤖</span>
              <h3 className="text-purple-300 font-black tracking-wide text-lg">AI Code Review</h3>
            </div>
            
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Strengths */}
              <div className="space-y-3">
                <h4 className="text-green-400 font-bold uppercase tracking-wider text-xs border-b border-green-900/30 pb-2">What you did well</h4>
                <ul className="space-y-2">
                  {review.strengths.map((str, i) => (
                    <li key={i} className="flex gap-2 text-sm text-gray-300">
                      <span className="text-green-500 mt-0.5">✓</span>
                      <span>{str}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Improvements */}
              <div className="space-y-3">
                <h4 className="text-yellow-400 font-bold uppercase tracking-wider text-xs border-b border-yellow-900/30 pb-2">Areas for Improvement</h4>
                <ul className="space-y-2">
                  {review.improvements.map((imp, i) => (
                    <li key={i} className="flex gap-2 text-sm text-gray-300">
                      <span className="text-yellow-500 mt-0.5">⚠️</span>
                      <span>{imp}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Pro Tip */}
            {review.tip && (
              <div className="bg-purple-900/20 border-t border-purple-900/30 p-4 mx-6 mb-6 rounded flex items-start gap-4">
                <div className="text-2xl pt-1">🎯</div>
                <div>
                  <h4 className="text-purple-300 font-bold text-xs uppercase tracking-wider mb-1">Pro Tip</h4>
                  <p className="text-sm text-gray-200">{review.tip}</p>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
