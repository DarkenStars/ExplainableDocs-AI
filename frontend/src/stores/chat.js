import { defineStore } from 'pinia'
import { ref } from 'vue'
import mockApi from '../services/mockApi'
import axios from 'axios'

const USE_REAL_BACKEND = true // Toggle this when ready

const api = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 30000
})

export const useChatStore = defineStore('chat', () => {
  const conversations = ref([])
  const currentMessages = ref([])
  const loading = ref(false)
  
  const sendMessage = async (message, image = null) => {
    loading.value = true
    
    try {
      if (!USE_REAL_BACKEND) {
        console.log('🎭 Using mock API...')
        return await mockApi.factCheck(message, image)
      }
      
      console.log('🔄 Using real Python backend...')
      const response = await api.post('/verify', {
        message: message,
        image: image ? 'uploaded' : null
      })
      
      return response.data
      
    } catch (error) {
      console.error('API Error:', error)
      
      if (!USE_REAL_BACKEND) {
        throw error
      }
      
      // Fallback to mock if real backend fails
      if (error.code === 'ECONNREFUSED') {
        console.log('⚠ Backend unavailable, using mock...')
        return await mockApi.factCheck(message, image)
      }
      
      // Fixed: Use backticks for template literal
      throw new Error(`Server error (${error.response?.status}): ${error.response?.data?.error || error.response?.statusText}`);
      
    } finally {
      loading.value = false
    }
  }
  
  const saveConversation = (title, messages) => {
    const conversation = {
      id: Date.now(),
      title: title || 'New Conversation',
      messages,
      timestamp: new Date()
    }
    
    conversations.value.unshift(conversation)
    localStorage.setItem('conversations', JSON.stringify(conversations.value))
  }
  
  const loadConversations = () => {
    const saved = localStorage.getItem('conversations')
    if (saved) {
      conversations.value = JSON.parse(saved)
    }
  }
  
  const getConversations = () => {
    return conversations.value
  }
  
  const clearHistory = () => {
    conversations.value = []
    currentMessages.value = []
    localStorage.removeItem('conversations')
  }
  
  const deleteConversation = (conversationId) => {
    conversations.value = conversations.value.filter(conv => conv.id !== conversationId)
    localStorage.setItem('conversations', JSON.stringify(conversations.value))
  }
  
  const updateConversation = (conversationId, updates) => {
    const index = conversations.value.findIndex(conv => conv.id === conversationId)
    if (index !== -1) {
      conversations.value[index] = { ...conversations.value[index], ...updates }
      localStorage.setItem('conversations', JSON.stringify(conversations.value))
    }
  }
  
  const getConversationById = (conversationId) => {
    return conversations.value.find(conv => conv.id === conversationId)
  }
  
  // Initialize conversations on store creation
  const initializeStore = () => {
    loadConversations()
  }
  
  return {
    conversations,
    currentMessages,
    loading,
    sendMessage,
    saveConversation,
    loadConversations,
    getConversations,
    clearHistory,
    deleteConversation,
    updateConversation,
    getConversationById,
    initializeStore
  }
})