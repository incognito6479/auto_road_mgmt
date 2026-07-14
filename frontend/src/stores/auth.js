import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken:
      localStorage.getItem('access_token') ||
      sessionStorage.getItem('access_token') ||
      null,
    refreshToken:
      localStorage.getItem('refresh_token') ||
      sessionStorage.getItem('refresh_token') ||
      null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async login(phone, password, remember) {
      const response = await api.post('/auth/token/', { phone, password })
      this.accessToken = response.data.access
      this.refreshToken = response.data.refresh

      // Persist based on "Eslab qolish" checkbox
      const storage = remember ? localStorage : sessionStorage
      storage.setItem('access_token', this.accessToken)
      storage.setItem('refresh_token', this.refreshToken)
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('refresh_token')
    },
  },
})
