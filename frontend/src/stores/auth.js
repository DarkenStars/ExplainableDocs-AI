import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)
  
  const login = async (credentials) => {
    loading.value = true
    try {
      // Simulate authentication
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      user.value = {
        id: 'user123',
        name: credentials.name || 'Demo User',
        email: credentials.email || 'demo@newsadvisor.ai',
        photoURL: 'https://via.placeholder.com/40'
      }
      isAuthenticated.value = true
      
      // Store in localStorage for persistence
      localStorage.setItem('user', JSON.stringify(user.value))
      
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: error.message }
    } finally {
      loading.value = false
    }
  }
  
  const logout = () => {
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('user')
    localStorage.removeItem('conversations')
  }
  
  const checkAuth = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      user.value = JSON.parse(savedUser)
      isAuthenticated.value = true
    }
  }
  
  return {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    checkAuth
  }
})
