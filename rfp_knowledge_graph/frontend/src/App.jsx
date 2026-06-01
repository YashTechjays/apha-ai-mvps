import { BrowserRouter, Routes, Route, Navigate, NavLink } from 'react-router-dom'
import { useState } from 'react'
import { authApi } from './api/client'
import DashboardPage from './pages/DashboardPage'
import RfpListPage from './pages/RfpListPage'
import RfpDetailPage from './pages/RfpDetailPage'
import CrawlPage from './pages/CrawlPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import ApplicationsPage from './pages/ApplicationsPage'
import CopilotPage from './pages/CopilotPage'

const ADMIN_NAV = [
  { path: '/', label: 'Dashboard', end: true },
  { path: '/rfps', label: 'RFP Explorer' },
  { path: '/crawl', label: 'Crawl Manager' },
]

const PHARMACIST_NAV = [
  { path: '/', label: 'Dashboard', end: true },
  { path: '/rfps', label: 'RFP Explorer' },
  { path: '/copilot', label: 'Copilot' },
  { path: '/applications', label: 'My Applications' },
  { path: '/profile', label: 'My Profile' },
]

function getRole() {
  return localStorage.getItem('role') || 'admin'
}

function Layout({ children }) {
  const role = getRole()
  const nav = role === 'pharmacist' ? PHARMACIST_NAV : ADMIN_NAV

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-56 bg-[#1B4F8A] text-white flex flex-col">
        <div className="p-5 border-b border-blue-700">
          <div className="text-xs font-semibold text-blue-300 uppercase tracking-widest mb-1">APhA</div>
          <div className="font-bold text-lg">RFP Knowledge Graph</div>
          <div className="text-xs text-blue-300 mt-0.5">Firecrawl + Neo4j</div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {nav.map(({ path, label, end }) => (
            <NavLink key={path} to={path} end={end}
              className={({ isActive }) =>
                `flex items-center px-3 py-2 rounded-lg text-sm transition ${isActive ? 'bg-blue-700 font-semibold' : 'hover:bg-blue-700/60'}`
              }>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-blue-700">
          <button onClick={() => {
            localStorage.removeItem('token')
            localStorage.removeItem('role')
            window.location.href = '/login'
          }} className="text-xs text-blue-300 hover:text-white">Log out</button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-8">{children}</main>
    </div>
  )
}

function LoginPage() {
  const [u, setU] = useState('')
  const [p, setP] = useState('')
  const [err, setErr] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    try {
      const r = await authApi.login(u, p)
      localStorage.setItem('token', r.data.access_token)
      localStorage.setItem('role', r.data.role || 'admin')
      window.location.href = '/'
    } catch {
      setErr('Invalid credentials')
    }
  }

  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow p-10 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-[#1B4F8A] text-center mb-2">APhA RFP Explorer</h1>
        <p className="text-sm text-gray-500 text-center mb-6">Knowledge Graph powered by Firecrawl + Neo4j</p>
        <form onSubmit={submit} className="space-y-4">
          <input className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Username" value={u} onChange={e => setU(e.target.value)} required />
          <input type="password" className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Password" value={p} onChange={e => setP(e.target.value)} required />
          {err && <p className="text-red-600 text-sm">{err}</p>}
          <button className="w-full bg-[#1B4F8A] text-white py-2.5 rounded-xl font-semibold">Sign In</button>
        </form>
        <p className="text-xs text-gray-400 text-center mt-4">Demo: admin / apha2026</p>
        <p className="text-xs text-gray-400 text-center mt-1">
          Pharmacist? <NavLink to="/register" className="text-blue-600 hover:underline">Create account</NavLink>
        </p>
      </div>
    </div>
  )
}

function PrivateRoute({ children }) {
  return localStorage.getItem('token') ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/*" element={
          <PrivateRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/rfps" element={<RfpListPage />} />
                <Route path="/rfps/:id" element={<RfpDetailPage />} />
                <Route path="/crawl" element={<CrawlPage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/copilot" element={<CopilotPage />} />
                <Route path="/applications" element={<ApplicationsPage />} />
              </Routes>
            </Layout>
          </PrivateRoute>
        } />
      </Routes>
    </BrowserRouter>
  )
}
