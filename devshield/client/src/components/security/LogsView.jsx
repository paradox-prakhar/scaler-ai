import React from 'react';

export default function LogsView({ content }) {
  const isSuspicious = (text) => {
    const suspiciousKeywords = ['Failed', 'shadow', 'passwd', 'unauthorized', 'error'];
    return suspiciousKeywords.some(keyword => text.includes(keyword));
  };

  return (
    <div className="w-full h-full p-6 text-gray-300 font-mono text-sm bg-black overflow-y-auto">
      <div className="mb-4 text-green-500 font-bold">
        $ tail -f /var/log/auth.log /var/log/syslog
      </div>
      
      <div className="space-y-1">
        {content.logs.map((log, idx) => {
          // Rudimentary parsing for styling
          // 2024-01-15 02:14:22 [AUTH] Failed login...
          const parts = log.match(/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\[.*?\]) (.*)$/);
          let timestamp = "", module = "", message = log;
          
          if (parts) {
            timestamp = parts[1];
            module = parts[2];
            message = parts[3];
          }
          
          const highlight = isSuspicious(message);

          return (
            <div key={idx} className={`flex gap-3 hover:bg-gray-900 px-2 py-1 -mx-2 ${highlight ? 'text-red-400' : 'text-gray-400'}`}>
              <span className="text-gray-500 shrink-0">{timestamp}</span>
              <span className="text-blue-400 font-bold shrink-0">{module}</span>
              <span className={highlight ? 'font-bold bg-red-900/30' : ''}>{message}</span>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 flex">
        <span className="text-green-500 font-bold mr-2">$</span>
        <span className="animate-pulse bg-gray-400 w-2 h-5 inline-block"></span>
      </div>
    </div>
  );
}
