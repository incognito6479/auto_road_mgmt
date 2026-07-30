import { defineStore } from 'pinia'
import api from '@/services/api'

const storedBranchId = localStorage.getItem('active_branch_id')

export const useBranchStore = defineStore('branch', {
  state: () => ({
    branches: [],
    // Empty string = no branch selected. Superusers have no home branch of
    // their own, so "unselected" must mean "no restriction", not a silent
    // default to some particular branch.
    activeBranch: localStorage.getItem('active_branch') || '',
    // Numeric id of the active branch — this is what gets sent to the backend
    // when creating new records. Resolved from the branches list if unknown.
    activeBranchId: storedBranchId ? Number(storedBranchId) : null,
    loading: false,
  }),
  actions: {
    async fetchBranches() {
      this.loading = true
      try {
        const res = await api.get('/branches/')
        const list = res.data.results || res.data || []
        this.branches = list
      } catch (err) {
        console.error('Error fetching branches:', err)
        this.branches = []
      } finally {
        this.loading = false
        // If a branch name was already chosen (persisted from a previous
        // session) but we don't know its id yet, resolve it now. Never pick
        // a branch that wasn't explicitly selected.
        if (this.activeBranch && this.activeBranchId == null) {
          const found = this.branches.find(b => b.name === this.activeBranch)
          if (found) this.setActiveBranch(this.activeBranch, found.id)
        }
      }
    },
    setActiveBranch(branchName, branchId = null) {
      this.activeBranch = branchName || ''

      if (this.activeBranch) {
        localStorage.setItem('active_branch', this.activeBranch)
        if (branchId == null) {
          const found = this.branches.find(b => b.name === this.activeBranch)
          branchId = found ? found.id : null
        }
      } else {
        // "All branches" selected — clear any previous restriction entirely.
        localStorage.removeItem('active_branch')
        branchId = null
      }

      this.activeBranchId = branchId
      if (branchId != null) {
        localStorage.setItem('active_branch_id', String(branchId))
      } else {
        localStorage.removeItem('active_branch_id')
      }
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
