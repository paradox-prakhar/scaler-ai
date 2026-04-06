import React from 'react';
import { motion } from 'framer-motion';

export default function DecisionPanel({ options, userChoice, onChoiceSelect, onConfirm, disabled }) {
  return (
    <div className="bg-[#0f111a] border-t border-gray-800 p-6">
      <h3 className="text-xl font-bold text-white mb-4">What would you do?</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
        {options.map((opt, i) => {
          const isSelected = userChoice === opt.id;
          return (
            <motion.button
              key={opt.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              onClick={() => onChoiceSelect(opt.id)}
              disabled={disabled}
              className={`p-4 text-left rounded border transition-all ${
                isSelected 
                  ? 'bg-purple-900/40 border-purple-500 shadow-[0_0_15px_rgba(168,85,247,0.3)]' 
                  : 'bg-[#1b1e2e] border-gray-700 hover:border-gray-500 opacity-80'
              } ${disabled && !isSelected ? 'opacity-30 cursor-not-allowed' : ''}`}
            >
              <div className="flex gap-4">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 border text-xs font-bold ${
                  isSelected ? 'bg-purple-500 border-purple-400 text-white' : 'bg-[#161925] border-gray-600 text-gray-400'
                }`}>
                  {opt.id}
                </div>
                <span className={isSelected ? 'text-white font-medium' : 'text-gray-300'}>
                  {opt.text}
                </span>
              </div>
            </motion.button>
          );
        })}
      </div>

      <div className="flex justify-end">
        <button
          onClick={onConfirm}
          disabled={disabled || !userChoice}
          className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-8 rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Confirm Choice
        </button>
      </div>
    </div>
  );
}
