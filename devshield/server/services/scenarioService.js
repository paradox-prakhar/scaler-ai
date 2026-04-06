import scenarios from '../data/scenarios.js';

export const getAllScenarios = () => {
    return scenarios.map(s => ({ 
        id: s.id, 
        type: s.type, 
        riskLevel: s.riskLevel, 
        title: s.title 
    }));
};

export const getScenarioById = (id) => {
    return scenarios.find(s => s.id === id) || null;
};

export const scoreDecision = (scenario, userChoice) => {
    let score = 0;
    let grade = 'Incorrect';
    let isCorrect = false;

    if (userChoice === scenario.correctAction) {
        score = 90;
        grade = 'Excellent';
        isCorrect = true;
    } else if (scenario.partialActions && scenario.partialActions.includes(userChoice)) {
        score = 55;
        grade = 'Partial';
    } else {
        score = 15;
    }

    return {
        score,
        grade,
        isCorrect,
        explanation: scenario.explanation,
        correctAction: scenario.correctAction,
        riskLevel: scenario.riskLevel
    };
};
