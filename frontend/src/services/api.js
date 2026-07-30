import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token =
    localStorage.getItem('access_token') ||
    sessionStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  if (config.method === 'get') {
    const activeBranch = localStorage.getItem('active_branch')
    if (activeBranch) {
      config.params = config.params || {}
      if (!config.params.branch) {
        config.params.branch = activeBranch
      }
    }
  }

  // When creating a new record, stamp it with the currently active branch
  // so it's correctly scoped without every form having to set it manually.
  if (config.method === 'post' && config.data) {
    const activeBranchId = localStorage.getItem('active_branch_id')
    if (activeBranchId) {
      if (config.data instanceof FormData) {
        if (!config.data.has('branch')) {
          config.data.append('branch', activeBranchId)
        }
      } else if (typeof config.data === 'object' && config.data.branch === undefined) {
        config.data.branch = Number(activeBranchId)
      }
    }
  }

  return config
})

export default api
