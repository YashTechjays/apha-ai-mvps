import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001',
})

export const chatApi = {
  sendMessage: (sessionToken, message, pageUrl) =>
    api.post('/chat/', { session_token: sessionToken, message, page_url: pageUrl }),
  getConversation: (sessionToken) =>
    api.get(`/chat/session/${sessionToken}`),
}

export const leadApi = {
  captureLead: (sessionToken, email, name, tier) =>
    api.post('/leads/', { session_token: sessionToken, email, name, interested_tier: tier }),
}

export const analyticsApi = {
  getSummary: () => api.get('/analytics/summary'),
}

export default api
