import * as aiService from '../services/aiService.js';

export const reviewCode = async (req, res) => {
    try {
        const { code, taskId, testResults } = req.body;
        
        if (!code || !taskId) {
            return res.status(400).json({ message: "Code and taskId are required for review." });
        }

        const review = await aiService.reviewCode(code, taskId, testResults);
        res.json({ review });
    } catch (error) {
        console.error("AI Review Error:", error);
        res.status(503).json({ message: "AI review service is currently unavailable." });
    }
};

export const generateScenario = async (req, res) => {
    try {
        const scenario = await aiService.generatePhishingEmail();
        res.json({ scenario });
    } catch (error) {
        console.error("AI Scenario Gen Error:", error);
        res.status(503).json({ message: "AI generation service is currently unavailable." });
    }
};
