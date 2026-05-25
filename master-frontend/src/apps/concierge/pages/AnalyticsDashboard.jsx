import { useEffect, useState } from 'react'
import { analyticsApi } from '../api/client'

export default function AnalyticsDashboard() {
  const [data, setData] = useState(null)

  useEffect(() => {
    analyticsApi.getSummary().then(r => setData(r.data)).catch(() => {})
  }, [])

  if (!data) return <div className="p-8 text-gray-400">Loading analytics...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Concierge Analytics</h1>
      <p className="text-sm text-gray-500 mb-8">AI Membership Concierge · APhA</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Conversations', value: data.total_conversations,                         color: 'border-blue-400 bg-blue-50 text-blue-700' },
          { label: 'Leads Captured',       value: data.leads_captured,                             color: 'border-green-400 bg-green-50 text-green-700' },
          { label: 'Lead Capture Rate',    value: `${(data.lead_capture_rate * 100).toFixed(0)}%`, color: 'border-purple-400 bg-purple-50 text-purple-700' },
          { label: 'Avg Turns / Conv.',    value: data.avg_turns_per_conversation,                 color: 'border-orange-400 bg-orange-50 text-orange-700' },
        ].map(card => (
          <div key={card.label} className={`rounded-xl border-l-4 p-4 shadow-sm ${card.color}`}>
            <div className="text-3xl font-bold">{card.value}</div>
            <div className="text-sm font-semibold mt-1">{card.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-4">Intent Breakdown</h2>
          {Object.entries(data.intent_breakdown || {}).map(([intent, count]) => (
            <div key={intent} className="flex items-center gap-3 mb-2">
              <div className="capitalize text-sm text-gray-700 w-28">{intent.replace('_', ' ')}</div>
              <div className="flex-1 bg-gray-100 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${Math.min((count / Math.max(data.total_conversations, 1)) * 100, 100)}%` }}
                />
              </div>
              <div className="text-sm font-semibold text-gray-900 w-8 text-right">{count}</div>
            </div>
          ))}
          {Object.keys(data.intent_breakdown || {}).length === 0 && (
            <p className="text-gray-400 text-sm">No data yet.</p>
          )}
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-4">Tier Recommendations</h2>
          {Object.entries(data.tier_recommendations || {}).map(([tier, count]) => (
            <div key={tier} className="flex items-center gap-3 mb-2">
              <div className="capitalize text-sm text-gray-700 w-28">{tier.replace('_', ' ')}</div>
              <div className="flex-1 bg-gray-100 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${Math.min((count / Math.max(data.total_conversations, 1)) * 100, 100)}%` }}
                />
              </div>
              <div className="text-sm font-semibold text-gray-900 w-8 text-right">{count}</div>
            </div>
          ))}
          {Object.keys(data.tier_recommendations || {}).length === 0 && (
            <p className="text-gray-400 text-sm">No tier recommendations yet.</p>
          )}
        </div>
      </div>
    </div>
  )
}
