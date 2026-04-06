import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { login, register } from '../services/api';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      let data;
      if (isLogin) {
        data = await login(formData.email, formData.password);
      } else {
        data = await register(formData.username, formData.email, formData.password);
      }
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify({ id: data._id, username: data.username, email: data.email }));
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.message || 'Authentication failed');
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center p-6" style={{ background: 'linear-gradient(135deg, #0f111a 0%, #161925 100%)' }}>
      <div className="w-full max-w-md bg-[#1b1e2e]/80 backdrop-blur-md rounded-xl shadow-2xl border border-gray-800 overflow-hidden relative">
        <div className="flex border-b border-gray-800">
          <button 
            className={`flex-1 py-4 font-bold text-sm uppercase tracking-widest relative ${isLogin ? 'text-white' : 'text-gray-500 hover:text-gray-300'}`}
            onClick={() => setIsLogin(true)}
          >
            Login
            {isLogin && <motion.div layoutId="tab" className="absolute bottom-0 left-0 right-0 h-1 bg-blue-500" />}
          </button>
          <button 
            className={`flex-1 py-4 font-bold text-sm uppercase tracking-widest relative ${!isLogin ? 'text-white' : 'text-gray-500 hover:text-gray-300'}`}
            onClick={() => setIsLogin(false)}
          >
            Register
            {!isLogin && <motion.div layoutId="tab" className="absolute bottom-0 left-0 right-0 h-1 bg-blue-500" />}
          </button>
        </div>

        <div className="p-8">
          <h2 className="text-2xl font-bold text-white mb-6">
            {isLogin ? 'Welcome Back' : 'Join DevShield'}
          </h2>
          
          {error && <div className="p-3 mb-6 bg-red-900/30 border border-red-800 rounded text-red-400 text-sm">{error}</div>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <AnimatePresence>
              {!isLogin && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Username</label>
                  <input 
                    type="text" 
                    required={!isLogin}
                    className="w-full bg-[#0f111a] border border-gray-700 rounded p-3 text-white focus:border-blue-500 outline-none"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                  />
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Email</label>
              <input 
                type="email" 
                required
                className="w-full bg-[#0f111a] border border-gray-700 rounded p-3 text-white focus:border-blue-500 outline-none"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Password</label>
              <input 
                type="password" 
                required
                className="w-full bg-[#0f111a] border border-gray-700 rounded p-3 text-white focus:border-blue-500 outline-none"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
              />
            </div>

            <button type="submit" className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold rounded p-3 mt-4 transition-colors">
              {isLogin ? 'Sign In' : 'Create Account'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
