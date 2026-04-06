import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3001/api'
});

export const getTasks = () => api.get('/tasks').then(res => res.data);
export const getTask = (id) => api.get(`/tasks/${id}`).then(res => res.data);
export const runTask = (id, code) => api.post(`/tasks/${id}/run`, { code }).then(res => res.data);

// Auth & Users
export const login = (email, password) => api.post('/auth/login', { email, password }).then(res => res.data);
export const register = (username, email, password) => api.post('/auth/register', { username, email, password }).then(res => res.data);

export const getProfile = (token) => api.get('/users/me', { headers: { Authorization: `Bearer ${token}` } }).then(res => res.data);
export const getLeaderboard = () => api.get('/users/leaderboard').then(res => res.data);

// Security Scenarios
export const getScenarios = () => api.get('/scenarios').then(res => res.data);
export const getScenario = (id) => api.get(`/scenarios/${id}`).then(res => res.data);
export const submitDecision = (id, choice) => api.post(`/scenarios/${id}/submit`, { choice }).then(res => res.data);

// AI
export const getAIReview = (code, taskId, testResults) => api.post('/ai/review', { code, taskId, testResults }).then(res => res.data);
export const fetchAIScenario = () => api.post('/ai/generate-scenario').then(res => res.data);

export default api;
