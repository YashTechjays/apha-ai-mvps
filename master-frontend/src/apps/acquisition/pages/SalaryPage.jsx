import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { acqSalaryApi, acqLeadApi } from '../../../api/client'
import { useSession } from '../hooks/useSession'
import APhAHeader from '../components/shared/APhAHeader'
import LeadModal from '../components/shared/LeadModal'
import MemberUpsell from '../components/shared/MemberUpsell'
import UsageMeter from '../components/shared/UsageMeter'

const STATES = [
  'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA',
  'KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
  'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT',
  'VA','WA','WV','WI','WY','DC',
]

const LICENSE_TYPES = [
  { value: 'pharmacist', label: 'Pharmacist (RPh/PharmD)' },
  { value: 'new_practitioner', label: 'New Practitioner (0-3yrs)' },
  { value: 'technician', label: 'Pharmacy Technician' },
  { value: 'researcher', label: 'Researcher/Scientist' },
]

const EXP_RANGES = ['0-2', '3-5', '6-10', '11-15', '16-20', '20+']

export default function SalaryPage() {
  const sessionId = useSession()
  const [form, setForm] = useState({
    state: 'TX',
    specialty: 'Hospital/Health-System',
    license_type: 'pharmacist',
    years_experience: '6-10',
    current_salary: '',
  })
  const [specialties, setSpecialties] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [usageInfo, setUsageInfo] = useState({ used: 0, limit: 3 })
  const [leadCaptured, setLeadCaptured] = useState(false)

  useEffect(() => {
    acqSalaryApi
      .getSpecialties()
      .then((r) => setSpecialties(r.data))
      .catch(() => {})
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await acqSalaryApi.benchmark({
        ...form,
        session_id: sessionId,
        current_salary: form.current_salary ? parseFloat(form.current_salary) : null,
      })
      setResult(res.data)
      setUsageInfo({ used: 3 - res.data.remaining_free_checks, limit: 3 })
    } catch (err) {
      if (err.response?.status === 429)
        setError('Daily limit reached. Join APhA for unlimited access.')
      else setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleLeadCapture = async (email, name) => {
    await acqLeadApi.capture({
      session_id: sessionId,
      email,
      name,
      source_tool: 'salary',
      usage_id: result?.usage_id,
      state: form.state,
      specialty: form.specialty,
      salary_percentile: result?.percentile,
      salary_gap_usd: result?.gap_to_75th,
    })
    setLeadCaptured(true)
    setShowModal(false)
  }

  const chartData = result
    ? [
        { label: '25th', value: result.p25, fill: '#e5e7eb' },
        { label: '50th (median)', value: result.p50, fill: '#93c5fd' },
        { label: '75th', value: result.p75, fill: '#3b82f6' },
        { label: '90th', value: result.p90, fill: '#1d4ed8' },
        { label: 'Member avg', value: result.member_premium_salary, fill: '#15803d' },
      ]
    : []

  return (
    <div className="min-h-screen bg-gray-50 font-body">
      <APhAHeader activeTool="salary" />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="font-display text-3xl font-bold text-gray-900 mb-2">
            Pharmacist Salary Benchmarker
          </h1>
          <p className="text-gray-500 text-sm max-w-lg mx-auto">
            See where your salary stands vs. peers in your state and specialty. Powered by
            APhA salary survey data.
          </p>
        </div>

        <UsageMeter used={usageInfo.used} limit={usageInfo.limit} />

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mt-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  State *
                </label>
                <select
                  value={form.state}
                  onChange={(e) => setForm({ ...form, state: e.target.value })}
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue"
                >
                  {STATES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  License type *
                </label>
                <select
                  value={form.license_type}
                  onChange={(e) => setForm({ ...form, license_type: e.target.value })}
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue"
                >
                  {LICENSE_TYPES.map((l) => (
                    <option key={l.value} value={l.value}>
                      {l.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                Specialty *
              </label>
              <select
                value={form.specialty}
                onChange={(e) => setForm({ ...form, specialty: e.target.value })}
                className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue"
              >
                {specialties.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Years of experience
                </label>
                <select
                  value={form.years_experience}
                  onChange={(e) => setForm({ ...form, years_experience: e.target.value })}
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue"
                >
                  {EXP_RANGES.map((r) => (
                    <option key={r} value={r}>
                      {r} years
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Current salary (optional)
                </label>
                <input
                  type="number"
                  placeholder="e.g. 125000"
                  value={form.current_salary}
                  onChange={(e) => setForm({ ...form, current_salary: e.target.value })}
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue"
                />
              </div>
            </div>
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700">
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-apha-blue text-white py-3.5 rounded-xl font-semibold hover:bg-apha-dark transition disabled:opacity-50"
            >
              {loading ? 'Calculating...' : 'Benchmark my salary'}
            </button>
          </form>
        </div>

        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6"
            >
              <div className="bg-apha-blue text-white rounded-2xl p-5 mb-4">
                <div className="text-xs text-blue-200 mb-1">AI Insight</div>
                <div className="font-semibold text-base">{result.headline}</div>
                {result.percentile && (
                  <div className="text-blue-100 text-sm mt-1">
                    You are at the{' '}
                    <span className="font-bold text-white">{result.percentile}th percentile</span>{' '}
                    for {result.specialty} in {result.state_name}
                  </div>
                )}
              </div>

              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
                <h3 className="font-semibold text-gray-800 mb-4">
                  Salary distribution &mdash; {result.state_name}
                </h3>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
                    <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                    <YAxis
                      tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                      tick={{ fontSize: 11 }}
                    />
                    <Tooltip formatter={(v) => `$${v.toLocaleString()}`} />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                      {chartData.map((d, i) => (
                        <Cell key={i} fill={d.fill} />
                      ))}
                    </Bar>
                    {form.current_salary && (
                      <ReferenceLine
                        y={parseFloat(form.current_salary)}
                        stroke="#ef4444"
                        strokeDasharray="5 5"
                        label={{ value: 'You', fill: '#ef4444', fontSize: 11 }}
                      />
                    )}
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4 relative">
                <h3 className="font-semibold text-gray-800 mb-3">Your personalized analysis</h3>
                {leadCaptured ? (
                  <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                    {result.commentary}
                  </p>
                ) : (
                  <div className="relative">
                    <p className="text-sm text-gray-400 leading-relaxed line-clamp-3 blur-sm select-none">
                      {result.commentary}
                    </p>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <button
                        onClick={() => setShowModal(true)}
                        className="bg-apha-blue text-white px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-apha-dark transition shadow-lg"
                      >
                        Unlock full analysis (free)
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <MemberUpsell tool="salary" />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <LeadModal
        isOpen={showModal}
        tool="salary"
        onSubmit={handleLeadCapture}
        onClose={() => setShowModal(false)}
      />
    </div>
  )
}
