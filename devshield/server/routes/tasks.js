import express from 'express';
import { listTasks, getTask, runTask } from '../controllers/taskController.js';

const router = express.Router();

router.get('/', listTasks);
router.get('/:id', getTask);
router.post('/:id/run', runTask);

export default router;
