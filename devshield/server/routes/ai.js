import express from 'express';
import { reviewCode, generateScenario } from '../controllers/aiController.js';

const router = express.Router();

router.post('/review', reviewCode);
router.post('/generate-scenario', generateScenario);

export default router;
