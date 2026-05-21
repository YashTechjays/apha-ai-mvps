import { useState } from 'react'
import { motion } from 'framer-motion'
import { STATES, LICENSE_TYPES, SPECIALTIES } from '../data/states'
import StepIndicator from '../components/StepIndicator'
import GapGauge from '../components/GapGauge'
import PlanCard from '../components/PlanCard'
import LeadCaptureModal from '../components/LeadCaptureModal'
import MembershipUpsell from '../components/MembershipUpsell'
import { useCalculator } from '../hooks/useCalculator'

export default function CalculatorPage() {
  const [form, setForm] = useState({
    state: '',
    renewal_date: '',
    hours_completed: '',
    license_type: 'pharmacist',
    specialty: 'General / Community Pharmacy',
  })
  const {
    step, loading, error, result, fullPlan, leadCaptured,
    showLeadModal, setShowLeadModal,
    calculate, captureLead, reset,
  } = useCalculator()

  const activeResult = fullPlan || result

  const handleSubmit = (e) => {
    e.preventDefault()
    calculate({ ...form, hours_completed: parseFloat(form.hours_completed) })
  }

  const urgencyColors = {
    low: 'bg-green-50 border-green-200 text-green-800',
    medium: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    high: 'bg-orange-50 border-orange-200 text-orange-800',
    critical: 'bg-red-50 border-red-200 text-red-800',
  }

  return (
    <div className="min-h-screen bg-gray-50 font-body">
      <header className="bg-apha-blue text-white py-4 px-6">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-blue-200 uppercase tracking-widest">
              American Pharmacists Association
            </div>
            <div className="font-display text-xl font-bold">pharmacist.com</div>
          </div>
          <a href="https://pharmacist.com/join" target="_blank" rel="noopener noreferrer"
            className="text-xs bg-white text-apha-blue px-4 py-2 rounded-lg font-semibold hover:bg-blue-50 transition">
            Join APhA
          </a>
        </div>
      </header>
      <main className="max-w-2xl mx-auto px-4 py-10">
        <StepIndicator currentStep={step} />

        {step === 1 && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <div className="text-center mb-8">
              <h1 className="font-display text-3xl font-bold text-gray-900 mb-3">
                Free CPE Gap Calculator
              </h1>
              <p className="text-gray-500 text-base max-w-md mx-auto">
                Find out exactly which courses you need for your state license renewal.
                Personalized plan in 30 seconds — free.
              </p>
            </div>
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">License state *</label>
                    <select value={form.state} onChange={e => setForm({...form, state: e.target.value})} required
                      className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue">
                      <option value="">Select state</option>
                      {STATES.map(s => <option key={s.code} value={s.code}>{s.name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">License type *</label>
                    <select value={form.license_type} onChange={e => setForm({...form, license_type: e.target.value})}
                      className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue">
                      {LICENSE_TYPES.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">License renewal date *</label>
                  <input type="date" value={form.renewal_date}
                    onChange={e => setForm({...form, renewal_date: e.target.value})} required
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                    CPE hours completed so far this cycle *
                  </label>
                  <input type="number" min="0" max="100" step="0.5"
                    placeholder="e.g. 8.5"
                    value={form.hours_completed}
                    onChange={e => setForm({...form, hours_completed: e.target.value})} required
                    className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue" />
                  <p className="text-xs text-gray-400 mt-1">Enter 0 if you haven't started yet</p>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1.5">Practice specialty</label>
                  <select value={form.specialty} onChange={e => setForm({...form, specialty: e.target.value})}
                    className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue">
                    {SPECIALTIES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700">{error}</div>
                )}
                <button type="submit" disabled={loading}
                  className="w-full bg-apha-blue text-white py-3.5 rounded-xl font-semibold text-base hover:bg-apha-dark transition disabled:opacity-50">
                  {loading ? '⏳ Generating your plan...' : 'Calculate my CPE gap →'}
                </button>
                <p className="text-center text-xs text-gray-400">
                  Free · No account required · Powered by APhA
                </p>
              </form>
            </div>
          </motion.div>
        )}

        {(step === 2 || step === 3) && activeResult && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            {activeResult.urgency_message && (
              <div className={`border rounded-xl p-3 mb-5 text-sm font-medium ${urgencyColors[activeResult.urgency_level]}`}>
                ⚠️ {activeResult.urgency_message}
              </div>
            )}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-5">
              <div className="flex items-center gap-6">
                <GapGauge pctComplete={activeResult.pct_complete}
                  hoursCompleted={activeResult.hours_completed}
                  hoursRequired={activeResult.hours_required} />
                <div className="flex-1">
                  <h2 className="font-display text-xl font-bold text-gray-900 mb-1">
                    {activeResult.state_name} CPE Plan
                  </h2>
                  <p className="text-sm text-gray-600 mb-3 leading-relaxed">{activeResult.summary}</p>
                  <div className="flex flex-wrap gap-3 text-sm">
                    <div className="bg-red-50 text-red-700 px-3 py-1 rounded-full font-semibold">
                      {activeResult.hours_gap}h still needed
                    </div>
                    <div className="bg-gray-100 text-gray-600 px-3 py-1 rounded-full">
                      {activeResult.days_until_renewal} days to renewal
                    </div>
                    {activeResult.mandatory_covered && (
                      <div className="bg-green-50 text-green-700 px-3 py-1 rounded-full">
                        ✓ Mandatory topics covered
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
            <div className="mb-2">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900">Your personalized course plan</h3>
                <span className="text-sm text-gray-400">
                  {activeResult.is_preview
                    ? `Showing ${activeResult.courses.length} of ${activeResult.preview_courses_count + 2}+ courses`
                    : `${activeResult.courses.length} courses · ${activeResult.total_plan_hours}h total`}
                </span>
              </div>
              <div className="space-y-3">
                {activeResult.courses.map((course, i) => (
                  <PlanCard key={course.course_id} course={course} index={i} isLocked={false} />
                ))}
                {activeResult.is_preview && !leadCaptured && (
                  <>
                    <div className="relative">
                      <PlanCard course={{ title: 'Unlock to see course', cpe_hours: 3, why_recommended: '', is_mandatory: false, price_nonmember: 0, url: '#', course_id: 'locked1' }} index={activeResult.courses.length} isLocked={true} />
                      <div className="absolute inset-0 flex items-center justify-center bg-white/80 rounded-xl">
                        <button onClick={() => setShowLeadModal(true)}
                          className="bg-apha-blue text-white px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-apha-dark transition">
                          🔓 Unlock full plan (free)
                        </button>
                      </div>
                    </div>
                    <div className="relative opacity-40">
                      <PlanCard course={{ title: 'Unlock to see course', cpe_hours: 2.5, why_recommended: '', is_mandatory: false, price_nonmember: 0, url: '#', course_id: 'locked2' }} index={activeResult.courses.length + 1} isLocked={true} />
                    </div>
                  </>
                )}
              </div>
            </div>
            <MembershipUpsell
              savings={Math.round(activeResult.member_savings_usd)}
              totalHours={activeResult.total_plan_hours}
              joinUrl="https://pharmacist.com/join"
            />
            <div className="text-center mt-6">
              <button onClick={reset} className="text-sm text-gray-400 hover:text-gray-600 underline">
                ← Start over
              </button>
            </div>
          </motion.div>
        )}

        <LeadCaptureModal
          isOpen={showLeadModal}
          hoursGap={result?.hours_gap}
          totalCourses={(result?.preview_courses_count || 3) + 2}
          onSubmit={captureLead}
          onClose={() => setShowLeadModal(false)}
        />
      </main>
      <footer className="text-center py-8 text-xs text-gray-400">
        © 2026 American Pharmacists Association · All CPE programs are ACPE-accredited ·
        <a href="https://pharmacist.com" className="underline ml-1">pharmacist.com</a>
      </footer>
    </div>
  )
}
