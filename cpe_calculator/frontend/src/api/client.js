import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8003',
})

export const calculatorApi = {
  calculate: (data) => api.post('/calculate/', data),
  getFullPlan: (calculationId, sessionId) =>
    api.get(`/calculate/full/${calculationId}`, { params: { session_id: sessionId } }),
  getStateSeo: (state) => api.get(`/seo/state/${state}`),
}

export const leadApi = {
  capture: (data) => api.post('/leads/', data),
}

export default api
