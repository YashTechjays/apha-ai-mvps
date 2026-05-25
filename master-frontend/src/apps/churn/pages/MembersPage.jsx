import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { membersApi } from '../api/client'
import RiskBadge from '../components/RiskBadge'
import ScoreBar from '../components/ScoreBar'

const RISK_FILTERS = ['all', 'critical', 'high', 'medium', 'low']

export default function MembersPage() {
  const [members, setMembers] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    const params = filter !== 'all' ? { risk_tier: filter } : {}
    membersApi.list(params).then(r => {
      setMembers(r.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [filter])

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Member Risk Table</h1>
      <p className="text-sm text-gray-500 mb-6">All active members sorted by churn risk score</p>

      <div className="flex gap-2 mb-5">
        {RISK_FILTERS.map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium capitalize transition ${
              filter === f ? 'bg-[#1B4F8A] text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-gray-400">Loading members...</p>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                {['Member', 'Tier', 'State', 'Risk Level', 'Risk Score', 'Renewal Date', 'Top Risk Factors'].map(h => (
                  <th key={h} className="text-left px-4 py-3 font-semibold text-gray-600 text-xs uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y">
              {members.map(m => (
                <tr
                  key={m.id}
                  onClick={() => navigate(`/churn/members/${m.id}`)}
                  className="hover:bg-blue-50 cursor-pointer transition"
                >
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{m.first_name} {m.last_name}</div>
                    <div className="text-xs text-gray-400">{m.email}</div>
                  </td>
                  <td className="px-4 py-3 capitalize text-gray-600">{m.tier?.replace('_', ' ')}</td>
                  <td className="px-4 py-3 text-gray-600">{m.state}</td>
                  <td className="px-4 py-3"><RiskBadge tier={m.risk_tier} /></td>
                  <td className="px-4 py-3 w-36"><ScoreBar score={m.churn_score} /></td>
                  <td className="px-4 py-3 text-gray-600 text-xs">
                    {m.renewal_date ? new Date(m.renewal_date).toLocaleDateString() : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {(m.top_risk_factors || []).slice(0, 2).map(f => (
                        <span key={f} className="bg-red-50 text-red-700 text-xs px-2 py-0.5 rounded-full">
                          {f.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {members.length === 0 && (
            <div className="text-center py-12 text-gray-400">No members found for this filter.</div>
          )}
        </div>
      )}
    </div>
  )
}
