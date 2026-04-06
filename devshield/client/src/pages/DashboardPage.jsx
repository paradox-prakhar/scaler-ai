import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { getProfile, getLeaderboard } from '../services/api';
import ScoreCard from '../components/dashboard/ScoreCard';
import ProgressBar from '../components/dashboard/ProgressBar';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import Leaderboard from '../components/dashboard/Leaderboard';

export default function DashboardPage() {
  const [profile, setProfile] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }

    Promise.all([
      getProfile(token).catch(() => null),
      getLeaderboard().catch(() => [])
    ]).then(([profileData, leaderData]) => {
      setProfile(profileData);
      setLeaderboard(leaderData);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="p-10 text-center text-gray-500">Loading Dashboard...</div>;

  if (!profile) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex flex-col items-center justify-center p-10 bg-[#0f111a] text-center">
        <span className="text-6xl mb-4 opacity-50">🔒</span>
        <h2 className="text-2xl font-bold text-white mb-2">Access Restricted</h2>
        <p className="text-gray-400 mb-6 max-w-md">You need to be logged in to view your unified dashboard scorecard and track your progress.</p>
        <Link to="/login" className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded font-bold transition-all shadow-[0_0_15px_rgba(37,99,235,0.4)]">
          Login or Register
        </Link>
      </div>
    );
  }

  const { user, stats, recentTasks, recentScenarios } = profile;

  return (
    <div className="min-h-[calc(100vh-64px)] bg-[#0f111a] text-gray-200 p-6 lg:p-10 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header Section */}
        <div className="flex items-center justify-between border-b border-gray-800 pb-6">
          <div>
            <h1 className="text-3xl font-black text-white">Welcome back, {user.username}!</h1>
            <p className="text-gray-400 mt-1">Here is your DevShield unified performance card.</p>
          </div>
          <div className="hidden sm:block text-right">
            <div className="text-xs font-bold text-gray-500 uppercase tracking-widest">Global Rank</div>
            <div className="text-3xl font-black text-blue-400 mt-1">
              #{leaderboard.findIndex(l => l.username === user.username) + 1 || '--'}
            </div>
          </div>
        </div>

        {/* Top Widgets: Score Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ScoreCard 
            title="Coding Benchmark Score" 
            score={stats.avgCodingScore} 
            icon="💻" 
            subtitle={`${stats.totalTasksAttempted} Tasks Attempted`}
            colorClass="border-t-green-500" 
          />
          <ScoreCard 
            title="Cyber Security Score" 
            score={stats.avgSecurityScore} 
            icon="🛡️" 
            subtitle={`${stats.totalScenariosAttempted} Scenarios Completed`}
            colorClass="border-t-orange-500" 
          />
        </div>

        {/* Middle Section: Progress Bars */}
        <div className="bg-[#161925] rounded-xl p-6 border border-gray-800 grid grid-cols-1 md:grid-cols-2 gap-8 shadow-xl">
          <div className="space-y-6">
            <h3 className="text-white font-bold tracking-wide flex items-center gap-2"><span className="text-green-500">▶</span> Coding Metrics</h3>
            <ProgressBar label="Code Correctness" value={stats.avgCodingScore} colorClass="bg-green-500" />
            <ProgressBar label="Implementation Speed" value={75} colorClass="bg-green-600" />
          </div>
          <div className="space-y-6">
            <h3 className="text-white font-bold tracking-wide flex items-center gap-2"><span className="text-orange-500">▶</span> Security Metrics</h3>
            <ProgressBar label="Threat Detection Accuracy" value={stats.avgSecurityScore} colorClass="bg-orange-500" />
            <ProgressBar label="Incident Response" value={stats.avgSecurityScore > 0 ? Math.min(stats.avgSecurityScore + 10, 100) : 0} colorClass="bg-orange-600" />
          </div>
        </div>

        {/* Bottom Section: Feed & Leaderboard */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 bg-[#1b1e2e]/50 rounded-xl p-6 border border-gray-800 shadow-xl">
            <h3 className="text-white font-bold mb-4 uppercase tracking-widest text-sm">Recent Activity</h3>
            <ActivityFeed tasks={recentTasks} scenarios={recentScenarios} />
          </div>
          <div className="lg:col-span-2 bg-[#1b1e2e]/50 rounded-xl p-6 border border-gray-800 shadow-xl">
            <h3 className="text-white font-bold mb-4 uppercase tracking-widest text-sm">Global Leaderboard</h3>
            <Leaderboard data={leaderboard} currentUsername={user.username} />
          </div>
        </div>

      </div>
    </div>
  );
}
