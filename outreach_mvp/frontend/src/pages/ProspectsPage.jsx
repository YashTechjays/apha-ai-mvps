import { useState, useEffect } from 'react'
import { prospectsApi } from '../api/client'

const TIER_STYLES = {
  A: 'bg-green-100 text-green-800',
  B: 'bg-blue-100 text-blue-800',
  C: 'bg-gray-100 text-gray-600',
}

const STATUS_STYLES = {
  new: 'text-gray-500',
  scored: 'text-blue-600',
  queued: 'text-yellow-600',
  contacted: 'text-indigo-600',
  replied: 'text-green-600',
  converted: 'text-green-700 font-bold',
  unsubscribed: 'text-red-500',
  bounced: 'text-red-400',
}

export default function ProspectsPage() {
  const [prospects, setProspects] = useState([])
  const [filters, setFilters] = useState({ tier: '', state: '', status: '' })
  const [stats, setStats] = useState(null)

  const load = () => {
    const params = {}
    if (filters.tier) params.tier = filters.tier
    if (filters.state) params.state = filters.state
    if (filters.status) params.status = filters.status
    params.limit = 200
    prospectsApi.list(params).then(r => setProspects(r.data)).catch(() => {})
  }

  useEffect(() => {
    load()
    prospectsApi.stats().then(r => setStats(r.data)).catch(() => {})
  }, [])

  useEffect(() => { load() }, [filters])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Prospect Universe</h1>
          {stats && <p className="text-sm text-gray-500 mt-1">{stats.total} total prospects / Avg ICP: {stats.avg_icp_score}</p>}
        </div>
      </div>

      <div className="flex gap-3 mb-6">
        <select value={filters.tier} onChange={e => setFilters({...filters, tier: e.target.value})}
          className="border rounded-lg px-3 py-2 text-sm">
          <option value="">All tiers</option>
          <option value="A">Tier A (80+)</option>
          <option value="B">Tier B (60-79)</option>
          <option value="C">Tier C (&lt;60)</option>
        </select>
        <select value={filters.state} onChange={e => setFilters({...filters, state: e.target.value})}
          className="border rounded-lg px-3 py-2 text-sm">
          <option value="">All states</option>
          {['CA','TX','FL','NY','IL','PA','OH','GA','NC','MI'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={filters.status} onChange={e => setFilters({...filters, status: e.target.value})}
          className="border rounded-lg px-3 py-2 text-sm">
          <option value="">All statuses</option>
          {['new','scored','queued','contacted','replied','converted'].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 text-xs uppercase">
            <tr>
              <th className="text-left px-4 py-3">Name</th>
              <th className="text-left px-4 py-3">Email</th>
              <th className="text-left px-4 py-3">State</th>
              <th className="text-left px-4 py-3">Specialty</th>
              <th className="text-center px-4 py-3">ICP Score</th>
              <th className="text-center px-4 py-3">Tier</th>
              <th className="text-center px-4 py-3">Status</th>
              <th className="text-center px-4 py-3">Sent</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {prospects.map(p => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{p.first_name} {p.last_name}</td>
                <td className="px-4 py-3 text-gray-500">{p.email || '--'}</td>
                <td className="px-4 py-3 text-gray-600">{p.state}</td>
                <td className="px-4 py-3 text-gray-600 truncate max-w-[160px]">{p.specialty || p.practice_setting}</td>
                <td className="px-4 py-3 text-center font-semibold">{p.icp_score?.toFixed(0) || '--'}</td>
                <td className="px-4 py-3 text-center">
                  {p.icp_tier && <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${TIER_STYLES[p.icp_tier] || ''}`}>{p.icp_tier}</span>}
                </td>
                <td className={`px-4 py-3 text-center capitalize ${STATUS_STYLES[p.status] || ''}`}>{p.status}</td>
                <td className="px-4 py-3 text-center text-gray-600">{p.emails_sent}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {prospects.length === 0 && (
          <div className="text-center py-12 text-gray-400">No prospects match your filters.</div>
        )}
      </div>
    </div>
  )
}
