import React, { useState } from 'react';

export default function PhishingEmailView({ content }) {
  const [hoveredClue, setHoveredClue] = useState(null);

  return (
    <div className="w-full max-w-2xl mx-auto bg-gray-100 rounded-lg shadow-xl overflow-hidden font-sans text-gray-800 relative">
      {/* Top Banner indicating it's a simulation */}
      <div className="bg-yellow-500 text-yellow-900 text-xs font-bold text-center py-1 uppercase tracking-wider">
        ⚠️ Security Simulation Environment
      </div>
      
      {/* Email Header */}
      <div className="bg-white border-b border-gray-300 p-4">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl font-semibold">{content.subject}</h2>
          <span className="text-xs text-gray-500">{content.timestamp}</span>
        </div>
        <div className="flex gap-2 text-sm">
          <span className="font-bold text-gray-600">From:</span>
          <span 
            className="text-blue-700 relative group cursor-help"
            onMouseEnter={() => setHoveredClue('Suspicious sender domain - not the official bank domain')}
            onMouseLeave={() => setHoveredClue(null)}
          >
            Bank Security &lt;{content.from}&gt;
            <span className="absolute -top-1 -right-2 w-2 h-2 bg-red-500 rounded-full animate-ping"></span>
            <span className="absolute -top-1 -right-2 w-2 h-2 bg-red-500 rounded-full"></span>
          </span>
        </div>
        <div className="flex gap-2 text-sm mt-1">
          <span className="font-bold text-gray-600">To:</span>
          <span>customer@example.com</span>
        </div>
      </div>

      {/* Email Body */}
      <div className="p-6 bg-white min-h-[200px]">
        <p className="mb-4">
          <span 
             className="relative cursor-help"
             onMouseEnter={() => setHoveredClue('Generic greeting - real banks usually use your actual name')}
             onMouseLeave={() => setHoveredClue(null)}
          >
            Dear Customer,
            <span className="absolute -top-1 -right-2 w-2 h-2 bg-red-500 rounded-full"></span>
          </span>
        </p>
        <p className="mb-4">
          <span
            className="relative cursor-help"
            onMouseEnter={() => setHoveredClue('Urgent/threatening language used to create panic')}
            onMouseLeave={() => setHoveredClue(null)}
          >
            We detected unusual activity. Click HERE immediately to verify your account or it will be suspended in 24 hours.
            <span className="absolute -top-1 -right-2 w-2 h-2 bg-red-500 rounded-full"></span>
          </span>
        </p>
        <p className="mt-8">
          <span 
            className="text-white bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded font-bold cursor-help relative inline-block text-sm"
            onMouseEnter={() => setHoveredClue('Suspicious call to action link (Hovering would normally show the true URL)')}
            onMouseLeave={() => setHoveredClue(null)}
            onClick={(e) => e.preventDefault()}
          >
            [Verify Account]
            <span className="absolute -top-1 -right-2 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
          </span>
        </p>
      </div>

      {/* Hover Info Tooltip */}
      {hoveredClue && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs py-2 px-3 rounded shadow-lg z-10 w-3/4 text-center">
          💡 {hoveredClue}
        </div>
      )}
    </div>
  );
}
