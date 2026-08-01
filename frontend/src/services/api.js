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

function getRefreshToken() {
  return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
}

// Whichever storage currently holds the refresh token is the one "Eslab
// qolish" chose at login — keep writing refreshed tokens back to that
// same storage.
function getTokenStorage() {
  return localStorage.getItem('refresh_token') ? localStorage : sessionStorage
}

function setTokens(access, refresh) {
  const storage = getTokenStorage()
  storage.setItem('access_token', access)
  if (refresh) storage.setItem('refresh_token', refresh)
}

function clearTokensAndRedirect() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  sessionStorage.removeItem('access_token')
  sessionStorage.removeItem('refresh_token')
  if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

// The access token expires in an hour; without this, every request made
// after that silently 401s — the user stays "logged in" on screen but no
// data ever loads again until they manually refresh the page. This
// transparently exchanges the refresh token for a new access token on the
// first 401 and retries the original request once. Concurrent 401s during
// a refresh share the single in-flight refresh call instead of each firing
// their own (which would race to rotate the refresh token).
let refreshPromise = null

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    const isAuthEndpoint = config?.url && config.url.includes('/auth/token/')
    if (!response || response.status !== 401 || config._retry || isAuthEndpoint) {
      return Promise.reject(error)
    }

    const refreshToken = getRefreshToken()
    if (!refreshToken) {
      clearTokensAndRedirect()
      return Promise.reject(error)
    }

    config._retry = true

    try {
      if (!refreshPromise) {
        refreshPromise = axios
          .post(`${import.meta.env.VITE_API_URL}/auth/token/refresh/`, { refresh: refreshToken })
          .then((res) => {
            setTokens(res.data.access, res.data.refresh)
            return res.data.access
          })
          .finally(() => {
            refreshPromise = null
          })
      }
      const newAccessToken = await refreshPromise
      config.headers.Authorization = `Bearer ${newAccessToken}`
      return api(config)
    } catch (refreshErr) {
      clearTokensAndRedirect()
      return Promise.reject(refreshErr)
    }
  }
)

export default api
