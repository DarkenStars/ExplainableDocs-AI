<template>
  <div class="chat-container">
    <div class="overlay" v-if="!isDesktop" :class="{ open: sidebarOpen }" @click="sidebarOpen = false"></div>

    <aside :class="['sidebar', { open: sidebarOpen }]">
      <div class="sidebar-header">
        <h3 class="sidebar-title">Conversations</h3>
        <button v-if="!isDesktop" @click="sidebarOpen = false" class="icon-btn close-sidebar-btn" aria-label="Close sidebar">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="sidebar-content">
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

    <main class="chat-main">
      <header class="chat-header">
        <button v-if="!isDesktop" @click="sidebarOpen = true" class="icon-btn" aria-label="Open sidebar">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="5" width="18" height="14" rx="2" ry="2"></rect><line x1="9" y1="5" x2="9" y2="19"></line>
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
                <button v-for="example in quickExamples" :key="example" @click="sendExampleMessage(example)" class="example-btn">
                  {{ example }}
                </button>
              </div>
            </div>
          </div>
          <MessageBubble v-for="message in activeConversation?.messages || []" :key="message.id" :message="message" class="animate-message-in"/>
          <div v-if="chatStore.loading" class="message-bubble ai animate-message-in">
            <div class="message-content"><TypingIndicator /></div>
          </div>
        </div>
      </section>

      <footer class="chat-input-area">
        <div class="chat-input-container">
          <button class="icon-btn" @click="triggerFileInput" aria-label="Attach file">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
          </button>
          <input type="file" ref="fileInput" @change="handleFileSelect" style="display: none;" />
          <textarea v-model="newMessage" @keypress.enter.exact.prevent="handleSendMessage" class="chat-input-field" placeholder="Ask a question or paste a claim..." rows="1" @input="autoGrow" ref="textareaRef" aria-label="Chat input"></textarea>
          <button @click="handleSendMessage" class="send-button" :disabled="!newMessage.trim() || chatStore.loading" title="Send Message" aria-label="Send Message">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></svg>
          </button>
        </div>
        <p class="input-disclaimer">News Advisor AI can make mistakes. Consider checking important information.</p>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue';
import { useChatStore } from '../stores/chat.js';
import MessageBubble from '../components/MessageBubble.vue';
import TypingIndicator from '../components/TypingIndicator.vue';

const chatStore = useChatStore();
const isDesktop = ref(window.innerWidth > 1024);
const sidebarOpen = ref(window.innerWidth > 1024);
const newMessage = ref('');
const selectedFile = ref(null);
const messagesContainer = ref(null);
const textareaRef = ref(null);
const fileInput = ref(null);

const activeConversation = computed(() => chatStore.getActiveConversation);
const quickExamples = computed(() => chatStore.recentUserMessages);

const handleResize = () => {
  isDesktop.value = window.innerWidth > 1024;
  if (isDesktop.value) {
    sidebarOpen.value = true;
  }
};

const handleNewChat = () => {
  chatStore.newChat();
  if (!isDesktop.value) sidebarOpen.value = false;
};

const handleSelectConversation = (id) => {
  chatStore.selectConversation(id);
  if (!isDesktop.value) sidebarOpen.value = false;
};

const triggerFileInput = () => fileInput.value?.click();
const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) selectedFile.value = file;
};

const scrollToBottom = () => nextTick(() => {
  if (messagesContainer.value) messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
});

watch(() => activeConversation.value?.messages, scrollToBottom, { deep: true });

const autoGrow = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto';
    textareaRef.value.style.height = `${textareaRef.value.scrollHeight}px`;
  }
};

const handleSendMessage = async () => {
  const messageContent = newMessage.value.trim();
  if (!messageContent || chatStore.loading) return;
  if (!chatStore.activeConversationId) {
    chatStore.newChat();
    await nextTick();
  }
  const fileToSend = selectedFile.value;
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
  window.addEventListener('resize', handleResize);
  if (chatStore.conversations.length === 0) chatStore.newChat();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* Base Styles */
.chat-container { display: flex; height: 100vh; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #FDFDFD; }
.sidebar { background: #FFFFFF; width: 280px; border-right: 1px solid #DEE2E6; display: flex; flex-direction: column; flex-shrink: 0; }
.sidebar-header { display: flex; justify-content: space-between; align-items: center; padding: 1.5rem 1.5rem 0; }
.sidebar-title { font-weight: 600; font-size: 1.25rem; }
.close-sidebar-btn, .open-sidebar-btn { display: none; }
.sidebar-content { display: flex; flex-direction: column; padding: 1.5rem; height: 100%; overflow-y: auto; }
.new-chat-btn { display: flex; align-items: center; justify-content: center; gap: 0.5rem; font-size: 1rem; font-weight: 500; padding: 0.75rem; margin-bottom: 1.5rem; border-radius: 0.75rem; background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%); color: #FFFFFF; border: none; cursor: pointer; transition: all 0.2s ease; }
.new-chat-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
.conversation-list { flex-grow: 1; }
.conversation-item { cursor: pointer; padding: 0.75rem 1rem; font-weight: 500; border-radius: 0.5rem; margin-bottom: 0.25rem; transition: all 0.2s ease; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.conversation-item:hover { background-color: #E9ECEF; }
.conversation-item.active { background-color: #343A40; color: #FFFFFF; }
.chat-main { flex-grow: 1; display: flex; flex-direction: column; height: 100%; }
.chat-header { flex-shrink: 0; height: 73px; display: flex; align-items: center; justify-content: space-between; padding: 0 1.5rem; background: #FFFFFF; border-bottom: 1px solid #DEE2E6; }
.chat-title { font-weight: 600; font-size: 1.25rem; color: #212529; text-align: center; flex-grow: 1; }
.icon-btn { background: none; border: none; padding: 0.5rem; border-radius: 50%; cursor: pointer; color: #6C757D; transition: all 0.2s ease; }
.icon-btn:hover { color: #343A40; background-color: #E9ECEF; }
.chat-messages { flex-grow: 1; overflow-y: auto; padding: 1rem; }
.chat-thread { max-width: 800px; margin: 0 auto; width: 100%; }
.welcome-card { padding: 1.5rem; text-align: center; }
.welcome-icon { font-size: 2.5rem; margin-bottom: 0.75rem; }
.welcome-card h2 { font-weight: 600; font-size: 1.35rem; margin-bottom: 0.4rem; }
.welcome-card p { margin-bottom: 1.2rem; font-size: 0.95rem; color: #6C757D; }
.quick-examples { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
.chat-input-area { padding: 1rem; background: linear-gradient(180deg, transparent, #FDFDFD 50%); }
.chat-input-container { max-width: 800px; margin: 0 auto; display: flex; align-items: center; gap: 0.5rem; background: #FFFFFF; border-radius: 9999px; padding: 0.5rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.05); border: 1px solid #DEE2E6; }
.chat-input-field { flex-grow: 1; font-family: inherit; font-size: 1rem; padding: 0.5rem; border: none; resize: none; outline: none; max-height: 120px; background: transparent; }
.send-button { background: #343A40; border: none; border-radius: 50%; width: 44px; height: 44px; cursor: pointer; color: #FFFFFF; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease; flex-shrink: 0; }
.send-button:hover:enabled { background: #495057; }
.send-button:disabled { background: #CBD5E1; cursor: not-allowed; }
.input-disclaimer { text-align: center; font-size: 0.75rem; color: #6C757D; margin-top: 1rem; }

/* Mobile and Tablet */
@media (max-width: 1024px) {
  .overlay { display: block; }
  .sidebar { position: fixed; transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
  .close-sidebar-btn, .open-sidebar-btn { display: block; }
  .quick-examples { grid-template-columns: 1fr; }
  .chat-title { font-size: 1.1rem; }
  .chat-header { padding: 0 1rem; }
}
</style>