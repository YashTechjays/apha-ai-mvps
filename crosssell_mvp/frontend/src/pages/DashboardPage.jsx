import { useState, useEffect } from 'react'
import { analyticsApi, scoresApi, nudgesApi } from '../api/client'
import ConversionFunnel from '../components/ConversionFunnel'

const PRODUCTS = ['education', 'publications', 'events', 'career', 'advocacy']
const PRODUCT_LABELS = { education:'CPE', publications:'Publications', events:'Events', career:'Career', advocacy:'Advocacy' }
const PRODUCT_ICONS  = { education:'🎓', publications:'📖', events:'🎪', career:'💼', advocacy:'🏛️' }

export default function DashboardPage() {
  const [overview, setOverview] = useState(null)
  const [byProduct, setByProduct] = useState(null)
  const [running, setRunning] = useState(false)
  const [nudgeResult, setNudgeResult] = useState(null)

  useEffect(() => {
    analyticsApi.overview().then(r => setOverview(r.data)).catch(() => {})
    analyticsApi.byProduct().then(r => setByProduct(r.data)).catch(() => {})
  }, [])

  const runScoring = async () => {
    setRunning(true)
    try {
      await scoresApi.runScoring()
      const r = await analyticsApi.overview(); setOverview(r.data)
      const r2 = await analyticsApi.byProduct(); setByProduct(r2.data)
    } finally { setRunning(false) }
  }

  const sendNudges = async (dryRun) => {
    const res = await nudgesApi.send(dryRun)
    setNudgeResult({ ...res.data, dry_run: dryRun })
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cross-Sell Engine</h1>
          <p className="text-sm text-gray-500 mt-1">APhA · AI-powered product expansion</p>
        </div>
        <div className="flex gap-3">
          <button onClick={runScoring} disabled={running}
            className="bg-[#1B4F8A] text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-800 transition disabled:opacity-60">
            {running ? '⏳ Scoring...' : '▶ Run Scoring'}
          </button>
          <button onClick={() => sendNudges(true)}
            className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-50">
            Dry Run Nudges
          </button>
          <button onClick={() => sendNudges(false)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-700">
            Send Nudges ⚡
          </button>
        </div>
      </div>

      {nudgeResult && (
        <div className={`mb-6 rounded-xl p-4 text-sm ${nudgeResult.dry_run ? 'bg-yellow-50 border border-yellow-200 text-yellow-800' : 'bg-green-50 border border-green-200 text-green-800'}`}>
          {nudgeResult.dry_run ? '🔍 Dry run: ' : '✅ Sent: '}
          {nudgeResult.sent} nudges sent · {nudgeResult.skipped} skipped · {nudgeResult.failed} failed
        </div>
      )}

      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Active members', value: overview.total_active_members, color: 'border-blue-400 bg-blue-50 text-blue-700' },
            { label: 'Avg streams/member', value: overview.avg_active_streams_per_member, color: 'border-purple-400 bg-purple-50 text-purple-700' },
            { label: 'Nudges sent', value: overview.total_nudges_sent, color: 'border-green-400 bg-green-50 text-green-700' },
            { label: 'Click rate', value: `${(overview.click_rate * 100).toFixed(0)}%`, color: 'border-orange-400 bg-orange-50 text-orange-700' },
          ].map(card => (
            <div key={card.label} className={`rounded-xl border-l-4 p-4 shadow-sm ${card.color}`}>
              <div className="text-3xl font-bold">{card.value}</div>
              <div className="text-sm font-semibold mt-1">{card.label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {overview && (
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Nudge conversion funnel</h2>
            <ConversionFunnel
              total={overview.total_nudges_sent}
              opens={Math.round(overview.total_nudges_sent * overview.open_rate)}
              clicks={Math.round(overview.total_nudges_sent * overview.click_rate)}
              conversions={Math.round(overview.total_nudges_sent * overview.conversion_rate)}
            />
          </div>
        )}
        {byProduct && (
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Product stream activity</h2>
            <div className="space-y-3">
              {PRODUCTS.map(p => {
                const d = byProduct[p] || {}
                return (
                  <div key={p} className="flex items-center gap-3">
                    <span className="text-lg w-6">{PRODUCT_ICONS[p]}</span>
                    <span className="text-sm text-gray-700 w-28">{PRODUCT_LABELS[p]}</span>
                    <div className="flex-1 bg-gray-100 rounded-full h-2">
                      <div className="bg-[#1B4F8A] h-2 rounded-full"
                        style={{ width: `${((d.active_pct || 0) * 100).toFixed(0)}%` }} />
                    </div>
                    <span className="text-xs text-gray-500 w-12 text-right">
                      {((d.active_pct || 0) * 100).toFixed(0)}% active
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
