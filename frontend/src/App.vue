<!-- <template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()
    
    onMounted(() => {
      
      authStore.checkAuth()
    })
  }
}
</script>

<style>
#app {
  min-height: 100vh;
}
</style> -->
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from './stores/auth';
import { useThemeStore } from './stores/theme'; // 1. Import the new theme store

// 2. Initialize the theme store. This is what activates the theme on app load.
useThemeStore(); 

const authStore = useAuthStore();
    
onMounted(() => {
  authStore.checkAuth();
});
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
