import { getAllScenarios, getScenarioById, scoreDecision } from '../services/scenarioService.js';

export const listScenarios = (req, res) => {
    res.json(getAllScenarios());
};

export const getScenario = (req, res) => {
    const scenario = getScenarioById(req.params.id);
    if (!scenario) {
        return res.status(404).json({ message: 'Scenario not found' });
    }
    
    // Return scenario WITHOUT exposing correctAction and partialActions
    const { correctAction, partialActions, explanation, ...safeScenario } = scenario;
    res.json(safeScenario);
};

export const submitDecision = (req, res) => {
    const scenario = getScenarioById(req.params.id);
    if (!scenario) {
        return res.status(404).json({ message: 'Scenario not found' });
    }

    const { choice } = req.body;
    if (!choice || !['A', 'B', 'C', 'D'].includes(choice)) {
        return res.status(400).json({ message: 'Invalid choice. Must be A, B, C, or D.' });
    }

    const result = scoreDecision(scenario, choice);
    
    // In a full implementation, we'd save this result to MongoDB for the current user here
    // const newResult = new ScenarioResult({ userId: req.user._id, scenarioId: scenario.id, ...result });
    // await newResult.save();

    res.json(result);
};
