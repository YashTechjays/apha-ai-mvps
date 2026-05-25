import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Layout from './components/Layout'
import DashboardPage from './pages/DashboardPage'
import CampaignsPage from './pages/CampaignsPage'
import ProspectsPage from './pages/ProspectsPage'
import { authApi } from './api/client'

function LoginPage() {
  const [u, setU] = useState('')
  const [p, setP] = useState('')
  const [err, setErr] = useState('')
  const submit = async (e) => {
    e.preventDefault()
    try {
      const r = await authApi.login(u, p)
      localStorage.setItem('outreach_token', r.data.access_token)
      window.location.href = '/'
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

function PrivateRoute({ children }) {
  return localStorage.getItem('outreach_token') ? children : <Navigate to="/login" replace />
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
                <Route path="/campaigns" element={<CampaignsPage />} />
                <Route path="/prospects" element={<ProspectsPage />} />
              </Routes>
            </Layout>
          </PrivateRoute>
        } />
      </Routes>
    </BrowserRouter>
  )
}
