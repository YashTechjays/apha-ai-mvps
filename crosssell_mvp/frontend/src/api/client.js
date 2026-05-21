import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8004' })

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

api.interceptors.response.use(r => r, err => {
  if (err.response?.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }
  return Promise.reject(err)
})

export const authApi = {
  login: (u, p) => {
    const f = new URLSearchParams()
    f.append('username', u)
    f.append('password', p)
    return api.post('/auth/login', f)
  },
}

export const scoresApi = {
  runScoring: () => api.post('/scores/run'),
  listMembers: (params) => api.get('/scores/members', { params }),
  getMemberScores: (id) => api.get(`/scores/member/${id}`),
}

export const nudgesApi = {
  send: (dryRun = true, productFilter = null) =>
    api.post('/nudges/send', { dry_run: dryRun, product_filter: productFilter }),
  list: (params) => api.get('/nudges/', { params }),
  markClicked: (id) => api.patch(`/nudges/${id}/clicked`),
}

export const analyticsApi = {
  overview: () => api.get('/analytics/overview'),
  byProduct: () => api.get('/analytics/by-product'),
}

export default api
