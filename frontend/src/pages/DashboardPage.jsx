import { useEffect, useState } from 'react'
import { scoresApi, alertsApi } from '../api/client'
import StatCard from '../components/StatCard'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'

const PIE_COLORS = { critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#22c55e' }

export default function DashboardPage() {
  const [dist, setDist] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [running, setRunning] = useState(false)
  const [lastRun, setLastRun] = useState(null)

  useEffect(() => {
    scoresApi.getDistribution().then(r => setDist(r.data)).catch(() => {})
    alertsApi.list({ resolved: false, limit: 5 }).then(r => setAlerts(r.data)).catch(() => {})
  }, [])

  const runScoring = async () => {
    setRunning(true)
    try {
      const res = await scoresApi.runScoring()
      setLastRun(res.data)
      const distRes = await scoresApi.getDistribution()
      setDist(distRes.data)
      const alertRes = await alertsApi.list({ resolved: false, limit: 5 })
      setAlerts(alertRes.data)
    } finally {
      setRunning(false)
    }
  }

  const pieData = dist
    ? ['critical', 'high', 'medium', 'low']
        .map(t => ({ name: t.charAt(0).toUpperCase() + t.slice(1), value: dist[t] || 0 }))
        .filter(d => d.value > 0)
    : []

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Churn Risk Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">American Pharmacists Association · Member Retention</p>
        </div>
        <button
          onClick={runScoring}
          disabled={running}
          className="bg-[#1B4F8A] text-white px-5 py-2.5 rounded-lg font-semibold hover:bg-blue-800 transition disabled:opacity-60 text-sm"
        >
          {running ? '⏳ Scoring...' : '▶ Run Scoring Now'}
        </button>
      </div>

      {lastRun && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-xl p-4 text-sm text-green-800">
          ✅ Scoring complete — {lastRun.total_scored} members scored · {lastRun.alerts_created} new alerts · Model: {lastRun.model_version}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Critical Risk" value={dist?.critical ?? '—'} sublabel="Score 85–100" color="red" />
        <StatCard label="High Risk" value={dist?.high ?? '—'} sublabel="Score 70–84" color="orange" />
        <StatCard label="Medium Risk" value={dist?.medium ?? '—'} sublabel="Score 50–69" color="yellow" />
        <StatCard label="Low Risk" value={dist?.low ?? '—'} sublabel="Score 0–49" color="green" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-4">Risk Distribution</h2>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%" cy="50%"
                  outerRadius={90}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {pieData.map((d) => (
                    <Cell key={d.name} fill={PIE_COLORS[d.name.toLowerCase()]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-sm">Run scoring to see distribution.</p>
          )}
        </div>

        {/* Active Alerts */}
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-4">🔔 Recent Alerts</h2>
          {alerts.length === 0 ? (
            <p className="text-gray-400 text-sm">No active alerts. Run scoring to generate alerts.</p>
          ) : (
            <ul className="space-y-3">
              {alerts.map(a => (
                <li key={a.id} className="border-l-4 border-red-400 pl-3 py-1">
                  <div className="text-sm font-medium text-gray-800 capitalize">{a.risk_tier} risk</div>
                  <div className="text-xs text-gray-500 mt-0.5 line-clamp-2">{a.message}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
