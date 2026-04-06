import mongoose from 'mongoose';

const ScenarioResultSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  scenarioId: String,
  scenarioType: String,
  userChoice: String,
  correctChoice: String,
  score: Number,
  riskLevel: String,
  completedAt: { type: Date, default: Date.now }
});

export default mongoose.model('ScenarioResult', ScenarioResultSchema);
