import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  login: (username, password) => {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)
    return api.post('/auth/login', form)
  },
}

export const membersApi = {
  list: (params) => api.get('/members/', { params }),
  get: (id) => api.get(`/members/${id}`),
}

export const scoresApi = {
  runScoring: () => api.post('/scores/run'),
  getMemberScores: (id) => api.get(`/scores/member/${id}`),
  getExplanation: (id) => api.get(`/scores/member/${id}/explain`),
  getDistribution: () => api.get('/scores/distribution'),
}

export const alertsApi = {
  list: (params) => api.get('/alerts/', { params }),
  update: (id, data) => api.patch(`/alerts/${id}`, data),
}

export default api
