<!-- <template>
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
</style> -->

<template>
  <header class="navbar" :class="{ scrolled: isScrolled, 'mobile-menu-open': isMobileMenuOpen }">
    <div class="navbar-content">
      <router-link to="/" class="logo" @click="scrollToTop">
        News Advisor AI
      </router-link>

      <nav class="nav-links">
        <a href="#features">Features</a>
        <a href="https://github.com/DarkenStars/ExplainableDocs-AI" target="_blank" rel="noopener noreferrer">About</a>
        <a href="https://t.me/NewsAdvisorAIBot" target="_blank">Telegram</a>
        <a href="https://wa.me/14155238886?text=Hi" target="_blank">WhatsApp</a>
      </nav>

      <div class="nav-actions">
        <button @click="themeStore.toggleTheme" class="btn-icon" aria-label="Toggle Dark Mode">
          <svg v-if="!themeStore.isDark" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
        </button>
        <router-link to="/chat" class="btn btn-primary desktop-only">
          Get Started
        </router-link>
      </div>
      
      <button @click="toggleMobileMenu" class="mobile-menu-button" aria-label="Toggle Menu">
        <svg v-if="!isMobileMenuOpen" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div class="mobile-menu" :class="{ open: isMobileMenuOpen }">
      <a href="#features" @click="closeMobileMenu">Features</a>
      <a href="https://github.com/DarkenStars/ExplainableDocs-AI" target="_blank" rel="noopener noreferrer" @click="closeMobileMenu">About</a>
      <a href="https://t.me/NewsAdvisorAIBot" target="_blank" @click="closeMobileMenu">Telegram</a>
      <router-link to="/chat" class="btn btn-primary" @click="closeMobileMenu">
        Get Started
      </router-link>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useThemeStore } from '../stores/theme.js';

const themeStore = useThemeStore();
const isScrolled = ref(false);
const isMobileMenuOpen = ref(false);

const handleScroll = () => {
  isScrolled.value = window.scrollY > 20;
};

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
  closeMobileMenu();
};

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};

watch(isMobileMenuOpen, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  document.body.style.overflow = ''; // Cleanup on component destroy
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
  z-index: 1002; /* Ensure logo is above mobile menu background */
}

/* Make logo on dark theme visible when mobile menu is open */
.navbar.mobile-menu-open .logo {
  color: var(--color-text-primary);
}
body.dark-theme .navbar.mobile-menu-open .logo {
  color: var(--color-text-primary);
}


.nav-links {
  display: flex;
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
  gap: 1rem;
}

.btn-icon {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  padding: 0.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 1002;
}

.btn-icon:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.mobile-menu-button {
  display: none; /* Hidden by default */
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-primary);
  z-index: 1002; /* Above mobile menu */
  padding: 0.5rem;
}

.mobile-menu {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  background: var(--color-surface);
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  transform: translateY(-100%);
  transition: transform 0.3s ease-in-out;
  z-index: 1001; /* Below the header content but above the page */
  visibility: hidden;
}

.mobile-menu.open {
  transform: translateY(0);
  visibility: visible;
}

.mobile-menu a {
  color: var(--color-text-primary);
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: 500;
}

.mobile-menu .btn-primary {
  color: var(--color-text-on-primary);
}

/* --- Media Query for Mobile --- */
@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  .desktop-only {
    display: none;
  }
  .mobile-menu-button {
    display: flex;
  }
}
</style>