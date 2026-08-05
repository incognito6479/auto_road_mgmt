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
    isAdmin: (state) => !!(state.user && state.user.role === 'admin' && !state.user.is_superuser),
    isMechanic: (state) => !!(state.user && state.user.role === 'mechanic'),
    isInstructor: (state) => !!(state.user && state.user.role === 'instructor'),
    isCoordinator: (state) => !!(state.user && state.user.role === 'coordinator'),
    isStudent: (state) => !!(state.user && state.user.role === 'student'),

    // Instructors and coordinators share one permission profile ("teaching staff").
    isTeachingStaff: (state) => !!(state.user && (state.user.role === 'instructor' || state.user.role === 'coordinator')),

    // ── Capability getters — views should prefer these over raw role checks ──

    /** Returning money to a student is superuser-only; admins are excluded. */
    canReturnMoney: (state) => !!(state.user && (state.user.is_superuser || state.user.role === 'superuser')),

    /** Accepting/among-staff money movement: superuser + admin only. */
    canManageFinances: (state) => !!(state.user && (state.user.is_superuser || state.user.role === 'superuser' || state.user.role === 'admin')),

    /** Mechanics may edit enrollment placement (learning place/time, instructor, teacher). */
    canEditEnrollmentPlacement: (state) => !!(state.user && (
      state.user.is_superuser || state.user.role === 'superuser' ||
      state.user.role === 'admin' || state.user.role === 'mechanic'
    )),

    /** Car records are editable by admin/superuser and mechanics. */
    canEditCars: (state) => !!(state.user && (
      state.user.is_superuser || state.user.role === 'superuser' ||
      state.user.role === 'admin' || state.user.role === 'mechanic'
    )),

    /** Instructors and theory teachers (coordinators), plus admin/superuser, upload certificates. */
    canUploadCertificates: (state) => !!(state.user && (
      state.user.is_superuser || state.user.role === 'superuser' ||
      state.user.role === 'admin' || state.user.role === 'instructor' || state.user.role === 'coordinator'
    )),

    /** Driving-lesson history is recorded by students themselves, plus admin/superuser. */
    canAddDrivingLesson: (state) => !!(state.user && (
      state.user.is_superuser || state.user.role === 'superuser' ||
      state.user.role === 'admin' || state.user.role === 'student'
    )),

    /** Only students leave reviews for their teachers/instructors. */
    canLeaveReviews: (state) => !!(state.user && state.user.role === 'student'),

    /** Where this role lands right after login. */
    homeRoute() {
      const u = this.user
      if (!u) return { name: 'home' }
      if (u.role === 'student') return { name: 'student-detail', params: { id: u.id } }
      if (u.role === 'instructor' || u.role === 'coordinator') return { name: 'user-detail', params: { id: u.id } }
      if (u.role === 'mechanic') return { name: 'groups' }
      return { name: 'home' }
    },
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

    async logout() {
      const refreshToken = this.refreshToken

      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('refresh_token')

      if (refreshToken) {
        try {
          await api.post('/auth/token/blacklist/', { refresh: refreshToken })
        } catch (err) {
          // Token may already be expired/blacklisted — local state is
          // already cleared above, so this is best-effort only.
          console.error('Failed to blacklist refresh token:', err)
        }
      }
    },
  },
})
