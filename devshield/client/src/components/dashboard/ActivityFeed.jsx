import React from 'react';
import { motion } from 'framer-motion';

export default function ActivityFeed({ tasks = [], scenarios = [] }) {
  // Merge and sort
  const activities = [
    ...tasks.map(t => ({ ...t, activityType: 'task' })),
    ...scenarios.map(s => ({ ...s, activityType: 'scenario' }))
  ].sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0)).slice(0, 8);

  if (activities.length === 0) {
    return (
      <div className="text-center p-8 text-gray-500 text-sm">
        No recent activity. Start a coding challenge or a security scenario!
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {activities.map((act, i) => (
        <motion.div 
          key={i}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.1 }}
          className="bg-[#161925] p-3 rounded border border-gray-800 flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <span className="text-xl">
              {act.activityType === 'task' ? '💻' : '🛡️'}
            </span>
            <div>
              <div className="text-sm font-bold text-gray-200">
                {act.activityType === 'task' ? act.task?.title || 'Unknown Task' : act.scenario?.title || 'Unknown Scenario'}
              </div>
              <div className="text-xs text-gray-500">
                {new Date(act.createdAt).toLocaleString()}
              </div>
            </div>
          </div>
          
          <div className="text-right">
            {act.activityType === 'task' ? (
              <span className={`text-xs font-bold px-2 py-1 rounded ${act.passed === act.total && act.total > 0 ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
                {act.passed}/{act.total} Tests
              </span>
            ) : (
              <span className={`text-xs font-bold px-2 py-1 rounded ${act.score >= 80 ? 'bg-green-900/30 text-green-400' : (act.score >= 50 ? 'bg-yellow-900/30 text-yellow-500' : 'bg-red-900/30 text-red-400')}`}>
                {act.score} Score
              </span>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
