import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import CodeBenchmark from './pages/CodeBenchmark'
import SecurityTrainerPage from './pages/SecurityTrainerPage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import './index.css'

function Navbar() {
  const [user, setUser] = React.useState(null);
  
  React.useEffect(() => {
    try {
      const u = JSON.parse(localStorage.getItem('user'));
      if (u) setUser(u);
    } catch(e) {}
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  return (
    <nav className="bg-[#161925] border-b border-gray-800 p-4 flex justify-between items-center text-sm">
      <Link to="/" className="text-xl font-black text-blue-500 flex items-center gap-2">
        <span>🛡️</span> DevShield
      </Link>
      <div className="space-x-6 flex items-center font-bold">
        <Link to="/code" className="text-gray-300 hover:text-white transition-colors">Code Benchmark</Link>
        <Link to="/security" className="text-gray-300 hover:text-white transition-colors">Security Trainer</Link>
        <Link to="/dashboard" className="text-gray-300 hover:text-white transition-colors">Dashboard</Link>
        
        {user ? (
          <div className="flex items-center gap-4 pl-4 border-l border-gray-700">
            <span className="text-gray-400">👤 {user.username}</span>
            <button onClick={handleLogout} className="text-xs bg-red-900/50 text-red-400 px-3 py-1.5 rounded hover:bg-red-800/80 transition-colors">Logout</button>
          </div>
        ) : (
          <Link to="/login" className="bg-blue-600 px-5 py-2 rounded text-white font-bold tracking-wide hover:bg-blue-500 transition-colors">Login / Register</Link>
        )}
      </div>
    </nav>
  )
}

function Home() {
  return <div className="p-10 text-center bg-[#0f111a] min-h-[calc(100vh-64px)] flex flex-col items-center justify-center"><h1 className="text-5xl font-black text-white mb-6">Welcome to DevShield</h1><p className="text-xl text-gray-400 max-w-2xl">The ultimate AI coding agent benchmark and interactive cyber security trainer for humans.</p></div>
}

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/code" element={<CodeBenchmark />} />
        <Route path="/security" element={<SecurityTrainerPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
