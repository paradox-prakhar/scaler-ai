import React from 'react';
import { motion } from 'framer-motion';

export default function Leaderboard({ data = [], currentUsername }) {
  if (!data || data.length === 0) {
    return <div className="p-8 text-center text-gray-500 text-sm">No leaderboard data available yet.</div>;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-800">
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-gray-400 bg-[#161925] border-b border-gray-800 uppercase tracking-wider">
          <tr>
            <th className="px-4 py-3 text-center">Rank</th>
            <th className="px-4 py-3">Agent / User</th>
            <th className="px-4 py-3 text-center">Code</th>
            <th className="px-4 py-3 text-center">Sec</th>
            <th className="px-4 py-3 text-right text-blue-400">Total</th>
          </tr>
        </thead>
        <tbody className="bg-[#0f111a]">
          {data.map((row, idx) => {
            const isMe = row.username === currentUsername;
            let rankDisplay = idx + 1;
            if (idx === 0) rankDisplay = '🥇';
            if (idx === 1) rankDisplay = '🥈';
            if (idx === 2) rankDisplay = '🥉';

            return (
              <motion.tr 
                key={idx}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: idx * 0.05 }}
                className={`border-b border-gray-800/50 hover:bg-[#161925] transition-colors ${
                  isMe ? 'bg-blue-900/20' : ''
                }`}
              >
                <td className="px-4 py-3 text-center font-bold">{rankDisplay}</td>
                <td className="px-4 py-3 font-medium text-gray-200">
                  {row.username} {isMe && <span className="text-xs text-blue-400 ml-2">(You)</span>}
                </td>
                <td className="px-4 py-3 text-center text-green-400 font-mono">{row.codingScore}</td>
                <td className="px-4 py-3 text-center text-orange-400 font-mono">{row.securityScore}</td>
                <td className="px-4 py-3 text-right text-blue-400 font-bold font-mono">{row.total}</td>
              </motion.tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
