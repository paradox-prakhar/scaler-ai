import { getProfileData, getLeaderboardData } from '../services/userService.js';

export const getProfile = async (req, res) => {
    try {
        const data = await getProfileData(req.user._id);
        res.json(data);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error fetching profile' });
    }
};

export const getLeaderboard = async (req, res) => {
    try {
        const data = await getLeaderboardData();
        res.json(data);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error fetching leaderboard' });
    }
};
