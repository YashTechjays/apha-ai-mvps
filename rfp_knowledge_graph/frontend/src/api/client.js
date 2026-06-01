import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8009' })

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
  register: (data) => api.post('/auth/register', data),
}

export const userApi = {
  me: () => api.get('/users/me'),
  updateProfile: (data) => api.put('/users/me/profile', data),
}

export const matchApi = {
  getMatches: (params) => api.get('/api/rfps/matches', { params }),
  collaborative: (params) => api.get('/api/rfps/recommendations/collaborative', { params }),
  explanation: (rfpId) => api.get(`/api/rfps/${rfpId}/match-explanation`),
}

export const applicationApi = {
  create: (rfpId, data) => api.post(`/api/rfps/${rfpId}/applications`, data),
  update: (rfpId, appId, data) => api.put(`/api/rfps/${rfpId}/applications/${appId}`, data),
  myApplications: (params) => api.get('/users/me/applications', { params }),
}

export const rfpApi = {
  list: (params, config) => api.get('/api/rfps', { params, ...config }),
  detail: (id) => api.get(`/api/rfps/${id}`),
  generateProposal: (id) => api.post(`/api/rfps/${id}/generate-proposal`),
  winRoom: (id, proposal) => api.post(`/api/rfps/${id}/win-room`, proposal ? { proposal } : {}),
}

export const crawlApi = {
  trigger: (url) => api.post('/api/crawl/trigger', url ? { url } : {}),
  status: () => api.get('/api/crawl/status'),
}

export const graphApi = {
  stats: () => api.get('/api/graph/stats'),
  insights: (params) => api.get('/api/graph/insights', { params }),
}

export const recommendationApi = {
  get: (params) => api.get('/api/recommendations', { params }),
}

export const foresightApi = {
  predictions: (params) => api.get('/api/foresight/predictions', { params }),
  personalized: (params) => api.get('/api/foresight/predictions/personalized', { params }),
  organization: (orgName) => api.get(`/api/foresight/organization/${encodeURIComponent(orgName)}`),
}

export const coalitionApi = {
  get: (rfpId, params) => api.get(`/api/rfps/${rfpId}/coalition`, { params }),
}

export const simulatorApi = {
  baseline: (rfpId) => api.get(`/api/simulator/${rfpId}/baseline`),
  run: (rfpId, hypothetical) => api.post(`/api/simulator/${rfpId}`, hypothetical),
}

export const copilotApi = {
  chat: (message) => api.post('/api/copilot/chat', { message }),
}

export default api
