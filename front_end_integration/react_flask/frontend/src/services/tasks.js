/**
 * Tasks service for handling task CRUD operations with the backend API
 */

import axios from 'axios';

const API_URL = '/api';

/**
 * Get all tasks
 * @returns {Promise<Array>} - List of tasks
 */
export const getAllTasks = async () => {
  try {
    const response = await axios.get(`${API_URL}/tasks`);
    return response.data;
  } catch (error) {
    console.error('Error fetching tasks:', error.response?.data || error.message);
    throw new Error(error.response?.data?.message || 'Failed to fetch tasks');
  }
};

/**
 * Get a specific task by ID
 * @param {string} id - Task ID
 * @returns {Promise<Object>} - Task data
 */
export const getTask = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/tasks/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching task ${id}:`, error.response?.data || error.message);
    throw new Error(error.response?.data?.message || 'Failed to fetch task');
  }
};

/**
 * Create a new task
 * @param {Object} taskData - Task data
 * @returns {Promise<Object>} - Created task
 */
export const createTask = async (taskData) => {
  try {
    const response = await axios.post(`${API_URL}/tasks`, taskData);
    return response.data;
  } catch (error) {
    console.error('Error creating task:', error.response?.data || error.message);
    throw new Error(error.response?.data?.message || 'Failed to create task');
  }
};

/**
 * Update an existing task
 * @param {string} id - Task ID
 * @param {Object} taskData - Updated task data
 * @returns {Promise<Object>} - Updated task
 */
export const updateTask = async (id, taskData) => {
  try {
    const response = await axios.put(`${API_URL}/tasks/${id}`, taskData);
    return response.data;
  } catch (error) {
    console.error(`Error updating task ${id}:`, error.response?.data || error.message);
    throw new Error(error.response?.data?.message || 'Failed to update task');
  }
};

/**
 * Delete a task
 * @param {string} id - Task ID
 * @returns {Promise<Object>} - Deletion confirmation
 */
export const deleteTask = async (id) => {
  try {
    const response = await axios.delete(`${API_URL}/tasks/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting task ${id}:`, error.response?.data || error.message);
    throw new Error(error.response?.data?.message || 'Failed to delete task');
  }
};
