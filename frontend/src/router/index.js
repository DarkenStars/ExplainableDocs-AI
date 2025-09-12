import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '../views/LandingPage.vue'
import ChatApp from '../views/ChatApp.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatApp
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
