import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    isAuthenticated: false
  }),

  getters: {
    isLoggedIn: (state) => state.isAuthenticated && state.user !== null
  },

  actions: {
    async login(login, securityKey) {
      try {
        const response = await api.post('/auth/login', {
          login,
          security_key: securityKey
        })
        
        this.token = response.data.access_token
        this.isAuthenticated = true
        
        // Получаем информацию о пользователе
        await this.fetchUser()
        
        return { success: true }
      } catch (error) {
        console.error('Login error:', error)
        return { 
          success: false, 
          error: error.response?.data?.detail || 'Ошибка авторизации' 
        }
      }
    },

    async register(login, securityKey) {
      try {
        const response = await api.post('/auth/register', {
          login,
          security_key: securityKey
        })
        
        return { success: true, user: response.data }
      } catch (error) {
        console.error('Registration error:', error)
        return { 
          success: false, 
          error: error.response?.data?.detail || 'Ошибка регистрации' 
        }
      }
    },

    async fetchUser() {
      try {
        const response = await api.get('/auth/me')
        this.user = response.data
      } catch (error) {
        console.error('Fetch user error:', error)
        // Просто выбрасываем ошибку, не вызываем logout
        throw error
      }
    },

    async logout() {
      try {
        await api.post('/auth/logout')
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.user = null
        this.token = null
        this.isAuthenticated = false
      }
    },

    // Проверка авторизации при загрузке приложения
    async checkAuth() {
      const token = this.getTokenFromCookie()
      if (token) {
        this.token = token
        try {
          await this.fetchUser()
          // Только после успешного получения пользователя устанавливаем isAuthenticated
          this.isAuthenticated = true
        } catch (error) {
          console.error('Auth check failed:', error)
          // Если не удалось получить пользователя, сбрасываем состояние
          this.user = null
          this.token = null
          this.isAuthenticated = false
        }
      }
    },

    getTokenFromCookie() {
      const cookies = document.cookie.split(';')
      for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=')
        if (name === 'access_token') {
          // Убираем кавычки и префикс "Bearer " если есть
          let token = value.replace(/"/g, '')
          if (token.startsWith('Bearer ')) {
            token = token.substring(7)
          }
          return token
        }
      }
      return null
    }
  }
})
