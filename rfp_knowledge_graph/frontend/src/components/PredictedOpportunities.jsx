import { useEffect, useState } from 'react'
import { foresightApi } from '../api/client'

function ConfidenceBar({ value }) {
  const color = value >= 70 ? 'bg-green-500' : value >= 40 ? 'bg-yellow-500' : 'bg-gray-400'
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 rounded-full bg-gray-100 overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${value}%` }} />
      </div>
      <span className="text-xs text-gray-500">{value}%</span>
    </div>
  )
}

function PredictionCard({ p }) {
  return (
    <div className="bg-white rounded-xl border border-dashed border-indigo-300 p-5">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 mr-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-indigo-500 mb-1">
            Predicted RFP
          </p>
          <h3 className="font-semibold text-gray-900 text-sm leading-snug">
            {p.organization}
            {p.category ? ` — ${p.category}` : ''}
          </h3>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          {p.fit_score != null && (
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-700">
              {p.fit_score}% fit
            </span>
          )}
          <ConfidenceBar value={p.confidence} />
        </div>
      </div>

      {p.state && <p className="text-xs text-gray-400 mb-2">{p.state}</p>}

      <div className="flex flex-wrap gap-1 mb-3">
        {p.categories?.map(cat => (
          <span key={cat} className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded text-xs">
            {cat}
          </span>
        ))}
      </div>

      <div className="text-xs text-gray-600 mb-2">{p.basis}</div>

      <div className="flex items-center justify-between text-xs text-gray-400 border-t border-gray-100 pt-2">
        <span>Expected window</span>
        <span className="font-medium text-gray-600">
          {p.predicted_window_start} → {p.predicted_window_end}
        </span>
      </div>
    </div>
  )
}

export default function PredictedOpportunities({ personalized = false }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetcher = personalized ? foresightApi.personalized : foresightApi.predictions
    fetcher({ limit: 6 })
      .then(res => setItems(res.data.items || []))
      .catch(() => setError('Could not load predictions'))
      .finally(() => setLoading(false))
  }, [personalized])

  if (loading) return null
  if (error) return null
  if (!items.length) return null

  return (
    <section className="mb-8">
      <div className="flex items-center gap-2 mb-3">
        <h2 className="text-lg font-semibold text-gray-900">Foresight — Predicted Opportunities</h2>
        <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700">
          before they post
        </span>
      </div>
      <p className="text-sm text-gray-500 mb-4">
        RFPs we expect to be posted soon, based on each organization&apos;s historical posting cadence.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((p, i) => (
          <PredictionCard key={`${p.organization}-${i}`} p={p} />
        ))}
      </div>
    </section>
  )
}
