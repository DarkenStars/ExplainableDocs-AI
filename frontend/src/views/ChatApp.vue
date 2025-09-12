<template>
  <div class="chat-container">
    <aside :class="['sidebar', { open: sidebarOpen }]">
      <div class="sidebar-content">
        <h3 class="sidebar-title">Conversations</h3>
        <button @click="handleNewChat" class="new-chat-btn">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          New Chat
        </button>
        <nav class="conversation-list">
          <div
            v-for="conversation in chatStore.conversations"
            :key="conversation.id"
            :class="['conversation-item', { active: conversation.id === chatStore.activeConversationId }]"
            @click="handleSelectConversation(conversation.id)"
          >
            {{ conversation.title }}
          </div>
        </nav>
      </div>
    </aside>

    <main class="chat-main" :class="{ 'sidebar-open': sidebarOpen }">
      <header class="chat-header">
        <button @click="toggleSidebar" class="icon-btn" aria-label="Toggle Sidebar">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="5" width="18" height="14" rx="2" ry="2"></rect>
            <line x1="9" y1="5" x2="9" y2="19"></line>
          </svg>
        </button>
        <h1 class="chat-title">News Advisor AI</h1>
        <router-link to="/" class="icon-btn" aria-label="Back to Home">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        </router-link>
      </header>

      <section class="chat-messages" ref="messagesContainer">
        <div class="chat-thread">
          <div v-if="!activeConversation || activeConversation.messages.length === 0" class="welcome-message">
            <div class="welcome-card animate-pop-in">
              <div class="welcome-icon">👋</div>
              <h2>Welcome!</h2>
              <p>Your AI-powered partner in combating misinformation.</p>
              <div class="quick-examples">
                <button
                  v-for="example in quickExamples"
                  :key="example"
                  @click="sendExampleMessage(example)"
                  class="example-btn"
                >
                  {{ example }}
                </button>
              </div>
            </div>
          </div>

          <MessageBubble
            v-for="message in activeConversation?.messages || []"
            :key="message.id"
            :message="message"
            class="animate-message-in"
          />

          <div v-if="chatStore.loading" class="message-bubble ai animate-message-in">
            <div class="message-content"><TypingIndicator /></div>
          </div>
        </div>
      </section>

      <footer class="chat-input-area">
        <div class="chat-input-container">
          <button class="icon-btn" @click="triggerFileInput" aria-label="Attach file">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
            </svg>
          </button>
          <input type="file" ref="fileInput" @change="handleFileSelect" style="display: none;" />

          <textarea
            v-model="newMessage"
            @keypress.enter.exact.prevent="handleSendMessage"
            class="chat-input-field"
            placeholder="Ask a question or paste a claim..."
            rows="1"
            @input="autoGrow"
            ref="textareaRef"
            aria-label="Chat input"
          ></textarea>
          <button
            @click="handleSendMessage"
            class="send-button"
            :disabled="!newMessage.trim() || chatStore.loading"
            title="Send Message"
            aria-label="Send Message"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
        <p class="input-disclaimer">News Advisor AI can make mistakes. Consider checking important information.</p>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue';
import { useChatStore } from '../stores/chat.js';
import MessageBubble from '../components/MessageBubble.vue';
import TypingIndicator from '../components/TypingIndicator.vue';

// Initialize the store
const chatStore = useChatStore();

// Component-specific state (UI only)
const sidebarOpen = ref(true);
const newMessage = ref('');
const selectedFile = ref(null);

// Template refs
const messagesContainer = ref(null);
const textareaRef = ref(null);
const fileInput = ref(null);

/**
 * **FIXED**: Use a computed property to get the active conversation reactively.
 * This ensures the view always shows the correct chat's messages.
 */
const activeConversation = computed(() => chatStore.getActiveConversation);

/**
 * **FIXED**: Use the new getter from the store for dynamic examples.
 */
const quickExamples = computed(() => chatStore.recentUserMessages);


const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value;
};

/**
 * **FIXED**: This now correctly calls the store action to create a new chat thread.
 */
const handleNewChat = () => {
  chatStore.newChat();
};

/**
 * **FIXED**: This now correctly calls the store action to switch conversations.
 */
const handleSelectConversation = (id) => {
  chatStore.selectConversation(id);
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
  }
};

// Function to automatically scroll to the bottom of the chat
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// Watch for new messages in the active chat and scroll down
watch(() => activeConversation.value?.messages, scrollToBottom, { deep: true });

const autoGrow = () => { 
  if (textareaRef.value) { 
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px';
  }
};

const handleSendMessage = async () => {
  const messageContent = newMessage.value.trim();
  if (!messageContent || chatStore.loading) return;

  // If no chat is active, create one before sending
  if (!chatStore.activeConversationId) {
    chatStore.newChat();
    await nextTick();
  }

  const fileToSend = selectedFile.value;
  
  // Reset input fields
  newMessage.value = '';
  selectedFile.value = null;
  if (fileInput.value) fileInput.value.value = '';
  autoGrow();

  await chatStore.sendMessage(messageContent, fileToSend);
};

const sendExampleMessage = (example) => {
  newMessage.value = example;
  handleSendMessage();
};

onMounted(() => {
  // If no chats exist after loading, create a new one to start
  if (chatStore.conversations.length === 0) {
    chatStore.newChat();
  }
});
</script>

<style scoped>
/* --- THEME: Royal Elegant (Charcoal Gray & Glacier White) + Bluish Gradient --- */
.chat-container {
  color-scheme: light;
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --color-bg: #FDFDFD;
  --color-sidebar-bg: #FFFFFF;
  --color-accent: #343A40; /* Used for non-gradient elements */
  --color-accent-hover: #495057;
  --color-accent-light: #E9ECEF;
  --color-text-header: #212529;
  --color-text-body: #343A40;
  --color-text-light: #6C757D;
  --color-text-on-accent: #FFFFFF;
  --color-border: #DEE2E6;
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
  --border-radius: 0.75rem;
  --border-radius-pill: 9999px;
  --sidebar-width: 280px;

  /* NEW: Bluish Gradient for Buttons/User Bubbles */
  --gradient-bluish: linear-gradient(135deg, #667EEA 0%, #764BA2 100%); /* Blue to Purple */
  --gradient-bluish-hover: linear-gradient(135deg, #5A6EE0 0%, #6A3E96 100%);
}

/* Animations */
@keyframes popIn {
  from { opacity: 0; transform: translateY(10px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.animate-message-in { animation: popIn 0.4s ease-out forwards; }
.animate-pop-in { animation: popIn 0.5s ease-out forwards; }

/* Base Layout */
.chat-container { display: flex; height: 100vh; font-family: var(--font-family); background-color: var(--color-bg); overflow: hidden; }

/* Sidebar */
.sidebar {
  background: var(--color-sidebar-bg);
  width: var(--sidebar-width);
  border-right: 1px solid var(--color-border);
  position: fixed; top: 0; left: 0;
  height: 100%;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  z-index: 100;
  display: flex; flex-direction: column;
}
.sidebar.open { transform: translateX(0); }
.sidebar-content { display: flex; flex-direction: column; padding: 1.5rem; height: 100%; }
.sidebar-title { font-weight: 600; font-size: 1.25rem; color: var(--color-text-header); margin-bottom: 1.5rem; }
.new-chat-btn {
  display: flex; align-items: center; justify-content: center; gap: 0.5rem; font-size: 1rem;
  font-weight: 500; padding: 0.75rem; margin-bottom: 1.5rem;
  border-radius: var(--border-radius);
  background: var(--gradient-bluish); /* NEW: Gradient background */
  color: var(--color-text-on-accent); border: none; cursor: pointer;
  transition: all 0.2s ease; /* NEW: Added transition for hover effect */
}
.new-chat-btn:hover {
  background: var(--gradient-bluish-hover); /* NEW: Darker gradient on hover */
  transform: translateY(-2px); /* NEW: Slight lift on hover */
  box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* NEW: Subtle shadow on hover */
}
.conversation-list { flex-grow: 1; overflow-y: auto; }
.conversation-item {
  cursor: pointer; padding: 0.75rem 1rem; font-weight: 500;
  border-radius: 0.5rem; margin-bottom: 0.25rem;
  color: var(--color-text-body); transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.conversation-item:hover { background-color: var(--color-accent-light); color: var(--color-accent); }
.conversation-item.active { background-color: var(--color-accent); color: var(--color-text-on-accent); }

/* Main Area */
.chat-main {
  flex-grow: 1; display: flex; flex-direction: column;
  height: 100%; width: 100%; position: relative;
  transition: margin-left 0.3s ease;
  background-color: var(--color-bg);
}
.chat-main.sidebar-open { margin-left: var(--sidebar-width); }
.chat-header {
  flex-shrink: 0; height: 73px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 1.5rem; z-index: 50;
  width: 100%;
  background: var(--color-sidebar-bg);
  border-bottom: 1px solid var(--color-border);
}
.chat-title { font-weight: 600; font-size: 1.25rem; color: var(--color-text-header); }
.icon-btn { background: none; border: none; padding: 0.5rem; border-radius: 50%; cursor: pointer; color: var(--color-text-light); transition: all 0.2s ease; }
.icon-btn:hover { color: var(--color-accent); background-color: var(--color-accent-light); }

/* Chat Message Area */
.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding-top: 90px;
  padding-bottom: 160px;
}
.chat-thread {
  max-width: 800px; /* Same max-width as input container */
  margin: 0 auto;
  padding: 0 1.5rem; /* Horizontal padding for content */
  width: 100%;
}
.welcome-message { max-width: 100%; text-align: center; }
.welcome-card { padding: 1.5rem 2.5rem; }
.welcome-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.welcome-card h2 { font-weight: 600; font-size: 1.35rem; color: var(--color-text-header); margin-bottom: 0.4rem; }
.welcome-card p { margin-bottom: 1.2rem; font-size: 0.95rem; color: var(--color-text-light); }
.quick-examples { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
.example-btn {
  background: var(--color-bg); border: 1px solid var(--color-border);
  border-radius: 0.5rem; padding: 0.6rem 0.8rem; cursor: pointer;
  font-weight: 500; font-size: 0.85rem; color: var(--color-text-body);
  transition: all 0.2s ease;
}
.example-btn:hover { background-color: var(--color-accent-light); border-color: var(--color-accent); color: var(--color-accent); }

/* Floating Input Area */
.chat-input-area {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 1rem 1.5rem 1.5rem;
  background: linear-gradient(180deg, transparent, var(--color-bg) 50%);
  pointer-events: none;
}
.chat-input-container {
  max-width: 800px; margin: 0 auto;
  display: flex; align-items: center; gap: 0.75rem; background: #FFFFFF;
  border-radius: var(--border-radius-pill);
  padding: 0.5rem 0.75rem 0.5rem 0.5rem;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
  pointer-events: all;
}
.chat-input-field {
  flex-grow: 1; font-family: var(--font-family); font-size: 1rem; padding: 0.5rem;
  border: none; resize: none; outline: none; color: var(--color-text-body);
  max-height: 120px; background: transparent;
}
.send-button {
  background: var(--color-accent); border: none;
  border-radius: var(--border-radius);
  width: 44px; height: 44px; cursor: pointer; color: var(--color-text-on-accent);
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s ease; flex-shrink: 0;
}
.send-button:hover:enabled { background: var(--color-accent-hover); }
.send-button:disabled { background: #CBD5E1; cursor: not-allowed; }
.input-disclaimer {
    text-align: center;
    font-size: 0.75rem;
    color: var(--color-text-light);
    margin-top: 1rem;
    pointer-events: all;
}
</style>