import { defineStore } from 'pinia'
import api from '@/services/api'

export const useBranchStore = defineStore('branch', {
  state: () => ({
    branches: [],
    activeBranch: localStorage.getItem('active_branch') || 'autoroad school',
    loading: false,
  }),
  actions: {
    async fetchBranches() {
      this.loading = true
      try {
        const res = await api.get('/branches/')
        const list = res.data.results || res.data || []
        if (list.length > 0) {
          this.branches = list
        } else {
          this.branches = [
            { id: 1, name: 'autoroad school' },
            { id: 2, name: 'arss' }
          ]
        }
      } catch (err) {
        console.error('Error fetching branches:', err)
        this.branches = [
          { id: 1, name: 'autoroad school' },
          { id: 2, name: 'arss' }
        ]
      } finally {
        this.loading = false
      }
    },
    setActiveBranch(branchName) {
      this.activeBranch = branchName
      localStorage.setItem('active_branch', branchName)
    },
    isBranchMatch(item) {
      if (!item) return true
      if (!this.activeBranch) return true
      const bName = item.branch_name || item.branch_info?.name || item.branch?.name || (typeof item.branch === 'string' ? item.branch : null)
      if (!bName) return true // Empty branch rows are shown in all branches
      return bName.toLowerCase().trim() === this.activeBranch.toLowerCase().trim()
    }
  }
})
