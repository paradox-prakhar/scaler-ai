import tasks from '../data/tasks.js';

export const getAllTasks = () => {
    return tasks.map(t => ({
        id: t.id,
        title: t.title,
        difficulty: t.difficulty,
        description: t.description
    }));
};

export const getTaskById = (id) => {
    return tasks.find(t => t.id === id) || null;
};
