import { useState } from 'react'
import { coalitionApi } from '../api/client'

function CoverageBar({ pct }) {
  const color = pct >= 80 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-400'
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-32 rounded-full bg-gray-100 overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-semibold tabular-nums">{pct}% covered</span>
    </div>
  )
}

export default function CoalitionPanel({ rfpId }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [opened, setOpened] = useState(false)

  const load = () => {
    setOpened(true)
    setLoading(true)
    coalitionApi.get(rfpId)
      .then(r => setData(r.data))
      .catch(() => setData({ error: true }))
      .finally(() => setLoading(false))
  }

  if (!opened) {
    return (
      <button onClick={load}
        className="inline-block bg-violet-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-violet-700">
        Find a Coalition
      </button>
    )
  }

  return (
    <div className="bg-white rounded-xl border p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Coalition Finder</h2>
        {data && !data.error && <CoverageBar pct={data.coverage_pct} />}
      </div>
      <p className="text-sm text-gray-500">
        A complementary team of pharmacists whose specialties collectively cover this RFP&apos;s requirements.
      </p>

      {loading && <p className="text-sm text-gray-400">Assembling the best team...</p>}
      {data?.error && <p className="text-sm text-red-500">Could not assemble a coalition.</p>}

      {data && !data.error && (
        <>
          <div className="space-y-3">
            {data.team.map(m => (
              <div key={m.user_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-gray-900 text-sm">{m.full_name}</span>
                  {m.location_state && (
                    <span className="text-xs text-gray-400">{m.location_state}</span>
                  )}
                </div>
                <div className="flex flex-wrap gap-1 mb-2">
                  {m.covers.map(c => (
                    <span key={c} className="px-2 py-0.5 bg-violet-50 text-violet-700 rounded text-xs">
                      {c}
                    </span>
                  ))}
                </div>
                {m.certifications?.length > 0 && (
                  <p className="text-xs text-gray-400">{m.certifications.join(' · ')}</p>
                )}
              </div>
            ))}
            {data.team.length === 0 && (
              <p className="text-sm text-gray-400">No matching pharmacists available.</p>
            )}
          </div>

          {data.uncovered_categories?.length > 0 && (
            <div className="text-xs text-gray-500">
              <span className="font-medium text-amber-600">Still uncovered: </span>
              {data.uncovered_categories.join(', ')}
            </div>
          )}
        </>
      )}
    </div>
  )
}
