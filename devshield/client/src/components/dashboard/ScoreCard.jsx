import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function ScoreCard({ title, score, icon, subtitle, colorClass }) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = parseInt(score, 10);
    if (!end) { setDisplayScore(0); return; }
    
    // Animate counter
    const duration = 1000;
    const increment = end / (duration / 16); // 60fps
    
    const countUp = () => {
      start += increment;
      if (start < end) {
        setDisplayScore(Math.floor(start));
        requestAnimationFrame(countUp);
      } else {
        setDisplayScore(end);
      }
    };
    
    requestAnimationFrame(countUp);
  }, [score]);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-[#1b1e2e]/80 backdrop-blur-md rounded-xl p-6 border-t-2 shadow-2xl relative overflow-hidden ${colorClass}`}
    >
      <div className="absolute -right-4 -top-8 text-8xl opacity-5 grayscale">{icon}</div>
      <h3 className="text-gray-400 text-sm font-bold tracking-widest uppercase mb-4">{title}</h3>
      <div className="flex items-end gap-3 mb-2">
        <span className="text-6xl font-black">{displayScore}</span>
        <span className="text-xl mb-1 opacity-75">{icon}</span>
      </div>
      <p className="text-sm opacity-80">{subtitle}</p>
    </motion.div>
  );
}
