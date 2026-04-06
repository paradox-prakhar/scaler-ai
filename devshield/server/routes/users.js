import express from 'express';
import { getProfile, getLeaderboard } from '../controllers/userController.js';
import { protect } from '../middleware/auth.js';

const router = express.Router();

router.get('/me', protect, getProfile);
router.get('/leaderboard', getLeaderboard);

export default router;
