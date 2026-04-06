export const scenarios = [
  {
    id: 'phishing-bank',
    type: 'phishing',
    riskLevel: 'high',
    title: 'Suspicious Bank Email',
    content: {
      from: 'security@bank-secure-alert.com',
      subject: 'URGENT: Your account has been compromised!',
      body: 'Dear Customer, We detected unusual activity. Click HERE immediately to verify your account or it will be suspended in 24 hours. [Verify Account]',
      timestamp: '2024-01-15 09:42',
      indicators: ['urgent language', 'suspicious sender domain', 'generic greeting', 'suspicious link']
    },
    options: [
      { id: 'A', text: 'Click the link and verify your account' },
      { id: 'B', text: 'Delete the email and ignore it' },
      { id: 'C', text: 'Forward to IT security and mark as phishing' },
      { id: 'D', text: 'Reply asking for more information' }
    ],
    correctAction: 'C',
    partialActions: ['B'],
    explanation: 'This is a phishing email. Red flags: suspicious domain (bank-secure-alert.com is NOT your bank), urgent/threatening language, generic greeting. Always report to IT — deleting is better than clicking but reporting helps protect others.'
  },
  {
    id: 'malware-alert',
    type: 'malware',
    riskLevel: 'critical',
    title: 'Antivirus Alert Popup',
    content: {
      alertType: 'CRITICAL SYSTEM WARNING',
      message: 'Your computer is infected with 47 viruses! Call Microsoft Support NOW: 1-800-XXX-XXXX to fix immediately!',
      source: 'Pop-up window (browser)'
    },
    options: [
      { id: 'A', text: 'Call the phone number immediately' },
      { id: 'B', text: 'Close the browser tab / window' },
      { id: 'C', text: 'Download the "fix" software shown' },
      { id: 'D', text: 'Run a scan with your actual antivirus' }
    ],
    correctAction: 'D',
    partialActions: ['B'],
    explanation: 'This is a scareware/tech support scam. Microsoft never contacts you via browser popups with phone numbers. Close the browser first (don\'t call the number), then run your real antivirus software.'
  },
  {
    id: 'suspicious-logs',
    type: 'logs',
    riskLevel: 'medium',
    title: 'Review These System Logs',
    content: {
      logs: [
        '2024-01-15 02:14:22 [AUTH] Failed login for user admin from 185.220.101.5',
        '2024-01-15 02:14:23 [AUTH] Failed login for user admin from 185.220.101.5',
        '2024-01-15 02:14:24 [AUTH] Failed login for user admin from 185.220.101.5',
        '2024-01-15 02:14:25 [AUTH] Successful login for user admin from 185.220.101.5',
        '2024-01-15 02:14:26 [FILE] admin accessed /etc/passwd',
        '2024-01-15 02:14:27 [FILE] admin accessed /etc/shadow',
      ]
    },
    options: [
      { id: 'A', text: 'This is normal activity, no action needed' },
      { id: 'B', text: 'Reset the admin password' },
      { id: 'C', text: 'Block the IP, reset admin credentials, and alert security team' },
      { id: 'D', text: 'Delete the logs to hide the breach' }
    ],
    correctAction: 'C',
    partialActions: ['B'],
    explanation: 'This shows a brute-force attack followed by successful unauthorized access. The attacker accessed sensitive system files (/etc/passwd, /etc/shadow). Full incident response is required: block IP, reset credentials, alert security team, preserve logs for forensics.'
  }
];

export default scenarios;
