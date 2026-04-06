import React from 'react';
import { motion } from 'framer-motion';

export default function ScenarioSelector({ scenarios, selectedId, onSelect }) {
  const getBadgeColor = (level) => {
    switch(level) {
      case 'critical': return 'bg-red-900/50 text-red-400 border border-red-800';
      case 'high': return 'bg-orange-900/50 text-orange-400 border border-orange-800';
      case 'medium': return 'bg-yellow-900/50 text-yellow-400 border border-yellow-800';
      default: return 'bg-gray-800 text-gray-400 border border-gray-700';
    }
  };

  const getIcon = (type) => {
    switch(type) {
      case 'phishing': return '📧';
      case 'malware': return '⚠️';
      case 'logs': return '📜';
      default: return '🛡️';
    }
  };

  return (
    <div className="flex flex-col gap-3 p-4">
      <h2 className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-2">Available Scenarios</h2>
      {scenarios.map((s) => {
        const isSelected = selectedId === s.id;
        return (
          <motion.div
            key={s.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onSelect(s.id)}
            className={`cursor-pointer p-4 rounded transition-all ${
              isSelected 
                ? 'bg-[#1b1e2e] border border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.3)]' 
                : 'bg-[#161925] border border-gray-800 hover:border-gray-600'
            }`}
          >
            <div className="flex items-start justify-between">
              <span className="text-2xl mr-3">{getIcon(s.type)}</span>
              <div className="flex-1">
                <h3 className={`font-bold ${isSelected ? 'text-blue-400' : 'text-gray-200'}`}>
                  {s.title}
                </h3>
                <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded mt-2 inline-block ${getBadgeColor(s.riskLevel)}`}>
                  {s.riskLevel}
                </span>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
