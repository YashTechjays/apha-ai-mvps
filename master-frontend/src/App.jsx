import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import MasterLayout from './components/MasterLayout'

// ── Churn Prediction ────────────────────────────────────────────
import ChurnLayout from './apps/churn/components/Layout'
import ChurnLoginPage from './apps/churn/pages/LoginPage'
import ChurnDashboardPage from './apps/churn/pages/DashboardPage'
import ChurnMembersPage from './apps/churn/pages/MembersPage'
import ChurnMemberDetailPage from './apps/churn/pages/MemberDetailPage'

// ── Concierge ───────────────────────────────────────────────────
import ConciergeDemoPage from './apps/concierge/pages/DemoPage'
import ConciergeAnalytics from './apps/concierge/pages/AnalyticsDashboard'

// ── CPE Calculator ──────────────────────────────────────────────
import CpeCalculatorPage from './apps/cpe/pages/CalculatorPage'

// ── Cross-Sell ──────────────────────────────────────────────────
import CrossSellDashboard from './apps/crosssell/pages/DashboardPage'
import CrossSellMembers from './apps/crosssell/pages/MembersPage'
import CrossSellMemberDetail from './apps/crosssell/pages/MemberDetailPage'
import CrossSellNudges from './apps/crosssell/pages/NudgesPage'

// ── Drug Reference ──────────────────────────────────────────────
import DrugRefLanding from './apps/drug_ref/pages/LandingPage'
import DrugRefPricing from './apps/drug_ref/pages/PricingPage'
import DrugRefLogin from './apps/drug_ref/pages/LoginPage'
import DrugRefSignup from './apps/drug_ref/pages/SignupPage'
import DrugRefQuery from './apps/drug_ref/pages/QueryPage'
import DrugRefDashboard from './apps/drug_ref/pages/DashboardPage'

// ── Acquisition Funnels ─────────────────────────────────────────
import AcqHomePage from './apps/acquisition/pages/HomePage'
import AcqSalaryPage from './apps/acquisition/pages/SalaryPage'
import AcqInteractionPage from './apps/acquisition/pages/InteractionPage'
import AcqCareerPage from './apps/acquisition/pages/CareerPage'

// ── Email MVP ───────────────────────────────────────────────────
import EmailLayout from './apps/email/components/Layout'
import EmailDashboard from './apps/email/pages/DashboardPage'
import EmailMembers from './apps/email/pages/MembersPage'
import EmailMemberDetail from './apps/email/pages/MemberDetailPage'
import EmailSends from './apps/email/pages/EmailSendsPage'
import EmailAnalytics from './apps/email/pages/AnalyticsPage'

// ── Outreach Automation ────────────────────────────────────────
import OutreachLayout from './apps/outreach/components/Layout'
import OutreachDashboard from './apps/outreach/pages/DashboardPage'
import OutreachProspects from './apps/outreach/pages/ProspectsPage'
import OutreachCampaigns from './apps/outreach/pages/CampaignsPage'

// ── Auth helpers ────────────────────────────────────────────────
function ChurnPrivateRoute({ children }) {
  return localStorage.getItem('churn_token') ? children : <Navigate to="/churn/login" replace />
}

function CrossSellPrivateRoute({ children }) {
  return localStorage.getItem('crosssell_token') ? children : <Navigate to="/crosssell/login" replace />
}

function OutreachPrivateRoute({ children }) {
  return localStorage.getItem('outreach_token') ? children : <Navigate to="/outreach/login" replace />
}

// CrossSell inline login (was in App.jsx of crosssell)
import { useState } from 'react'
import { crosssellAuthApi, outreachAuthApi } from './api/client'

function CrossSellLoginPage() {
  const [u, setU] = useState('')
  const [p, setP] = useState('')
  const [err, setErr] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    try {
      const r = await crosssellAuthApi.login(u, p)
      localStorage.setItem('crosssell_token', r.data.access_token)
      window.location.href = '/crosssell'
    } catch {
      setErr('Invalid credentials')
    }
  }

  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow p-10 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-[#1B4F8A] text-center mb-6">APhA Cross-Sell</h1>
        <form onSubmit={submit} className="space-y-4">
          <input className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Username" value={u} onChange={e => setU(e.target.value)} required />
          <input type="password" className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Password" value={p} onChange={e => setP(e.target.value)} required />
          {err && <p className="text-red-600 text-sm">{err}</p>}
          <button className="w-full bg-[#1B4F8A] text-white py-2.5 rounded-xl font-semibold">Sign In</button>
        </form>
        <p className="text-xs text-gray-400 text-center mt-4">Demo: admin / apha2026</p>
      </div>
    </div>
  )
}

// CrossSell layout with sidebar
import { NavLink } from 'react-router-dom'

function CrossSellLayout({ children }) {
  const NAV = [
    { path: '/crosssell', label: 'Dashboard', end: true },
    { path: '/crosssell/members', label: 'Members' },
    { path: '/crosssell/nudges', label: 'Nudges' },
  ]
  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-56 bg-[#1B4F8A] text-white flex flex-col">
        <div className="p-5 border-b border-blue-700">
          <div className="text-xs font-semibold text-blue-300 uppercase tracking-widest mb-1">APhA</div>
          <div className="font-bold text-lg">Cross-Sell Engine</div>
          <div className="text-xs text-blue-300 mt-0.5">by Techjays</div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map(({ path, label, end }) => (
            <NavLink key={path} to={path} end={end}
              className={({ isActive }) =>
                `flex items-center px-3 py-2 rounded-lg text-sm transition ${isActive ? 'bg-blue-700 font-semibold' : 'hover:bg-blue-700/60'}`
              }>{label}</NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-blue-700">
          <button onClick={() => { localStorage.removeItem('crosssell_token'); window.location.href = '/crosssell/login' }}
            className="text-xs text-blue-300 hover:text-white">Logout</button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-8">{children}</main>
    </div>
  )
}

function OutreachLoginPage() {
  const [u, setU] = useState('')
  const [p, setP] = useState('')
  const [err, setErr] = useState('')
  const submit = async (e) => {
    e.preventDefault()
    try {
      const r = await outreachAuthApi.login(u, p)
      localStorage.setItem('outreach_token', r.data.access_token)
      window.location.href = '/outreach'
    } catch {
      setErr('Invalid credentials')
    }
  }
  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow p-10 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-[#1B4F8A] text-center mb-2">APhA Outreach</h1>
        <p className="text-sm text-gray-400 text-center mb-6">AI-Powered Acquisition</p>
        <form onSubmit={submit} className="space-y-4">
          <input className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Username" value={u} onChange={e => setU(e.target.value)} required />
          <input type="password" className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Password" value={p} onChange={e => setP(e.target.value)} required />
          {err && <p className="text-red-600 text-sm">{err}</p>}
          <button className="w-full bg-[#1B4F8A] text-white py-2.5 rounded-xl font-semibold">Sign In</button>
        </form>
        <p className="text-xs text-gray-400 text-center mt-4">Demo: admin / apha2026</p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <MasterLayout>
        <Routes>
          {/* Home */}
          <Route path="/" element={null} />

          {/* ── Churn Prediction ─────────────────────────── */}
          <Route path="/churn/login" element={<ChurnLoginPage />} />
          <Route path="/churn" element={
            <ChurnPrivateRoute>
              <ChurnLayout><ChurnDashboardPage /></ChurnLayout>
            </ChurnPrivateRoute>
          } />
          <Route path="/churn/members" element={
            <ChurnPrivateRoute>
              <ChurnLayout><ChurnMembersPage /></ChurnLayout>
            </ChurnPrivateRoute>
          } />
          <Route path="/churn/members/:id" element={
            <ChurnPrivateRoute>
              <ChurnLayout><ChurnMemberDetailPage /></ChurnLayout>
            </ChurnPrivateRoute>
          } />

          {/* ── Concierge ────────────────────────────────── */}
          <Route path="/concierge" element={<ConciergeDemoPage />} />
          <Route path="/concierge/analytics" element={<ConciergeAnalytics />} />

          {/* ── CPE Calculator ───────────────────────────── */}
          <Route path="/cpe" element={<CpeCalculatorPage />} />
          <Route path="/cpe/state/:stateCode" element={<CpeCalculatorPage />} />

          {/* ── Cross-Sell ───────────────────────────────── */}
          <Route path="/crosssell/login" element={<CrossSellLoginPage />} />
          <Route path="/crosssell" element={
            <CrossSellPrivateRoute>
              <CrossSellLayout><CrossSellDashboard /></CrossSellLayout>
            </CrossSellPrivateRoute>
          } />
          <Route path="/crosssell/members" element={
            <CrossSellPrivateRoute>
              <CrossSellLayout><CrossSellMembers /></CrossSellLayout>
            </CrossSellPrivateRoute>
          } />
          <Route path="/crosssell/members/:id" element={
            <CrossSellPrivateRoute>
              <CrossSellLayout><CrossSellMemberDetail /></CrossSellLayout>
            </CrossSellPrivateRoute>
          } />
          <Route path="/crosssell/nudges" element={
            <CrossSellPrivateRoute>
              <CrossSellLayout><CrossSellNudges /></CrossSellLayout>
            </CrossSellPrivateRoute>
          } />

          {/* ── Drug Reference ──────────────────────────── */}
          <Route path="/drug-ref" element={<DrugRefLanding />} />
          <Route path="/drug-ref/pricing" element={<DrugRefPricing />} />
          <Route path="/drug-ref/login" element={<DrugRefLogin />} />
          <Route path="/drug-ref/signup" element={<DrugRefSignup />} />
          <Route path="/drug-ref/query" element={<DrugRefQuery />} />
          <Route path="/drug-ref/dashboard" element={<DrugRefDashboard />} />

          {/* ── Acquisition Funnels ────────────────────── */}
          <Route path="/acquisition" element={<AcqHomePage />} />
          <Route path="/acquisition/salary" element={<AcqSalaryPage />} />
          <Route path="/acquisition/interactions" element={<AcqInteractionPage />} />
          <Route path="/acquisition/career" element={<AcqCareerPage />} />

          {/* ── Outreach Automation ────────────────────── */}
          <Route path="/outreach/login" element={<OutreachLoginPage />} />
          <Route path="/outreach" element={
            <OutreachPrivateRoute>
              <OutreachLayout><OutreachDashboard /></OutreachLayout>
            </OutreachPrivateRoute>
          } />
          <Route path="/outreach/prospects" element={
            <OutreachPrivateRoute>
              <OutreachLayout><OutreachProspects /></OutreachLayout>
            </OutreachPrivateRoute>
          } />
          <Route path="/outreach/campaigns" element={
            <OutreachPrivateRoute>
              <OutreachLayout><OutreachCampaigns /></OutreachLayout>
            </OutreachPrivateRoute>
          } />

          {/* ── Email MVP ───────────────────────────────── */}
          <Route path="/email" element={<EmailLayout><EmailDashboard /></EmailLayout>} />
          <Route path="/email/members" element={<EmailLayout><EmailMembers /></EmailLayout>} />
          <Route path="/email/members/:id" element={<EmailLayout><EmailMemberDetail /></EmailLayout>} />
          <Route path="/email/emails" element={<EmailLayout><EmailSends /></EmailLayout>} />
          <Route path="/email/analytics" element={<EmailLayout><EmailAnalytics /></EmailLayout>} />
        </Routes>
      </MasterLayout>
    </BrowserRouter>
  )
}
