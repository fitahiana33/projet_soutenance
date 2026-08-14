import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },

  actions: {
    async login(email, password) {
      try {
        const { data } = await api.post('/auth/login', { email, password })
        this.token = data.access_token
        localStorage.setItem('token', this.token)

        await this.fetchCurrentUser()
        return { success: true }
      } catch (error) {
        const message =
          error.response && error.response.data && error.response.data.detail
            ? error.response.data.detail
            : 'Email ou mot de passe incorrect'
        return { success: false, message }
      }
    },

    async fetchCurrentUser() {
      try {
        const { data } = await api.get('/auth/me')
        this.user = data
        localStorage.setItem('user', JSON.stringify(data))
        return data
      } catch (error) {
        this.logout()
        return null
      }
    },

    async restoreSession() {
      if (!this.token) {
        return false
      }
      const user = await this.fetchCurrentUser()
      return !!user
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
