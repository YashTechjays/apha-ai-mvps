import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  timeout: 60000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("apha_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("apha_token");
      if (window.location.pathname !== "/login" && window.location.pathname !== "/signup") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default api;

export const auth = {
  signup: (data) => api.post("/auth/signup", data).then((r) => r.data),
  login: (data) => api.post("/auth/login", data).then((r) => r.data),
  me: () => api.get("/auth/me").then((r) => r.data),
  apiKeys: {
    list: () => api.get("/auth/api-keys").then((r) => r.data),
    create: (label) => api.post("/auth/api-keys", { label }).then((r) => r.data),
    revoke: (id) => api.delete(`/auth/api-keys/${id}`).then((r) => r.data),
  },
};

export const queries = {
  ask: (question, category) =>
    api.post("/query", { question, category }).then((r) => r.data),
  feedback: (query_id, thumbs_up, feedback_text) =>
    api.post("/query/feedback", { query_id, thumbs_up, feedback_text }).then((r) => r.data),
  history: (limit = 25) =>
    api.get("/query/history", { params: { limit } }).then((r) => r.data),
};

export const subs = {
  plans: () => api.get("/subscriptions/plans").then((r) => r.data),
  me: () => api.get("/subscriptions/me").then((r) => r.data),
  checkout: (plan_code) =>
    api.post("/subscriptions/checkout", { plan_code }).then((r) => r.data),
  cancel: () => api.post("/subscriptions/cancel").then((r) => r.data),
};

export const analytics = {
  usage: (days = 30) =>
    api.get("/analytics/usage", { params: { days } }).then((r) => r.data),
};
