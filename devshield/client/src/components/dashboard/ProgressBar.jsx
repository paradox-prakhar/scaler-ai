import React from 'react';
import { motion } from 'framer-motion';

export default function ProgressBar({ label, value, colorClass, bgClass = 'bg-gray-800' }) {
  // Ensure value is between 0 and 100
  const width = Math.min(Math.max(value || 0, 0), 100);

  return (
    <div className="w-full">
      <div className="flex justify-between items-end mb-2">
        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">{label}</span>
        <span className="text-sm font-bold text-white">{width}%</span>
      </div>
      <div className={`h-3 rounded-full ${bgClass} overflow-hidden`}>
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${width}%` }}
          transition={{ type: 'spring', stiffness: 30, delay: 0.2 }}
          className={`h-full rounded-full ${colorClass}`}
        />
      </div>
    </div>
  );
}
