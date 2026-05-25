import { useState, useEffect } from 'react'
import { analyticsApi, campaignsApi } from '../api/client'
import CampaignCard from '../components/CampaignCard'

const TIERS = ['pharmacist', 'new_practitioner', 'student', 'technician']
const STATES = ['', 'CA', 'TX', 'FL', 'NY', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    name: '', target_tier: 'pharmacist', target_state: '',
    min_icp_score: 65, daily_send_cap: 100, is_dry_run: true,
  })

  const load = () => analyticsApi.campaigns().then(r => setCampaigns(r.data)).catch(() => {})
  useEffect(() => { load() }, [])

  const createCampaign = async (e) => {
    e.preventDefault()
    await campaignsApi.create(form)
    setShowForm(false)
    load()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
        <button onClick={() => setShowForm(!showForm)}
          className="bg-[#1B4F8A] text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-800">
          + New Campaign
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-2xl border border-gray-200 p-6 mb-6">
          <h2 className="font-semibold text-gray-800 mb-4">Create Campaign</h2>
          <form onSubmit={createCampaign} className="space-y-4">
            <input placeholder="Campaign name" value={form.name}
              onChange={e => setForm({...form, name: e.target.value})} required
              className="w-full border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Target tier</label>
                <select value={form.target_tier} onChange={e => setForm({...form, target_tier: e.target.value})}
                  className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                  {TIERS.map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">State (optional)</label>
                <select value={form.target_state} onChange={e => setForm({...form, target_state: e.target.value})}
                  className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                  {STATES.map(s => <option key={s} value={s}>{s || 'All states'}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Min ICP score</label>
                <input type="number" min={40} max={100} value={form.min_icp_score}
                  onChange={e => setForm({...form, min_icp_score: parseInt(e.target.value)})}
                  className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <input type="checkbox" id="dry_run" checked={form.is_dry_run}
                onChange={e => setForm({...form, is_dry_run: e.target.checked})} />
              <label htmlFor="dry_run" className="text-sm text-gray-700">
                Dry run (generate emails but don't send -- recommended for first launch)
              </label>
            </div>
            <div className="flex gap-3">
              <button type="submit"
                className="bg-[#1B4F8A] text-white px-5 py-2 rounded-lg text-sm font-semibold">
                Create Campaign
              </button>
              <button type="button" onClick={() => setShowForm(false)}
                className="border border-gray-300 text-gray-600 px-5 py-2 rounded-lg text-sm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {campaigns.map(c => <CampaignCard key={c.id} campaign={c} onUpdate={load} />)}
        {campaigns.length === 0 && (
          <div className="col-span-2 text-center py-12 text-gray-400">
            No campaigns yet. Create your first campaign above.
          </div>
        )}
      </div>
    </div>
  )
}
