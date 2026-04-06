import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import './index.css'

function Navbar() {
  return (
    <nav className="bg-dark-card border-b border-dark-border p-4 flex justify-between items-center">
      <Link to="/" className="text-xl font-bold text-primary">🛡 DevShield</Link>
      <div className="space-x-6">
        <Link to="/code" className="hover:text-primary transition-colors">Code Benchmark</Link>
        <Link to="/security" className="hover:text-primary transition-colors">Security Trainer</Link>
        <Link to="/dashboard" className="hover:text-primary transition-colors">Dashboard</Link>
        <Link to="/login" className="bg-primary px-4 py-2 rounded font-medium hover:bg-opacity-90">Login</Link>
      </div>
    </nav>
  )
}

function Home() {
  return <div className="p-10 text-center"><h1 className="text-4xl font-bold mb-4">Welcome to DevShield</h1><p className="text-lg text-gray-400">Benchmark AI code and train humans in cyber security.</p></div>
}

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/code" element={<div className="p-10 text-center"><h1>Coding Benchmark (Coming soon)</h1></div>} />
        <Route path="/security" element={<div className="p-10 text-center"><h1>Security Trainer (Coming soon)</h1></div>} />
        <Route path="/dashboard" element={<div className="p-10 text-center"><h1>Unified Dashboard (Coming soon)</h1></div>} />
        <Route path="/login" element={<div className="p-10 text-center"><h1>Login / Register</h1></div>} />
      </Routes>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
