import express from 'express';
import { listScenarios, getScenario, submitDecision } from '../controllers/scenarioController.js';

const router = express.Router();

router.get('/', listScenarios);
router.get('/:id', getScenario);
router.post('/:id/submit', submitDecision);

export default router;
