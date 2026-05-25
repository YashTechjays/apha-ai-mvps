import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || ''

// ── Churn API (/api/churn) ───────────────────────────────────────
const churnApi = axios.create({ baseURL: `${BASE}/api/churn` })
churnApi.interceptors.request.use((c) => {
  const t = localStorage.getItem('churn_token')
  if (t) c.headers.Authorization = `Bearer ${t}`
  return c
})
churnApi.interceptors.response.use((r) => r, (e) => {
  if (e.response?.status === 401) {
    localStorage.removeItem('churn_token')
    window.location.href = '/churn/login'
  }
  return Promise.reject(e)
})

export const churnAuthApi = {
  login: (username, password) => {
    const form = new URLSearchParams()
    form.append('username', username)
    form.append('password', password)
    return churnApi.post('/auth/login', form)
  },
}
export const churnMembersApi = {
  list: (params) => churnApi.get('/members/', { params }),
  get: (id) => churnApi.get(`/members/${id}`),
}
export const churnScoresApi = {
  runScoring: () => churnApi.post('/scores/run'),
  getMemberScores: (id) => churnApi.get(`/scores/member/${id}`),
  getExplanation: (id) => churnApi.get(`/scores/member/${id}/explain`),
  getDistribution: () => churnApi.get('/scores/distribution'),
}
export const churnAlertsApi = {
  list: (params) => churnApi.get('/alerts/', { params }),
  update: (id, data) => churnApi.patch(`/alerts/${id}`, data),
}

// ── Concierge API (/api/concierge) ───────────────────────────────
const conciergeApi = axios.create({ baseURL: `${BASE}/api/concierge` })

export const conciergeChatApi = {
  sendMessage: (sessionToken, message, pageUrl) =>
    conciergeApi.post('/chat/', { session_token: sessionToken, message, page_url: pageUrl }),
  getConversation: (sessionToken) =>
    conciergeApi.get(`/chat/session/${sessionToken}`),
}
export const conciergeLeadApi = {
  captureLead: (sessionToken, email, name, tier) =>
    conciergeApi.post('/leads/', { session_token: sessionToken, email, name, interested_tier: tier }),
}
export const conciergeAnalyticsApi = {
  getSummary: () => conciergeApi.get('/analytics/summary'),
}

// ── CPE Calculator API (/api/cpe) ────────────────────────────────
const cpeApi = axios.create({ baseURL: `${BASE}/api/cpe` })

export const cpeCalculatorApi = {
  calculate: (data) => cpeApi.post('/calculate/', data),
  getFullPlan: (calculationId, sessionId) =>
    cpeApi.get(`/calculate/full/${calculationId}`, { params: { session_id: sessionId } }),
  getStateSeo: (state) => cpeApi.get(`/seo/state/${state}`),
}
export const cpeLeadApi = {
  capture: (data) => cpeApi.post('/leads/', data),
}

// ── Cross-Sell API (/api/crosssell) ──────────────────────────────
const crosssellApi = axios.create({ baseURL: `${BASE}/api/crosssell` })
crosssellApi.interceptors.request.use((c) => {
  const t = localStorage.getItem('crosssell_token')
  if (t) c.headers.Authorization = `Bearer ${t}`
  return c
})
crosssellApi.interceptors.response.use((r) => r, (e) => {
  if (e.response?.status === 401) {
    localStorage.removeItem('crosssell_token')
    window.location.href = '/crosssell/login'
  }
  return Promise.reject(e)
})

export const crosssellAuthApi = {
  login: (u, p) => {
    const f = new URLSearchParams()
    f.append('username', u)
    f.append('password', p)
    return crosssellApi.post('/auth/login', f)
  },
}
export const crosssellScoresApi = {
  runScoring: () => crosssellApi.post('/scores/run'),
  listMembers: (params) => crosssellApi.get('/scores/members', { params }),
  getMemberScores: (id) => crosssellApi.get(`/scores/member/${id}`),
}
export const crosssellNudgesApi = {
  send: (dryRun = true, productFilter = null) =>
    crosssellApi.post('/nudges/send', { dry_run: dryRun, product_filter: productFilter }),
  list: (params) => crosssellApi.get('/nudges/', { params }),
  markClicked: (id) => crosssellApi.patch(`/nudges/${id}/clicked`),
}
export const crosssellAnalyticsApi = {
  overview: () => crosssellApi.get('/analytics/overview'),
  byProduct: () => crosssellApi.get('/analytics/by-product'),
}

// ── Drug Reference API (/api/drugref) ────────────────────────────
const drugrefApi = axios.create({ baseURL: `${BASE}/api/drugref` })
drugrefApi.interceptors.request.use((c) => {
  const t = localStorage.getItem('drugref_token')
  if (t) c.headers.Authorization = `Bearer ${t}`
  return c
})
drugrefApi.interceptors.response.use((r) => r, (e) => {
  if (e.response?.status === 401) {
    localStorage.removeItem('drugref_token')
    const p = window.location.pathname
    if (!p.startsWith('/drug-ref/login') && !p.startsWith('/drug-ref/signup')) {
      window.location.href = '/drug-ref/login'
    }
  }
  return Promise.reject(e)
})

export const drugrefAuth = {
  signup: (data) => drugrefApi.post('/auth/signup', data).then((r) => r.data),
  login: (data) => drugrefApi.post('/auth/login', data).then((r) => r.data),
  me: () => drugrefApi.get('/auth/me').then((r) => r.data),
  apiKeys: {
    list: () => drugrefApi.get('/auth/api-keys').then((r) => r.data),
    create: (label) => drugrefApi.post('/auth/api-keys', { label }).then((r) => r.data),
    revoke: (id) => drugrefApi.delete(`/auth/api-keys/${id}`).then((r) => r.data),
  },
}
export const drugrefQueries = {
  ask: (question, category) =>
    drugrefApi.post('/query', { question, category }).then((r) => r.data),
  feedback: (query_id, thumbs_up, feedback_text) =>
    drugrefApi.post('/query/feedback', { query_id, thumbs_up, feedback_text }).then((r) => r.data),
  history: (limit = 25) =>
    drugrefApi.get('/query/history', { params: { limit } }).then((r) => r.data),
}
export const drugrefSubs = {
  plans: () => drugrefApi.get('/subscriptions/plans').then((r) => r.data),
  me: () => drugrefApi.get('/subscriptions/me').then((r) => r.data),
  checkout: (plan_code) =>
    drugrefApi.post('/subscriptions/checkout', { plan_code }).then((r) => r.data),
  cancel: () => drugrefApi.post('/subscriptions/cancel').then((r) => r.data),
}
export const drugrefAnalytics = {
  usage: (days = 30) =>
    drugrefApi.get('/analytics/usage', { params: { days } }).then((r) => r.data),
}

// ── Email MVP API (/api/email) ───────────────────────────────────
const emailApi = axios.create({ baseURL: `${BASE}/api/email` })

export const emailMembersApi = {
  list: (params) => emailApi.get('/members/', { params }),
  get: (id) => emailApi.get(`/members/${id}`),
  getBenefitSummary: (id, month) =>
    emailApi.get(`/members/${id}/benefit-summary`, { params: { send_month: month } }),
}
export const emailSendsApi = {
  list: (params) => emailApi.get('/emails/', { params }),
  getMemberEmails: (id) => emailApi.get(`/emails/member/${id}`),
  preview: (id, month) =>
    emailApi.get(`/emails/preview/${id}`, { params: { send_month: month } }),
  sendSingle: (id, month) =>
    emailApi.post(`/emails/send/${id}`, null, { params: { send_month: month } }),
  runBatch: (month, dryRun) =>
    emailApi.post('/emails/run-batch', null, { params: { send_month: month, dry_run: dryRun } }),
}
export const emailAnalyticsApi = {
  summary: (month) => emailApi.get('/analytics/summary', { params: { send_month: month } }),
  topMembers: (month) => emailApi.get('/analytics/top-members', { params: { send_month: month } }),
  byStatus: (month) => emailApi.get('/analytics/by-status', { params: { send_month: month } }),
}

// ── Acquisition Funnels API (/api/acquisition) ──────────────────
const acqApi = axios.create({ baseURL: `${BASE}/api/acquisition` })

export const acqSalaryApi = {
  benchmark: (data) => acqApi.post('/salary/benchmark', data),
  getStates: () => acqApi.get('/salary/states'),
  getSpecialties: () => acqApi.get('/salary/specialties'),
}
export const acqInteractionApi = {
  check: (data) => acqApi.post('/interactions/check', data),
  search: (prefix) => acqApi.post('/interactions/search', { prefix, limit: 8 }),
}
export const acqCareerApi = {
  score: (data) => acqApi.post('/career/score', data),
  getActionPlan: (usageId, sessionId) =>
    acqApi.get(`/career/action-plan/${usageId}`, { params: { session_id: sessionId } }),
}
export const acqLeadApi = {
  capture: (data) => acqApi.post('/leads/', data),
}
export const acqAnalyticsApi = {
  summary: () => acqApi.get('/analytics/summary'),
}

// ── Outreach Automation API (/api/outreach) ──────────────────────
const outreachApi = axios.create({ baseURL: `${BASE}/api/outreach` })
outreachApi.interceptors.request.use((c) => {
  const t = localStorage.getItem('outreach_token')
  if (t) c.headers.Authorization = `Bearer ${t}`
  return c
})
outreachApi.interceptors.response.use((r) => r, (e) => {
  if (e.response?.status === 401) {
    localStorage.removeItem('outreach_token')
    window.location.href = '/outreach/login'
  }
  return Promise.reject(e)
})

export const outreachAuthApi = {
  login: (u, p) => {
    const f = new URLSearchParams()
    f.append('username', u)
    f.append('password', p)
    return outreachApi.post('/auth/login', f)
  },
}
export const outreachProspectsApi = {
  list: (params) => outreachApi.get('/prospects/', { params }),
  stats: () => outreachApi.get('/prospects/stats'),
  import: () => outreachApi.post('/prospects/import'),
  score: () => outreachApi.post('/prospects/score'),
}
export const outreachCampaignsApi = {
  list: () => outreachApi.get('/campaigns/'),
  create: (data) => outreachApi.post('/campaigns/', data),
  launch: (id, maxProspects) => outreachApi.post(`/campaigns/${id}/launch`, null, { params: { max_prospects: maxProspects } }),
  pause: (id) => outreachApi.patch(`/campaigns/${id}/pause`),
  get: (id) => outreachApi.get(`/campaigns/${id}`),
}
export const outreachAnalyticsApi = {
  overview: () => outreachApi.get('/analytics/overview'),
  campaigns: () => outreachApi.get('/analytics/campaigns'),
}

export { churnApi, conciergeApi, cpeApi, crosssellApi, drugrefApi, emailApi, acqApi, outreachApi }
