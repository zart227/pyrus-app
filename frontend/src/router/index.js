import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import TasksView from '../views/TasksView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      name: 'tasks',
      component: TasksView,
      meta: { requiresAuth: true }
    }
  ]
})

// Защита маршрутов
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Проверяем авторизацию если еще не проверяли
  if (!authStore.isAuthenticated) {
    try {
      await authStore.checkAuth()
    } catch (error) {
      console.error('Auth check failed in router:', error)
    }
  }
  
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  
  if (requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (requiresGuest && authStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router 