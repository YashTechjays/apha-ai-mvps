import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { applicationApi } from '../api/client'

const STATUSES = ['all', 'draft', 'submitted', 'in_review', 'won', 'lost']

const STATUS_COLORS = {
  draft: 'bg-gray-100 text-gray-600',
  submitted: 'bg-blue-100 text-blue-700',
  in_review: 'bg-yellow-100 text-yellow-700',
  won: 'bg-green-100 text-green-700',
  lost: 'bg-red-100 text-red-600',
}

export default function ApplicationsPage() {
  const [apps, setApps] = useState([])
  const [tab, setTab] = useState('all')
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(null)

  const load = (status) => {
    setLoading(true)
    applicationApi.myApplications(status !== 'all' ? { status } : {})
      .then(r => setApps(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => { load(tab) }, [tab])

  const changeStatus = async (app, newStatus) => {
    setUpdating(app.id)
    try {
      const r = await applicationApi.update(app.rfp_id, app.id, { status: newStatus })
      setApps(prev => prev.map(a => a.id === app.id ? r.data : a))
    } catch { /* ignore */ } finally {
      setUpdating(null)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Applications</h1>
        <p className="text-sm text-gray-500 mt-1">Track your RFP proposal submissions</p>
      </div>

      {/* Status tabs */}
      <div className="flex gap-1 border-b">
        {STATUSES.map(s => (
          <button key={s} onClick={() => setTab(s)}
            className={`px-4 py-2 text-sm font-medium capitalize border-b-2 transition -mb-px ${
              tab === s ? 'border-[#1B4F8A] text-[#1B4F8A]' : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}>
            {s === 'in_review' ? 'In Review' : s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-gray-400 text-sm">Loading...</p>
      ) : apps.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-400 text-sm mb-3">No applications yet.</p>
          <Link to="/rfps" className="text-blue-600 text-sm hover:underline">Browse RFPs to get started</Link>
        </div>
      ) : (
        <div className="bg-white rounded-xl border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">RFP</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Organization</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Deadline</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Submitted</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {apps.map(app => (
                <tr key={app.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <Link to={`/rfps/${app.rfp_id}`} className="text-blue-600 hover:underline font-medium line-clamp-2 max-w-xs">
                      {app.rfp_title || app.rfp_id}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{app.rfp_org || '—'}</td>
                  <td className="px-4 py-3 text-gray-500">{app.rfp_deadline || '—'}</td>
                  <td className="px-4 py-3">
                    <select
                      disabled={updating === app.id}
                      value={app.status}
                      onChange={e => changeStatus(app, e.target.value)}
                      className={`text-xs font-medium px-2 py-1 rounded border-0 ring-1 ring-gray-200 cursor-pointer ${STATUS_COLORS[app.status] || ''}`}>
                      {['draft', 'submitted', 'in_review', 'won', 'lost'].map(s => (
                        <option key={s} value={s}>{s === 'in_review' ? 'In Review' : s.charAt(0).toUpperCase() + s.slice(1)}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs">
                    {app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <Link to={`/rfps/${app.rfp_id}`}
                      className="text-xs text-gray-400 hover:text-blue-600">View RFP</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
