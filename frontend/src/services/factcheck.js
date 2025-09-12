import axios from 'axios'

const api = axios.create({
  baseURL: '',  // Empty because Vite proxy handles routing
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000, // 60 seconds for ML processing
})

export async function verifyClaim(claim) {
  try {
    // This gets proxied to http://localhost:5000/verify
    const response = await api.post('/api/verify', { claim })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to verify claim')
  }
}

export async function getHistory() {
  try {
    // This gets proxied to http://localhost:5000/history
    const response = await api.get('/api/history')
    return response.data
  } catch (error) {
    throw new Error('Failed to get history')
  }
}
