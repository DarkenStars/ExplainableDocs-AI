<template>
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
      // Check for existing authentication
      authStore.checkAuth()
    })
  }
}
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
