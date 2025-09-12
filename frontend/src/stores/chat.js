import { defineStore } from 'pinia';
import { ref, watch, computed } from 'vue';
// FIXED: The import path now includes the .js extension for full clarity.
import api from '@/services/api.js'; 

export const useChatStore = defineStore('chat', () => {
  // --- STATE ---
  const conversations = ref([]);
  const activeConversationId = ref(null);
  const loading = ref(false);

  // --- GETTERS ---
  const getActiveConversation = computed(() => {
    if (!activeConversationId.value) return null;
    return conversations.value.find(c => c.id === activeConversationId.value);
  });

  const recentUserMessages = computed(() => {
    const userMessages = new Set();
    for (let i = conversations.value.length - 1; i >= 0; i--) {
      const conv = conversations.value[i];
      for (let j = conv.messages.length - 1; j >= 0; j--) {
        const msg = conv.messages[j];
        if (msg.type === 'user' && msg.content.trim()) {
          userMessages.add(msg.content.trim());
        }
        if (userMessages.size >= 3) {
          return Array.from(userMessages);
        }
      }
    }
    return userMessages.size > 0 ? Array.from(userMessages) : [
      'Is this image altered?', 'Fact-check: election fraud', '5G health risks'
    ];
  });

  // --- ACTIONS ---
  const loadConversations = () => {
    const saved = localStorage.getItem('conversations');
    if (saved) {
      conversations.value = JSON.parse(saved);
      if (!activeConversationId.value && conversations.value.length > 0) {
        activeConversationId.value = conversations.value[0].id;
      }
    }
  };

  const newChat = () => {
    const newConversation = {
      id: Date.now(),
      title: 'New Chat',
      messages: [],
      timestamp: new Date(),
    };
    conversations.value.unshift(newConversation);
    activeConversationId.value = newConversation.id;
  };

  const selectConversation = (id) => {
    activeConversationId.value = id;
  };

  const sendMessage = async (message, image = null) => {
    if (!getActiveConversation.value) {
      newChat();
    }
    const conversation = getActiveConversation.value;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      image: image ? URL.createObjectURL(image) : null,
      timestamp: new Date(),
    };
    conversation.messages.push(userMessage);

    if (conversation.messages.length === 1 && message.trim()) {
      conversation.title = message.length > 30 ? `${message.substring(0, 27)}...` : message;
    }

    loading.value = true;
    try {
      const responseData = await api.verifyClaim(message);
      
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: '',
        factCheck: responseData,
        timestamp: new Date(),
      };
      conversation.messages.push(aiMessage);

    } catch (error) {
      console.error('API Error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: `Sorry, an error occurred: ${error.message}`,
        factCheck: null,
        timestamp: new Date(),
      };
      conversation.messages.push(errorMessage);
    } finally {
      loading.value = false;
    }
  };

  // --- PERSISTENCE ---
  watch(
    conversations,
    (newConversations) => {
      localStorage.setItem('conversations', JSON.stringify(newConversations));
    },
    { deep: true }
  );

  // --- INITIALIZATION ---
  loadConversations();

  return {
    conversations,
    activeConversationId,
    loading,
    getActiveConversation,
    recentUserMessages,
    newChat,
    selectConversation,
    sendMessage,
  };
});