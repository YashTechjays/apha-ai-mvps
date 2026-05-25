import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { interactionApi, leadApi } from '../api/client'
import { useSession } from '../hooks/useSession'
import APhAHeader from '../components/shared/APhAHeader'
import LeadModal from '../components/shared/LeadModal'
import MemberUpsell from '../components/shared/MemberUpsell'
import UsageMeter from '../components/shared/UsageMeter'

const SEVERITY_STYLES = {
  major: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300', label: 'MAJOR' },
  moderate: { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-300', label: 'MODERATE' },
  minor: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300', label: 'MINOR' },
  unknown: { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-300', label: 'UNKNOWN' },
}

function DrugSearchBox({ label, value, onChange, onSelect }) {
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  const handleChange = useCallback(
    async (e) => {
      const val = e.target.value
      onChange(val)
      if (val.length >= 2) {
        try {
          const res = await interactionApi.search(val)
          setSuggestions(res.data)
          setShowSuggestions(true)
        } catch {
          setSuggestions([])
        }
      } else {
        setSuggestions([])
        setShowSuggestions(false)
      }
    },
    [onChange]
  )

  return (
    <div className="relative">
      <label className="block text-sm font-semibold text-gray-700 mb-1.5">{label}</label>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
        placeholder="Type drug name..."
        className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue"
      />
      {showSuggestions && suggestions.length > 0 && (
        <ul className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg max-h-48 overflow-y-auto">
          {suggestions.map((drug) => (
            <li
              key={drug.id}
              className="px-4 py-2 text-sm hover:bg-blue-50 cursor-pointer"
              onMouseDown={() => {
                onSelect(drug.name)
                setShowSuggestions(false)
              }}
            >
              {drug.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function SeverityBadge({ severity }) {
  const style = SEVERITY_STYLES[severity] || SEVERITY_STYLES.unknown
  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${style.bg} ${style.text} border ${style.border}`}
    >
      {style.label}
    </span>
  )
}

export default function InteractionPage() {
  const sessionId = useSession()
  const [drugA, setDrugA] = useState('')
  const [drugB, setDrugB] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [usageInfo, setUsageInfo] = useState({ used: 0, limit: 3 })
  const [leadCaptured, setLeadCaptured] = useState(false)

  const handleCheck = async (e) => {
    e.preventDefault()
    if (!drugA.trim() || !drugB.trim()) return
    setLoading(true)
    setError('')
    try {
      const res = await interactionApi.check({
        session_id: sessionId,
        drug_a: drugA,
        drug_b: drugB,
      })
      setResult(res.data)
      setHistory((prev) => [
        { drugA: res.data.drug_a, drugB: res.data.drug_b, severity: res.data.severity },
        ...prev,
      ])
      setUsageInfo({ used: 3 - res.data.remaining_free_checks, limit: 3 })
      if (res.data.remaining_free_checks <= 1 && !leadCaptured) {
        setShowModal(true)
      }
    } catch (err) {
      if (err.response?.status === 429)
        setError('Daily limit reached. Join APhA for unlimited access.')
      else if (err.response?.status === 400) setError(err.response.data.detail)
      else setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleLeadCapture = async (email, name) => {
    await leadApi.capture({
      session_id: sessionId,
      email,
      name,
      source_tool: 'interaction',
      usage_id: result?.usage_id,
    })
    setLeadCaptured(true)
    setShowModal(false)
  }

  return (
    <div className="min-h-screen bg-gray-50 font-body">
      <APhAHeader activeTool="interactions" />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="font-display text-3xl font-bold text-gray-900 mb-2">
            Drug Interaction Checker
          </h1>
          <p className="text-gray-500 text-sm max-w-lg mx-auto">
            Check clinically significant drug interactions with AI-powered clinical summaries.
          </p>
        </div>

        <UsageMeter used={usageInfo.used} limit={usageInfo.limit} />

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mt-4">
          <form onSubmit={handleCheck} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <DrugSearchBox
                label="Drug A *"
                value={drugA}
                onChange={setDrugA}
                onSelect={setDrugA}
              />
              <DrugSearchBox
                label="Drug B *"
                value={drugB}
                onChange={setDrugB}
                onSelect={setDrugB}
              />
            </div>
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700">
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={loading || !drugA.trim() || !drugB.trim()}
              className="w-full bg-apha-blue text-white py-3.5 rounded-xl font-semibold hover:bg-apha-dark transition disabled:opacity-50"
            >
              {loading ? 'Checking...' : 'Check interaction'}
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
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
                <div className="flex items-center gap-3 mb-4">
                  <h3 className="font-semibold text-gray-800">
                    {result.drug_a} + {result.drug_b}
                  </h3>
                  <SeverityBadge severity={result.severity} />
                </div>

                <div className="bg-gray-50 rounded-xl p-4 mb-4">
                  <p className="text-sm text-gray-700 leading-relaxed">{result.summary}</p>
                </div>

                {result.mechanism && (
                  <div className="space-y-3">
                    {leadCaptured ? (
                      <>
                        <div>
                          <div className="text-xs font-semibold text-gray-500 uppercase mb-1">
                            Mechanism
                          </div>
                          <p className="text-sm text-gray-700">{result.mechanism}</p>
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-gray-500 uppercase mb-1">
                            Clinical Effect
                          </div>
                          <p className="text-sm text-gray-700">{result.clinical_effect}</p>
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-gray-500 uppercase mb-1">
                            Management
                          </div>
                          <p className="text-sm text-gray-700">{result.management}</p>
                        </div>
                      </>
                    ) : (
                      <div className="relative">
                        <div className="blur-sm select-none space-y-2">
                          <p className="text-sm text-gray-400">{result.mechanism}</p>
                          <p className="text-sm text-gray-400">{result.management}</p>
                        </div>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <button
                            onClick={() => setShowModal(true)}
                            className="bg-apha-blue text-white px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-apha-dark transition shadow-lg"
                          >
                            Unlock full details (free)
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <p className="text-xs text-gray-400 mt-4 italic">{result.disclaimer}</p>
              </div>

              <MemberUpsell tool="interactions" />
            </motion.div>
          )}
        </AnimatePresence>

        {history.length > 0 && (
          <div className="mt-6 bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h3 className="font-semibold text-gray-800 mb-3">Today&apos;s checks</h3>
            <div className="space-y-2">
              {history.map((h, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-2.5"
                >
                  <span className="text-sm text-gray-700">
                    {h.drugA} + {h.drugB}
                  </span>
                  <SeverityBadge severity={h.severity} />
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <LeadModal
        isOpen={showModal}
        tool="interactions"
        onSubmit={handleLeadCapture}
        onClose={() => setShowModal(false)}
      />
    </div>
  )
}
