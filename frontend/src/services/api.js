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
  return config
})

export default api
