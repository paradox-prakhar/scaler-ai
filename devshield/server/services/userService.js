import mongoose from 'mongoose';
import User from '../models/User.js';
import TaskResult from '../models/TaskResult.js';
import ScenarioResult from '../models/ScenarioResult.js';

export const getProfileData = async (userId) => {
    // If mongo is not ready, return stub data
    if (mongoose.connection.readyState !== 1) {
        return {
            user: { username: 'testuser', email: 'test@example.com', _id: userId },
            recentTasks: [
                { task: { title: 'Fix the Sum Bug', _id: '1' }, passed: 3, total: 3, createdAt: new Date() }
            ],
            recentScenarios: [
                { scenario: { title: 'Suspicious Bank Email', _id: '2' }, score: 90, grade: 'Excellent', createdAt: new Date() }
            ],
            stats: { 
                avgCodingScore: 100, 
                avgSecurityScore: 90, 
                totalTasksAttempted: 1, 
                totalScenariosAttempted: 1 
            }
        };
    }

    const user = await User.findById(userId).select('-password');
    
    // Aggregation/Fetch logic
    const recentTasks = await TaskResult.find({ user: userId }).sort({ createdAt: -1 }).limit(5).populate('task', 'title');
    const recentScenarios = await ScenarioResult.find({ user: userId }).sort({ createdAt: -1 }).limit(5).populate('scenario', 'title');
    
    const allTasks = await TaskResult.find({ user: userId });
    const allScenarios = await ScenarioResult.find({ user: userId });

    let avgCodingScore = 0;
    if (allTasks.length > 0) {
        const sum = allTasks.reduce((acc, t) => acc + (t.total > 0 ? (t.passed / t.total) * 100 : 0), 0);
        avgCodingScore = Math.round(sum / allTasks.length);
    }

    let avgSecurityScore = 0;
    if (allScenarios.length > 0) {
        const sum = allScenarios.reduce((acc, s) => acc + s.score, 0);
        avgSecurityScore = Math.round(sum / allScenarios.length);
    }

    return {
        user: {
            _id: user._id,
            username: user.username,
            email: user.email,
        },
        recentTasks,
        recentScenarios,
        stats: {
            avgCodingScore,
            avgSecurityScore,
            totalTasksAttempted: allTasks.length,
            totalScenariosAttempted: allScenarios.length
        }
    };
};

export const getLeaderboardData = async () => {
    if (mongoose.connection.readyState !== 1) {
         return [
             { username: 'hax0r', codingScore: 95, securityScore: 80, total: 175 },
             { username: 'testuser', codingScore: 100, securityScore: 90, total: 190 },
         ].sort((a,b) => b.total - a.total);
    }

    const users = await User.find({}).select('username codeScore securityScore');
    
    // For a real app, codeScore and securityScore should be updated on the User model
    // or aggregated dynamically across the results collections.
    // Assuming simple stub if fields exist.
    const mapped = users.map(u => ({
        username: u.username,
        codingScore: u.codeScore || 0,
        securityScore: u.securityScore || 0,
        total: (u.codeScore || 0) + (u.securityScore || 0)
    }));

    return mapped.sort((a, b) => b.total - a.total).slice(0, 10);
};
