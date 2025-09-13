<!-- <template>
  <div class="typing-indicator">
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  </div>
</template>

<script>
export default {
  name: 'TypingIndicator'
}
</script>

<style scoped>
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 1rem;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  
  background: var(--color-text-secondary); 
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 80%, 100% { 
    transform: scale(0.8); 
    opacity: 0.5; 
  }
  40% { 
    transform: scale(1.2); 
    opacity: 1; 
  }
}
</style> -->
<template>
  <div class="typing-indicator">
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  </div>
</template>

<script>
export default {
  name: 'TypingIndicator'
}
</script>

<style scoped>
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 1rem;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  /* FIXED: Uses a variable that works in both themes */
  background-color: var(--color-secondary); 
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 80%, 100% { 
    transform: scale(0.6); 
    opacity: 0.5; 
  }
  40% { 
    transform: scale(1.0); 
    opacity: 1; 
  }
}
</style>