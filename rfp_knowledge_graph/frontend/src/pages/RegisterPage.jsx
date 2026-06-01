import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authApi } from '../api/client'

export default function RegisterPage() {
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '' })
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const submit = async (e) => {
    e.preventDefault()
    setErr('')
    if (form.password !== form.confirm) { setErr('Passwords do not match'); return }
    setLoading(true)
    try {
      const r = await authApi.register({ username: form.username, email: form.email, password: form.password })
      localStorage.setItem('token', r.data.access_token)
      localStorage.setItem('role', r.data.role)
      window.location.href = '/profile'
    } catch (e) {
      setErr(e.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-blue-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow p-10 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-[#1B4F8A] text-center mb-1">Create Account</h1>
        <p className="text-sm text-gray-500 text-center mb-6">Join APhA RFP Explorer as a pharmacist</p>
        <form onSubmit={submit} className="space-y-4">
          <input className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Username" value={form.username} onChange={e => update('username', e.target.value)} required />
          <input type="email" className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Email" value={form.email} onChange={e => update('email', e.target.value)} required />
          <input type="password" className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Password (min 8 chars)" value={form.password} onChange={e => update('password', e.target.value)} required />
          <input type="password" className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Confirm password" value={form.confirm} onChange={e => update('confirm', e.target.value)} required />
          {err && <p className="text-red-600 text-sm">{err}</p>}
          <button disabled={loading}
            className="w-full bg-[#1B4F8A] text-white py-2.5 rounded-xl font-semibold disabled:opacity-50">
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p className="text-xs text-gray-400 text-center mt-4">
          Already have an account? <Link to="/login" className="text-blue-600 hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
