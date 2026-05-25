import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8006',
})

export const salaryApi = {
  benchmark: (data) => api.post('/salary/benchmark', data),
  getStates: () => api.get('/salary/states'),
  getSpecialties: () => api.get('/salary/specialties'),
}

export const interactionApi = {
  check: (data) => api.post('/interactions/check', data),
  search: (prefix) => api.post('/interactions/search', { prefix, limit: 8 }),
}

export const careerApi = {
  score: (data) => api.post('/career/score', data),
  getActionPlan: (usageId, sessionId) =>
    api.get(`/career/action-plan/${usageId}`, { params: { session_id: sessionId } }),
}

export const leadApi = {
  capture: (data) => api.post('/leads/', data),
}

export const analyticsApi = {
  summary: () => api.get('/analytics/summary'),
}

export default api
