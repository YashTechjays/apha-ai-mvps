import { useState, useEffect } from 'react'
import { analyticsApi, prospectsApi } from '../api/client'
import FunnelChart from '../components/FunnelChart'

export default function DashboardPage() {
  const [overview, setOverview] = useState(null)
  const [prospectStats, setProspectStats] = useState(null)
  const [running, setRunning] = useState(null)

  useEffect(() => {
    analyticsApi.overview().then(r => setOverview(r.data)).catch(() => {})
    prospectsApi.stats().then(r => setProspectStats(r.data)).catch(() => {})
  }, [])

  const runAction = async (action) => {
    setRunning(action)
    try {
      if (action === 'import') await prospectsApi.import()
      if (action === 'score') await prospectsApi.score()
      const [ov, ps] = await Promise.all([
        analyticsApi.overview(), prospectsApi.stats()
      ])
      setOverview(ov.data)
      setProspectStats(ps.data)
    } finally { setRunning(null) }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Outreach Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">APhA Non-Member Acquisition - AI Outreach</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => runAction('import')} disabled={!!running}
            className="bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-800 transition disabled:opacity-60">
            {running === 'import' ? 'Importing...' : 'Import NPI Data'}
          </button>
          <button onClick={() => runAction('score')} disabled={!!running}
            className="bg-[#1B4F8A] text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-800 transition disabled:opacity-60">
            {running === 'score' ? 'Scoring...' : 'Run ICP Scoring'}
          </button>
        </div>
      </div>

      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total prospects', value: overview.total_prospects, color: 'border-blue-400 bg-blue-50 text-blue-700' },
            { label: 'Emails sent', value: overview.total_emails_sent, color: 'border-green-400 bg-green-50 text-green-700' },
            { label: 'Open rate', value: `${(overview.open_rate * 100).toFixed(0)}%`, color: 'border-purple-400 bg-purple-50 text-purple-700' },
            { label: 'Conversions', value: overview.converted, color: 'border-orange-400 bg-orange-50 text-orange-700' },
          ].map(card => (
            <div key={card.label} className={`rounded-xl border-l-4 p-4 shadow-sm ${card.color}`}>
              <div className="text-3xl font-bold">{card.value}</div>
              <div className="text-sm font-semibold mt-1">{card.label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-4">Prospect funnel</h2>
          <FunnelChart data={overview} />
        </div>

        {prospectStats && (
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Prospect pool status</h2>
            <div className="space-y-3">
              {Object.entries(prospectStats.by_status || {}).map(([status, count]) => (
                <div key={status} className="flex items-center gap-3">
                  <span className="text-sm capitalize text-gray-700 w-24">{status}</span>
                  <div className="flex-1 bg-gray-100 rounded-full h-2">
                    <div className="bg-[#1B4F8A] h-2 rounded-full"
                      style={{ width: `${Math.min((count / (prospectStats.total || 1)) * 100, 100)}%` }} />
                  </div>
                  <span className="text-sm font-semibold text-gray-900 w-12 text-right">{count}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t text-sm text-gray-500">
              Avg ICP score: <span className="font-semibold text-gray-900">{prospectStats.avg_icp_score}</span>
              {' '}/{' '}
              Tier A: <span className="font-semibold text-green-700">{prospectStats.by_tier?.A || 0}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
