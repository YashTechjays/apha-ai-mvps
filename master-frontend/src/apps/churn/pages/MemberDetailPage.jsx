import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { membersApi, scoresApi, alertsApi } from '../api/client'
import RiskBadge from '../components/RiskBadge'
import ScoreBar from '../components/ScoreBar'
import ShapExplainer from '../components/ShapExplainer'

export default function MemberDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [member, setMember] = useState(null)
  const [explanation, setExplanation] = useState(null)
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    membersApi.get(id).then(r => setMember(r.data)).catch(() => {})
    scoresApi.getExplanation(id).then(r => setExplanation(r.data)).catch(() => {})
    alertsApi.list({ resolved: false }).then(r =>
      setAlerts(r.data.filter(a => a.member_id === id))
    ).catch(() => {})
  }, [id])

  if (!member) return <div className="text-gray-400 p-8">Loading...</div>

  const resolveAlert = async (alertId) => {
    await alertsApi.update(alertId, { is_resolved: true, outcome: 'retained' })
    setAlerts(prev => prev.filter(a => a.id !== alertId))
  }

  return (
    <div>
      <button
        onClick={() => navigate('/members')}
        className="text-sm text-blue-600 hover:underline mb-6 flex items-center gap-1"
      >
        ← Back to Members
      </button>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: Member Info */}
        <div className="md:col-span-1 space-y-4">
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <div className="text-xl font-bold text-gray-900">{member.first_name} {member.last_name}</div>
            <div className="text-sm text-gray-500 mt-1">{member.email}</div>
            <div className="mt-4 space-y-2 text-sm">
              {[
                ['Tier', member.tier?.replace('_', ' ')],
                ['State', member.state],
                ['Specialty', member.specialty],
                ['Member since', `${member.years_as_member?.toFixed(1)} years`],
                ['Renewals', member.renewal_count],
                ['Renewal date', member.renewal_date ? new Date(member.renewal_date).toLocaleDateString() : '—'],
              ].map(([label, value]) => (
                <div key={label}>
                  <span className="text-gray-500">{label}:</span>{' '}
                  <span className="font-medium capitalize">{value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm p-6">
            <div className="font-semibold text-gray-700 mb-3">Churn Risk Score</div>
            <div className="mb-3"><RiskBadge tier={member.risk_tier} /></div>
            <ScoreBar score={member.churn_score} />
            {member.top_risk_factors?.length > 0 && (
              <div className="mt-4">
                <div className="text-xs font-semibold text-gray-500 mb-2 uppercase">Top Risk Factors</div>
                <ul className="space-y-1">
                  {member.top_risk_factors.map(f => (
                    <li key={f} className="text-xs bg-red-50 text-red-700 px-2 py-1 rounded">
                      {f.replace(/_/g, ' ')}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Right: Explanation + Alerts */}
        <div className="md:col-span-2 space-y-4">
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Why is this member at risk?</h2>
            {explanation?.factors?.length > 0 ? (
              <ShapExplainer factors={explanation.factors} />
            ) : (
              <p className="text-gray-400 text-sm">Run scoring to generate explanation.</p>
            )}
          </div>

          {alerts.length > 0 && (
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <h2 className="font-semibold text-gray-800 mb-4">🔔 Active Alerts</h2>
              <div className="space-y-3">
                {alerts.map(a => (
                  <div key={a.id} className="border border-red-200 bg-red-50 rounded-xl p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <RiskBadge tier={a.risk_tier} />
                        <p className="text-sm text-gray-700 mt-2">{a.message}</p>
                      </div>
                      <button
                        onClick={() => resolveAlert(a.id)}
                        className="shrink-0 text-xs bg-green-600 text-white px-3 py-1.5 rounded-lg hover:bg-green-700"
                      >
                        Mark Retained
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Engagement Snapshot</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              {[
                ['Days since last login', member.days_since_last_login?.toFixed(0)],
                ['CPE hours (last 90 days)', member.cpe_hours_last_90d?.toFixed(1)],
                ['Email open rate (30d)', `${((member.email_open_rate_30d || 0) * 100).toFixed(0)}%`],
                ['Events attended (YTD)', member.events_attended_ytd],
                ['Publications read (30d)', member.publications_read_30d],
                ['Community posts (90d)', member.community_posts_90d],
              ].map(([label, value]) => (
                <div key={label} className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-500">{label}</div>
                  <div className="font-semibold text-gray-900 mt-1">{value ?? '—'}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
