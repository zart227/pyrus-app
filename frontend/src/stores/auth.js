import { defineStore } from 'pinia'
import api from '../api'

let refreshTimerId = null

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    isAuthenticated: false,
    tokenExpiresIn: null
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
        this.tokenExpiresIn = response.data.expires_in
        this.isAuthenticated = true
        
        await this.fetchUser()
        this.startTokenRefreshTimer()
        
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
        throw error
      }
    },

    async refreshSession() {
      const response = await api.post('/auth/refresh')
      this.token = response.data.access_token
      this.tokenExpiresIn = response.data.expires_in
      this.isAuthenticated = true
      return response.data
    },

    startTokenRefreshTimer() {
      this.stopTokenRefreshTimer()

      const expiresIn = this.tokenExpiresIn || 480 * 60
      const refreshInMs = Math.max((expiresIn - 300) * 1000, 60 * 1000)

      refreshTimerId = setInterval(async () => {
        try {
          await this.refreshSession()
        } catch (error) {
          console.error('Token refresh failed:', error)
          this.stopTokenRefreshTimer()
        }
      }, refreshInMs)
    },

    stopTokenRefreshTimer() {
      if (refreshTimerId) {
        clearInterval(refreshTimerId)
        refreshTimerId = null
      }
    },

    async logout() {
      try {
        await api.post('/auth/logout')
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.stopTokenRefreshTimer()
        this.user = null
        this.token = null
        this.tokenExpiresIn = null
        this.isAuthenticated = false
      }
    },

    async checkAuth() {
      const token = this.getTokenFromCookie()
      if (token) {
        this.token = token
        try {
          await this.fetchUser()
          this.isAuthenticated = true
          this.startTokenRefreshTimer()
        } catch (error) {
          console.error('Auth check failed:', error)
          try {
            await this.refreshSession()
            await this.fetchUser()
            this.isAuthenticated = true
            this.startTokenRefreshTimer()
          } catch (refreshError) {
            console.error('Auth refresh on startup failed:', refreshError)
            this.user = null
            this.token = null
            this.tokenExpiresIn = null
            this.isAuthenticated = false
            this.stopTokenRefreshTimer()
          }
        }
      }
    },

    getTokenFromCookie() {
      const cookies = document.cookie.split(';')
      for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=')
        if (name === 'access_token') {
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
