import mongoose from 'mongoose';

const TaskResultSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  taskId: String,
  taskTitle: String,
  passed: Number,
  failed: Number,
  totalTests: Number,
  scorePercent: Number,
  code: String,
  submittedAt: { type: Date, default: Date.now }
});

export default mongoose.model('TaskResult', TaskResultSchema);
