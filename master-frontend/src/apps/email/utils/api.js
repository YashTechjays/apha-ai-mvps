import {
  emailMembersApi,
  emailSendsApi,
  emailAnalyticsApi,
} from '../../../api/client'

export const getMembers = (params) => emailMembersApi.list(params)
export const getMember = (id) => emailMembersApi.get(id)
export const getBenefitSummary = (id, month) => emailMembersApi.getBenefitSummary(id, month)

export const getEmailSends = (params) => emailSendsApi.list(params)
export const getMemberEmails = (id) => emailSendsApi.getMemberEmails(id)
export const previewEmail = (id, month) => emailSendsApi.preview(id, month)
export const sendSingleEmail = (id, month) => emailSendsApi.sendSingle(id, month)
export const runBatch = (month, dryRun) => emailSendsApi.runBatch(month, dryRun)

export const getAnalyticsSummary = (month) => emailAnalyticsApi.summary(month)
export const getTopMembers = (month) => emailAnalyticsApi.topMembers(month)
export const getByStatus = (month) => emailAnalyticsApi.byStatus(month)
