import axios from 'axios';

// Create an Axios instance that will use the Vite proxy
const api = axios.create({
  baseURL: '/api', // This will be proxied to http://localhost:5000 by Vite
  timeout: 60000, // 60-second timeout for long-running ML models
});

export default {
  /**
   * Sends a claim to the backend for verification.
   * @param {string} claim - The user's claim.
   * @returns {Promise<Object>} The fact-check result from the backend.
   */
  async verifyClaim(claim) {
    try {
      // The endpoint here must match the one in your backend/app.py
      const response = await api.post('/verify', { message: claim });
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      // Create a user-friendly error object to display in the chat
      throw new Error(error.response?.data?.detail || 'A network error occurred.');
    }
  },
};