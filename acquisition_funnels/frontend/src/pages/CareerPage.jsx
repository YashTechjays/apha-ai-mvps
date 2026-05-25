import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
} from 'recharts'
import { careerApi, leadApi } from '../api/client'
import { useSession } from '../hooks/useSession'
import APhAHeader from '../components/shared/APhAHeader'
import LeadModal from '../components/shared/LeadModal'
import MemberUpsell from '../components/shared/MemberUpsell'

const SPECIALTIES = [
  'Hospital/Health-System',
  'Community Pharmacy',
  'Ambulatory Care',
  'Managed Care',
  'Long-Term Care',
  'Oncology',
  'Academia',
  'Industry/Pharmaceutical',
  'Government/Military',
  'Pediatrics',
  'Infectious Disease',
]

const CAREER_STAGES = [
  { value: 'student', label: 'Student' },
  { value: 'new_practitioner', label: 'New Practitioner (0-3 yrs)' },
  { value: 'mid_career', label: 'Mid-Career (3-10 yrs)' },
  { value: 'senior', label: 'Senior (10-20 yrs)' },
  { value: 'expert', label: 'Expert (20+ yrs)' },
]

const STATES = [
  'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA',
  'KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
  'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT',
  'VA','WA','WV','WI','WY','DC',
]

const EXP_RANGES = ['0-2', '3-5', '6-10', '11-15', '16-20', '20+']

function ScoreGauge({ score, label }) {
  const circumference = 2 * Math.PI * 45
  const offset = circumference - (score / 100) * circumference
  const color =
    score >= 80 ? '#22c55e' : score >= 60 ? '#3b82f6' : score >= 40 ? '#f59e0b' : '#ef4444'

  return (
    <div className="flex flex-col items-center">
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="45" fill="none" stroke="#e5e7eb" strokeWidth="10" />
        <circle
          cx="60"
          cy="60"
          r="45"
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 60 60)"
        />
        <text x="60" y="55" textAnchor="middle" className="text-2xl font-bold" fill={color}>
          {score}
        </text>
        <text x="60" y="72" textAnchor="middle" className="text-xs" fill="#9ca3af">
          /100
        </text>
      </svg>
      {label && <div className="text-sm font-medium text-gray-700 mt-1">{label}</div>}
    </div>
  )
}

export default function CareerPage() {
  const sessionId = useSession()
  const [step, setStep] = useState(1)
  const [form, setForm] = useState({
    license_type: 'pharmacist',
    specialty: 'Hospital/Health-System',
    state: 'TX',
    years_experience: '6-10',
    career_stage: 'mid_career',
    board_certifications: 0,
    cpe_hours_2yr: 0,
    certificates_earned: 0,
    immunization_certified: false,
    mtm_experience: false,
    leadership_roles: 0,
    advocacy_activities: false,
    mentorship_active: false,
    technology_skills: 3,
    association_member: false,
    presentations_given: 0,
    research_collaborations: false,
  })
  const [result, setResult] = useState(null)
  const [actionPlan, setActionPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [leadCaptured, setLeadCaptured] = useState(false)

  const updateForm = (key, value) => setForm((prev) => ({ ...prev, [key]: value }))

  const handleSubmit = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await careerApi.score({ ...form, session_id: sessionId })
      setResult(res.data)
      setStep(4)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleLeadCapture = async (email, name) => {
    await leadApi.capture({
      session_id: sessionId,
      email,
      name,
      source_tool: 'career',
      usage_id: result?.usage_id,
      state: form.state,
      specialty: form.specialty,
      career_stage: form.career_stage,
      career_score: result?.overall_score,
      top_gap_dimension: result?.top_gap,
    })
    setLeadCaptured(true)
    setShowModal(false)
    // Fetch action plan
    try {
      const planRes = await careerApi.getActionPlan(result.usage_id, sessionId)
      setActionPlan(planRes.data.action_plan)
    } catch {
      // Plan retrieval failed silently
    }
  }

  const radarData = result
    ? Object.entries(result.scores).map(([key, val]) => ({
        dimension: val.label || key,
        score: val.score || 0,
        fullMark: 100,
      }))
    : []

  const selectClass =
    'w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue'
  const inputClass = selectClass

  return (
    <div className="min-h-screen bg-gray-50 font-body">
      <APhAHeader activeTool="career" />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="font-display text-3xl font-bold text-gray-900 mb-2">
            Career Readiness Scorer
          </h1>
          <p className="text-gray-500 text-sm max-w-lg mx-auto">
            Score your career across 6 competency dimensions. Takes about 3 minutes.
          </p>
        </div>

        {/* Progress bar */}
        {step < 4 && (
          <div className="flex gap-2 mb-6">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`h-1.5 flex-1 rounded-full ${
                  s <= step ? 'bg-apha-blue' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        )}

        {/* Step 1: Basic profile */}
        {step === 1 && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Step 1: Your profile</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                    Career stage
                  </label>
                  <select
                    value={form.career_stage}
                    onChange={(e) => updateForm('career_stage', e.target.value)}
                    className={selectClass}
                  >
                    {CAREER_STAGES.map((c) => (
                      <option key={c.value} value={c.value}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">State</label>
                  <select
                    value={form.state}
                    onChange={(e) => updateForm('state', e.target.value)}
                    className={selectClass}
                  >
                    {STATES.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Specialty
                </label>
                <select
                  value={form.specialty}
                  onChange={(e) => updateForm('specialty', e.target.value)}
                  className={selectClass}
                >
                  {SPECIALTIES.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Years of experience
                </label>
                <select
                  value={form.years_experience}
                  onChange={(e) => updateForm('years_experience', e.target.value)}
                  className={selectClass}
                >
                  {EXP_RANGES.map((r) => (
                    <option key={r} value={r}>
                      {r} years
                    </option>
                  ))}
                </select>
              </div>
              <button
                onClick={() => setStep(2)}
                className="w-full bg-apha-blue text-white py-3.5 rounded-xl font-semibold hover:bg-apha-dark transition"
              >
                Next: Clinical skills &rarr;
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Clinical skills */}
        {step === 2 && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Step 2: Clinical skills</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                    Board certifications held
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={form.board_certifications}
                    onChange={(e) => updateForm('board_certifications', parseInt(e.target.value) || 0)}
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                    CPE hours (last 2 years)
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={form.cpe_hours_2yr}
                    onChange={(e) => updateForm('cpe_hours_2yr', parseFloat(e.target.value) || 0)}
                    className={inputClass}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Certificate programs completed
                </label>
                <input
                  type="number"
                  min="0"
                  value={form.certificates_earned}
                  onChange={(e) => updateForm('certificates_earned', parseInt(e.target.value) || 0)}
                  className={inputClass}
                />
              </div>
              <div className="space-y-3">
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={form.immunization_certified}
                    onChange={(e) => updateForm('immunization_certified', e.target.checked)}
                    className="rounded border-gray-300 text-apha-blue focus:ring-apha-blue"
                  />
                  <span className="text-sm text-gray-700">Immunization certified</span>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={form.mtm_experience}
                    onChange={(e) => updateForm('mtm_experience', e.target.checked)}
                    className="rounded border-gray-300 text-apha-blue focus:ring-apha-blue"
                  />
                  <span className="text-sm text-gray-700">MTM experience</span>
                </label>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-xl font-semibold hover:bg-gray-50 transition"
                >
                  &larr; Back
                </button>
                <button
                  onClick={() => setStep(3)}
                  className="flex-1 bg-apha-blue text-white py-3 rounded-xl font-semibold hover:bg-apha-dark transition"
                >
                  Next: Professional activities &rarr;
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Professional activities */}
        {step === 3 && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Step 3: Professional activities</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                    Leadership roles held
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={form.leadership_roles}
                    onChange={(e) => updateForm('leadership_roles', parseInt(e.target.value) || 0)}
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                    Presentations given
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={form.presentations_given}
                    onChange={(e) => updateForm('presentations_given', parseInt(e.target.value) || 0)}
                    className={inputClass}
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                  Technology skills (1-5)
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={form.technology_skills}
                  onChange={(e) => updateForm('technology_skills', parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>Basic</span>
                  <span>Advanced</span>
                </div>
              </div>
              <div className="space-y-3">
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={form.advocacy_activities}
                    onChange={(e) => updateForm('advocacy_activities', e.target.checked)}
                    className="rounded border-gray-300 text-apha-blue focus:ring-apha-blue"
                  />
                  <span className="text-sm text-gray-700">Active in advocacy</span>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={form.mentorship_active}
                    onChange={(e) => updateForm('mentorship_active', e.target.checked)}
                    className="rounded border-gray-300 text-apha-blue focus:ring-apha-blue"
                  />
                  <span className="text-sm text-gray-700">Active mentor/mentee</span>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={form.association_member}
                    onChange={(e) => updateForm('association_member', e.target.checked)}
                    className="rounded border-gray-300 text-apha-blue focus:ring-apha-blue"
                  />
                  <span className="text-sm text-gray-700">Professional association member</span>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={form.research_collaborations}
                    onChange={(e) => updateForm('research_collaborations', e.target.checked)}
                    className="rounded border-gray-300 text-apha-blue focus:ring-apha-blue"
                  />
                  <span className="text-sm text-gray-700">Research collaborations</span>
                </label>
              </div>
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700">
                  {error}
                </div>
              )}
              <div className="flex gap-3">
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-xl font-semibold hover:bg-gray-50 transition"
                >
                  &larr; Back
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="flex-1 bg-apha-blue text-white py-3 rounded-xl font-semibold hover:bg-apha-dark transition disabled:opacity-50"
                >
                  {loading ? 'Scoring...' : 'Get my score'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Results */}
        <AnimatePresence>
          {step === 4 && result && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
              {/* Overall score */}
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4 text-center">
                <h2 className="font-semibold text-gray-800 mb-4">Your Career Readiness Score</h2>
                <ScoreGauge score={result.overall_score} />
                <p className="text-sm text-gray-600 mt-4 max-w-md mx-auto">{result.summary}</p>
                <div className="flex justify-center gap-6 mt-4 text-sm">
                  <div>
                    <span className="text-gray-500">Peer percentile:</span>{' '}
                    <span className="font-semibold text-apha-blue">
                      {result.peer_percentile}th
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Trajectory:</span>{' '}
                    <span className="font-semibold text-gray-800">{result.trajectory}</span>
                  </div>
                </div>
              </div>

              {/* Radar chart */}
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
                <h3 className="font-semibold text-gray-800 mb-4">Competency breakdown</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 11 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
                    <Radar
                      name="Score"
                      dataKey="score"
                      stroke="#1B4F8A"
                      fill="#1B4F8A"
                      fillOpacity={0.3}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              {/* Score breakdown */}
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
                <h3 className="font-semibold text-gray-800 mb-4">Dimension scores</h3>
                <div className="space-y-3">
                  {Object.entries(result.scores).map(([key, val]) => (
                    <div key={key}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="font-medium text-gray-700">{val.label || key}</span>
                        <span className="font-semibold text-gray-900">{val.score}/100</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            val.score >= 70
                              ? 'bg-green-500'
                              : val.score >= 50
                              ? 'bg-blue-500'
                              : 'bg-orange-400'
                          }`}
                          style={{ width: `${val.score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 p-3 bg-green-50 rounded-xl">
                  <div className="text-xs font-semibold text-green-700 mb-1">Top strength</div>
                  <p className="text-sm text-green-800">{result.top_strength_note}</p>
                </div>
                <div className="mt-2 p-3 bg-orange-50 rounded-xl">
                  <div className="text-xs font-semibold text-orange-700 mb-1">
                    Biggest opportunity
                  </div>
                  <p className="text-sm text-orange-800">{result.top_gap_note}</p>
                </div>
              </div>

              {/* Action plan - gated */}
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4 relative">
                <h3 className="font-semibold text-gray-800 mb-3">Your 90-day action plan</h3>
                {leadCaptured && actionPlan ? (
                  <div className="space-y-4">
                    <p className="text-sm font-medium text-apha-blue">{actionPlan.headline}</p>
                    {actionPlan.actions?.map((action, i) => (
                      <div key={i} className="bg-gray-50 rounded-xl p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs bg-apha-blue text-white px-2 py-0.5 rounded-full font-semibold">
                            {action.timeline}
                          </span>
                          <span className="font-semibold text-sm text-gray-800">
                            {action.title}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{action.description}</p>
                        <p className="text-xs text-apha-blue font-medium">
                          APhA Resource: {action.apha_resource}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="relative">
                    <div className="blur-sm select-none space-y-3">
                      <div className="bg-gray-50 rounded-xl p-4 h-20" />
                      <div className="bg-gray-50 rounded-xl p-4 h-20" />
                      <div className="bg-gray-50 rounded-xl p-4 h-20" />
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <button
                        onClick={() => setShowModal(true)}
                        className="bg-apha-blue text-white px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-apha-dark transition shadow-lg"
                      >
                        Unlock your action plan (free)
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <MemberUpsell tool="career" />

              <div className="text-center mt-6">
                <button
                  onClick={() => {
                    setStep(1)
                    setResult(null)
                    setActionPlan(null)
                  }}
                  className="text-sm text-apha-blue font-semibold hover:underline"
                >
                  Retake assessment
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <LeadModal
        isOpen={showModal}
        tool="career"
        onSubmit={handleLeadCapture}
        onClose={() => setShowModal(false)}
      />
    </div>
  )
}
