<template>
  <header class="navbar" :class="{ scrolled: isScrolled }">
    <div class="navbar-content">
      <router-link to="/" class="logo">
        News Advisor AI
      </router-link>
      
      <nav class="nav-links">
        <a href="#features">Features</a>
        <a href="#about">About</a>
        <a href="https://wa.me/1234567890?text=Hi" target="_blank">WhatsApp</a>
        <a href="https://t.me/NewsAdvisorAIBot" target="_blank">Telegram</a>
      </nav>
      
      <div class="nav-actions">
        <router-link to="/chat" class="btn btn-primary">
          Get Started
        </router-link>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const isScrolled = ref(false);

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20;
};

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: transparent;
  padding: 1.5rem 5%;
  transition: background-color 0.3s ease, border-bottom 0.3s ease;
}

.navbar.scrolled {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border);
}

body.dark-theme .navbar.scrolled {
    background: rgba(26, 26, 26, 0.8);
}

.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.logo {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  text-decoration: none;
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  list-style: none;
  gap: 2rem;
  align-items: center;
}

.nav-links a {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  transition: color 0.2s ease;
}

.nav-links a:hover {
  color: var(--color-text-primary);
}

.nav-actions {
  display: flex;
  align-items: center;
}
</style>