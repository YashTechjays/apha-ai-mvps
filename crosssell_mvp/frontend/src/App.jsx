import { BrowserRouter, Routes, Route, Navigate, NavLink } from 'react-router-dom'
import { useState } from 'react'
import { authApi } from './api/client'
import DashboardPage from './pages/DashboardPage'
import MembersPage from './pages/MembersPage'
import MemberDetailPage from './pages/MemberDetailPage'
import NudgesPage from './pages/NudgesPage'

const NAV = [
  { path: '/', label: '📊 Dashboard', end: true },
  { path: '/members', label: '👥 Members' },
  { path: '/nudges', label: '📬 Nudges' },
]

function Layout({ children }) {
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
              }>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-blue-700">
          <button onClick={() => { localStorage.removeItem('token'); window.location.href = '/login' }}
            className="text-xs text-blue-300 hover:text-white">← Log out</button>
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
      window.location.href = '/'
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

function PrivateRoute({ children }) {
  return localStorage.getItem('token') ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={
          <PrivateRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/members" element={<MembersPage />} />
                <Route path="/members/:id" element={<MemberDetailPage />} />
                <Route path="/nudges" element={<NudgesPage />} />
              </Routes>
            </Layout>
          </PrivateRoute>
        } />
      </Routes>
    </BrowserRouter>
  )
}
