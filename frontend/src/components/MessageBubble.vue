<!-- <template>
  <div class="message-bubble" :class="{ user: message.type === 'user', ai: message.type === 'ai' }">
    <div class="message-content">
      
      <div v-if="message.type === 'user'" class="user-message">
        <p>{{ message.content }}</p>
        <div v-if="message.image" class="message-image">
          <img :src="message.image" alt="User uploaded image" class="uploaded-image" />
        </div>
      </div>
      
      
      <div v-else class="ai-message">
        <div v-if="message.factCheck">
          <FactCheckResult :result="message.factCheck" />
        </div>
        <div v-else>
          <p>{{ message.content }}</p>
        </div>
      </div>
    </div>
    
    <div class="message-timestamp">
      {{ formatTime(message.timestamp) }}
    </div>
  </div>
</template>

<script>
import FactCheckResult from './FactCheckResult.vue'

export default {
  name: 'MessageBubble',
  components: {
    FactCheckResult
  },
  props: {
    message: {
      type: Object,
      required: true
    }
  },
  setup() {
    const formatTime = (timestamp) => {
      return new Intl.DateTimeFormat('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      }).format(new Date(timestamp))
    }
    
    return {
      formatTime
    }
  }
}
</script>

<style scoped>
.message-image {
  margin-top: 1rem;
}

.uploaded-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: var(--radius-md);
  object-fit: cover;
}

.message-timestamp {
  font-size: 0.75rem;
  opacity: 0.6;
  text-align: center;
  margin-top: 0.5rem;
  color: var(--text-muted);
}
</style> -->
<template>
  <div class="message-bubble" :class="{ user: message.type === 'user', ai: message.type === 'ai' }">
    <div class="message-content">
      <div v-if="message.type === 'user'" class="user-message">
        <p v-if="message.content">{{ message.content }}</p>
        <div v-if="message.image" class="message-image">
          <img :src="message.image" alt="User uploaded content" class="uploaded-image" />
        </div>
      </div>
      
      <div v-else class="ai-message">
        <FactCheckResult v-if="message.factCheck" :result="message.factCheck" />
        <p v-else>{{ message.content }}</p>
      </div>
    </div>
    
    <div class="message-timestamp">
      {{ formatTime(message.timestamp) }}
    </div>
  </div>
</template>

<script>
import FactCheckResult from './FactCheckResult.vue'

export default {
  name: 'MessageBubble',
  components: {
    FactCheckResult
  },
  props: {
    message: {
      type: Object,
      required: true
    }
  },
  setup() {
    const formatTime = (timestamp) => {
      return new Intl.DateTimeFormat('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      }).format(new Date(timestamp))
    }
    
    return {
      formatTime
    }
  }
}
</script>

<style scoped>
/* Main bubble layout */
.message-bubble {
  max-width: 80%;
  margin-bottom: 0.25rem; /* Reduced margin */
  display: flex;
  flex-direction: column;
  font-size: 1rem;
  word-wrap: break-word;
  line-height: 1.5;
  white-space: pre-wrap;
}
.message-bubble.user {
  margin-left: auto;
  align-items: flex-end; /* Align timestamp to the right */
}
.message-bubble.ai {
  margin-right: auto;
  align-items: flex-start; /* Align timestamp to the left */
}

/* Content container styling */
.message-content {
  padding: 0.75rem 1.125rem;
  border-radius: var(--border-radius);
  user-select: text;
}
.message-bubble.user > .message-content {
  background: var(--gradient-bluish); /* NEW: Gradient background for user bubbles */
  color: var(--color-text-on-accent);
}
.message-bubble.ai > .message-content {
  background: #FFFFFF;
  border: 1px solid var(--color-border);
  color: var(--color-text-body);
}

/* User-uploaded image styling */
.message-image {
  margin-top: 0.75rem;
  background-color: rgba(0,0,0,0.1);
  border-radius: calc(var(--border-radius) - 4px); /* Slightly smaller radius */
}
.uploaded-image {
  max-width: 100%;
  max-height: 300px;
  display: block;
  border-radius: calc(var(--border-radius) - 4px);
  object-fit: cover;
}
.user-message p {
  margin: 0; /* Remove default paragraph margin */
}

/* Timestamp styling */
.message-timestamp {
  font-size: 0.75rem;
  color: var(--color-text-light);
  margin-top: 0.5rem;
  padding: 0 0.5rem;
}
</style>