import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import mongoose from 'mongoose';

// Load env vars
dotenv.config();

const app = express();

// Middleware
app.use(cors({ origin: 'http://localhost:5173' }));
app.use(express.json());

// Basic health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date() });
});

// Import route definitions (these files will be created next)
// import authRoutes from './routes/auth.js';
// import tasksRoutes from './routes/tasks.js';
// import scenariosRoutes from './routes/scenarios.js';
// import usersRoutes from './routes/users.js';
// import aiRoutes from './routes/ai.js';

// Setup routes
// app.use('/api/auth', authRoutes);
// app.use('/api/tasks', tasksRoutes);
// app.use('/api/scenarios', scenariosRoutes);
// app.use('/api/users', usersRoutes);
// app.use('/api/ai', aiRoutes);

// Connect to MongoDB using older compatible options (or just URI as 8.x handles it fine)
const PORT = process.env.PORT || 3001;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/devshield';

mongoose.connect(MONGO_URI)
  .then(() => {
    console.log('✅ Connected to MongoDB');
    app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));
  })
  .catch(err => {
    console.error('❌ MongoDB Connection Error:', err.message);
  });
