import { useState, useEffect } from 'react'
import { simulatorApi } from '../api/client'

function Gauge({ value, label }) {
  const color = value >= 70 ? 'text-green-600' : value >= 40 ? 'text-yellow-600' : 'text-red-500'
  return (
    <div className="flex flex-col items-center">
      <span className={`text-3xl font-bold tabular-nums ${color}`}>{value}%</span>
      <span className="text-xs text-gray-400 uppercase tracking-wide">{label}</span>
    </div>
  )
}

function FactorBars({ factors }) {
  const rows = [
    ['Category fit', factors.category],
    ['Requirements', factors.requirements],
    ['Location', factors.location],
    ['Org type', factors.org_type],
  ]
  return (
    <div className="space-y-1.5">
      {rows.map(([label, f]) => (
        <div key={label} className="flex items-center gap-2 text-xs">
          <span className="w-24 text-gray-500">{label}</span>
          <div className="flex-1 h-1.5 rounded-full bg-gray-100 overflow-hidden">
            <div className="h-full bg-sky-500" style={{ width: `${f.score}%` }} />
          </div>
          <span className="w-8 text-right tabular-nums text-gray-600">{f.score}</span>
        </div>
      ))}
    </div>
  )
}

export default function SimulatorPanel({ rfpId }) {
  const [data, setData] = useState(null)
  const [opened, setOpened] = useState(false)
  const [specialties, setSpecialties] = useState([])
  const [location, setLocation] = useState(null)
  const [sim, setSim] = useState(null)

  const load = () => {
    setOpened(true)
    simulatorApi.baseline(rfpId).then(r => {
      setData(r.data)
      setSpecialties(r.data.profile.specialties || [])
      setLocation(r.data.profile.location_state)
    }).catch(() => setData({ error: true }))
  }

  // Recompute whenever the hypothetical profile changes.
  useEffect(() => {
    if (!data || data.error) return
    simulatorApi.run(rfpId, { specialties, location_state: location })
      .then(r => setSim(r.data))
      .catch(() => {})
  }, [specialties, location, data])

  const toggleSpecialty = (cat) => {
    setSpecialties(prev => prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat])
  }

  if (!opened) {
    return (
      <button onClick={load}
        className="inline-block bg-sky-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-sky-700">
        Win-Probability Simulator
      </button>
    )
  }

  if (data?.error) return <p className="text-sm text-red-500">Simulator unavailable.</p>
  if (!data) return <p className="text-sm text-gray-400">Loading simulator...</p>

  // Surface RFP-relevant specialties first, then the rest of the palette.
  const palette = [
    ...data.rfp_categories,
    ...data.available_specialties.filter(c => !data.rfp_categories.includes(c)),
  ]
  const delta = sim?.delta ?? 0

  return (
    <div className="bg-white rounded-xl border p-6 space-y-5">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Win-Probability Simulator</h2>
        <p className="text-sm text-gray-500">
          Toggle hypothetical changes to see how your odds move. Nothing is saved.
        </p>
      </div>

      <div className="flex items-center justify-around bg-gray-50 rounded-lg py-4">
        <Gauge value={sim?.baseline.probability ?? data.baseline.probability} label="Current" />
        <div className="text-center">
          <span className={`text-sm font-semibold ${delta > 0 ? 'text-green-600' : delta < 0 ? 'text-red-500' : 'text-gray-400'}`}>
            {delta > 0 ? `+${delta}` : delta} pts
          </span>
          <div className="text-xs text-gray-300">→</div>
        </div>
        <Gauge value={sim?.simulated.probability ?? data.baseline.probability} label="Simulated" />
      </div>

      {sim && <FactorBars factors={sim.simulated.factors} />}

      <div>
        <p className="text-xs font-medium text-gray-600 mb-2">Specialties (toggle)</p>
        <div className="flex flex-wrap gap-1.5">
          {palette.map(cat => {
            const on = specialties.includes(cat)
            const relevant = data.rfp_categories.includes(cat)
            return (
              <button key={cat} onClick={() => toggleSpecialty(cat)}
                className={`px-2.5 py-1 rounded-full text-xs font-medium border transition ${
                  on ? 'bg-sky-600 text-white border-sky-600'
                     : relevant ? 'bg-sky-50 text-sky-700 border-sky-200'
                     : 'bg-white text-gray-500 border-gray-200'}`}>
                {cat}{relevant && !on ? ' +' : ''}
              </button>
            )
          })}
        </div>
      </div>

      {data.levers?.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-600 mb-2">Highest-impact moves</p>
          <div className="space-y-1">
            {data.levers.map((l, i) => (
              <div key={i} className="flex items-center justify-between text-xs border border-gray-100 rounded px-3 py-1.5">
                <span className="text-gray-600">
                  {l.type === 'specialty' ? `Add specialty: ${l.value}` : `Relocate to ${l.value}`}
                </span>
                <span className="text-green-600 font-semibold">+{l.delta} pts</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
