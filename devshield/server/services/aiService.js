// Mock implementation of AI Service
// In a real application, you'd use the OpenAI or Gemini SDK here.

export const reviewCode = async (code, taskId, testResults) => {
    // Simulate AI thinking delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Return structured AI review mock
    return {
        strengths: [
            "Good use of fundamental JavaScript constructs.",
            "Variable naming is reasonably clear.",
            "Logic generally flows in the right direction."
        ],
        improvements: [
            "Could consider using more modern ES6 features (e.g., reduce for array operations).",
            "Be careful with edge cases when inputs are empty or null.",
            "Adding a few inline comments would make the intent clearer for future maintainers."
        ],
        tip: "Consider writing a quick unit test for boundary conditions immediately after drafting your logic to catch off-by-one errors early."
    };
};

export const generatePhishingEmail = async () => {
    // Simulate AI thinking delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    return {
        from: "it-support@company-portal-update.com",
        subject: "Action Required: Mandatory Password Rotation",
        body: "Dear Employee,\n\nOur security policies require you to immediately update your password. Please click the link below to verify your credentials.\n\n[Verify Credentials Here]\n\nFailure to act within 24 hours will result in account suspension.\n\nThanks,\nIT Department",
        indicators: [
            "Sense of urgency ('immediately update', 'failure to act within 24 hours').",
            "Suspicious generic 'From' domain ('company-portal-update.com').",
            "Generic greeting ('Dear Employee')."
        ],
        correctAction: "Report as phishing",
        explanation: "This is a classic phishing template using urgency and generic greetings to panic the target into clicking a malicious link."
    };
};
