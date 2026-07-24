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
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isSuperuser: (state) => !!(state.user && (state.user.is_superuser || state.user.role === 'superuser')),
    isAdminOrSuperuser: (state) => !!(state.user && (state.user.is_superuser || state.user.role === 'superuser' || state.user.role === 'admin')),
    isStaff: (state) => !!(state.user && (state.user.is_staff || state.user.is_superuser || state.user.role === 'admin' || state.user.role === 'superuser')),
    isMechanic: (state) => !!(state.user && state.user.role === 'mechanic'),
  },

  actions: {
    async fetchCurrentUser() {
      if (!this.accessToken) return null
      try {
        const response = await api.get('/users/me/')
        this.user = response.data
        return this.user
      } catch (err) {
        console.error('Failed to fetch user:', err)
        return null
      }
    },

    async login(phone, password, remember) {
      const response = await api.post('/auth/token/', { phone, password })
      this.accessToken = response.data.access
      this.refreshToken = response.data.refresh

      // Persist based on "Eslab qolish" checkbox
      const storage = remember ? localStorage : sessionStorage
      storage.setItem('access_token', this.accessToken)
      storage.setItem('refresh_token', this.refreshToken)

      await this.fetchCurrentUser()
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('refresh_token')
    },
  },
})
