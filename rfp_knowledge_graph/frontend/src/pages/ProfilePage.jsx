import { useState, useEffect } from 'react'
import { userApi } from '../api/client'

const SPECIALTIES = [
  'clinical-pharmacy', 'community-pharmacy', 'hospital-pharmacy', 'specialty-pharmacy',
  'consulting', 'public-health', 'compliance', 'technology', 'education', 'oncology',
  'telepharmacy', 'rural-health', 'long-term-care', 'managed-care', 'medicaid', 'pbm',
  'pharmacogenomics', 'antimicrobial-stewardship', 'compounding', 'informatics',
]

const ORG_TYPES = ['government', 'nonprofit', 'private', 'academic']

function TagSelect({ label, options, value, onChange }) {
  const toggle = (opt) => {
    const next = value.includes(opt) ? value.filter(v => v !== opt) : [...value, opt]
    onChange(next)
  }
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
      <div className="flex flex-wrap gap-2">
        {options.map(opt => (
          <button key={opt} type="button" onClick={() => toggle(opt)}
            className={`px-3 py-1 rounded-full text-xs border transition ${
              value.includes(opt)
                ? 'bg-[#1B4F8A] text-white border-[#1B4F8A]'
                : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'
            }`}>
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function ProfilePage() {
  const [form, setForm] = useState({
    full_name: '', bio: '', years_experience: '', location_state: '', location_city: '',
    specialties: [], certifications: [], org_types_preferred: [],
    notify_on_match: true, notify_threshold: 70,
  })
  const [certInput, setCertInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    userApi.me().then(r => {
      const p = r.data.profile || {}
      setForm({
        full_name: p.full_name || '',
        bio: p.bio || '',
        years_experience: p.years_experience ?? '',
        location_state: p.location_state || '',
        location_city: p.location_city || '',
        specialties: p.specialties || [],
        certifications: p.certifications || [],
        org_types_preferred: p.org_types_preferred || [],
        notify_on_match: p.notify_on_match ?? true,
        notify_threshold: p.notify_threshold ?? 70,
      })
    }).finally(() => setLoading(false))
  }, [])

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const addCert = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      const val = certInput.trim().replace(/,$/, '')
      if (val && !form.certifications.includes(val)) update('certifications', [...form.certifications, val])
      setCertInput('')
    }
  }
  const removeCert = (c) => update('certifications', form.certifications.filter(x => x !== c))

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await userApi.updateProfile({
        ...form,
        years_experience: form.years_experience ? parseInt(form.years_experience) : null,
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="text-gray-400 p-8">Loading...</div>

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>
        <p className="text-sm text-gray-500 mt-1">Your profile is used to match and score RFPs</p>
      </div>

      <form onSubmit={submit} className="space-y-6">
        {/* Personal Info */}
        <div className="bg-white rounded-xl border p-6 space-y-4">
          <h2 className="font-semibold text-gray-800">Personal Information</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.full_name} onChange={e => update('full_name', e.target.value)} placeholder="Dr. Jane Smith" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Years Experience</label>
              <input type="number" min="0" max="60"
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.years_experience} onChange={e => update('years_experience', e.target.value)} placeholder="10" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
              <input className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.location_state} onChange={e => update('location_state', e.target.value.toUpperCase().slice(0, 2))}
                placeholder="TX" maxLength={2} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
              <input className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.location_city} onChange={e => update('location_city', e.target.value)} placeholder="Houston" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
            <textarea rows={3}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={form.bio} onChange={e => update('bio', e.target.value)}
              placeholder="Brief professional background..." />
          </div>
        </div>

        {/* Specialties */}
        <div className="bg-white rounded-xl border p-6 space-y-4">
          <h2 className="font-semibold text-gray-800">Expertise</h2>
          <TagSelect label="Specialties" options={SPECIALTIES} value={form.specialties}
            onChange={v => update('specialties', v)} />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Certifications <span className="text-gray-400 font-normal">(type and press Enter)</span>
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {form.certifications.map(c => (
                <span key={c} className="flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">
                  {c}
                  <button type="button" onClick={() => removeCert(c)} className="hover:text-red-500">×</button>
                </span>
              ))}
            </div>
            <input className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={certInput} onChange={e => setCertInput(e.target.value)} onKeyDown={addCert}
              placeholder="PharmD, BCOP, BCPS, MTM..." />
          </div>
          <TagSelect label="Preferred Organization Types" options={ORG_TYPES} value={form.org_types_preferred}
            onChange={v => update('org_types_preferred', v)} />
        </div>

        {/* Notifications */}
        <div className="bg-white rounded-xl border p-6 space-y-4">
          <h2 className="font-semibold text-gray-800">Notifications</h2>
          <label className="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" className="w-4 h-4 accent-blue-600"
              checked={form.notify_on_match} onChange={e => update('notify_on_match', e.target.checked)} />
            <span className="text-sm text-gray-700">Email me when new matching RFPs are found</span>
          </label>
          {form.notify_on_match && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum match score to notify: <span className="text-blue-600 font-semibold">{form.notify_threshold}%</span>
              </label>
              <input type="range" min="0" max="100" step="5"
                className="w-full accent-blue-600"
                value={form.notify_threshold} onChange={e => update('notify_threshold', parseInt(e.target.value))} />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>0%</span><span>50%</span><span>100%</span>
              </div>
            </div>
          )}
        </div>

        <button type="submit" disabled={saving}
          className="bg-[#1B4F8A] text-white px-8 py-2.5 rounded-xl font-semibold disabled:opacity-50 flex items-center gap-2">
          {saving ? 'Saving...' : saved ? '✓ Saved' : 'Save Profile'}
        </button>
      </form>
    </div>
  )
}
