import { getAllTasks, getTaskById } from '../services/taskService.js';
import { executeCode } from '../sandbox/executor.js';

export const listTasks = (req, res) => {
    res.json(getAllTasks());
};

export const getTask = (req, res) => {
    const task = getTaskById(req.params.id);
    if (!task) {
        return res.status(404).json({ message: 'Task not found' });
    }
    // Return full task including starterCode, but omit testRunner implementation details
    const { testRunner, ...safeTask } = task;
    res.json(safeTask);
};

export const runTask = async (req, res) => {
    const task = getTaskById(req.params.id);
    if (!task) {
        return res.status(404).json({ message: 'Task not found' });
    }

    const { code } = req.body;
    if (!code) {
        return res.status(400).json({ message: 'Code is required' });
    }

    try {
        const result = await executeCode(code, task);
        res.json(result);
    } catch (error) {
        console.error('Error executing task:', error);
        res.status(500).json({ message: 'Internal server error during execution' });
    }
};
