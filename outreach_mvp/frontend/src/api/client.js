import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8007' })

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('outreach_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})
api.interceptors.response.use(r => r, err => {
  if (err.response?.status === 401) {
    localStorage.removeItem('outreach_token')
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
  }
}
export const prospectsApi = {
  list: (params) => api.get('/prospects/', { params }),
  stats: () => api.get('/prospects/stats'),
  import: () => api.post('/prospects/import'),
  score: () => api.post('/prospects/score'),
}
export const campaignsApi = {
  list: () => api.get('/campaigns/'),
  create: (data) => api.post('/campaigns/', data),
  launch: (id, maxProspects) => api.post(`/campaigns/${id}/launch`, null, { params: { max_prospects: maxProspects } }),
  pause: (id) => api.patch(`/campaigns/${id}/pause`),
  get: (id) => api.get(`/campaigns/${id}`),
}
export const analyticsApi = {
  overview: () => api.get('/analytics/overview'),
  campaigns: () => api.get('/analytics/campaigns'),
}
export default api
