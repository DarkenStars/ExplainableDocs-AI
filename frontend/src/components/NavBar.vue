<template>
  <nav class="navbar" :class="{ scrolled: isScrolled }">
    <div class="navbar-content">
      <router-link to="/" class="logo">
        News Advisor AI
      </router-link>
      
      <ul class="nav-links">
        <li><a href="#features">Features</a></li>
        <li><a href="#about">About</a></li>
        <li><a href="#contact">Contact</a></li>
        <li>
          <a href="#" class="bot-link" @click.prevent="openBotLink('whatsapp')">
            💬 WhatsApp Bot
          </a>
        </li>
        <li>
          <a href="#" class="bot-link" @click.prevent="openBotLink('telegram')">
            📨 Telegram Bot
          </a>
        </li>
      </ul>
      
      <router-link to="/chat" class="btn btn-primary">
        Get Started →
      </router-link>
    </div>
  </nav>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'NavBar',
  setup() {
    const isScrolled = ref(false)
    
    const handleScroll = () => {
      isScrolled.value = window.scrollY > 50
    }
    
    const openBotLink = (platform) => {
      const links = {
        whatsapp: 'https://wa.me/1234567890?text=Hi%20News%20Advisor%20AI',
        telegram: 'https://t.me/NewsAdvisorAIBot'
      }
      
      window.open(links[platform], '_blank')
    }
    
    onMounted(() => {
      window.addEventListener('scroll', handleScroll)
    })
    
    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
    })
    
    return {
      isScrolled,
      openBotLink
    }
  }
}
</script>
