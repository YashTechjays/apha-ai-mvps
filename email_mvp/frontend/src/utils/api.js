import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8002";
const api = axios.create({ baseURL: API_URL + "/api" });

export const getMembers = (params) => api.get("/members/", { params });
export const getMember = (id) => api.get(`/members/${id}`);
export const getBenefitSummary = (id, month) =>
  api.get(`/members/${id}/benefit-summary`, { params: { send_month: month } });

export const getEmailSends = (params) => api.get("/emails/", { params });
export const getMemberEmails = (id) => api.get(`/emails/member/${id}`);
export const previewEmail = (id, month) =>
  api.get(`/emails/preview/${id}`, { params: { send_month: month } });
export const sendSingleEmail = (id, month) =>
  api.post(`/emails/send/${id}`, null, { params: { send_month: month } });
export const runBatch = (month, dryRun) =>
  api.post("/emails/run-batch", null, { params: { send_month: month, dry_run: dryRun } });

export const getAnalyticsSummary = (month) =>
  api.get("/analytics/summary", { params: { send_month: month } });
export const getTopMembers = (month) =>
  api.get("/analytics/top-members", { params: { send_month: month } });
export const getByStatus = (month) =>
  api.get("/analytics/by-status", { params: { send_month: month } });
