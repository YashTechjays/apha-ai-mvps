import { campaignsApi } from '../api/client'

const STATUS_STYLES = {
  draft: 'bg-gray-100 text-gray-700',
  active: 'bg-green-100 text-green-700',
  paused: 'bg-yellow-100 text-yellow-700',
  completed: 'bg-blue-100 text-blue-700',
  archived: 'bg-gray-100 text-gray-400',
}

export default function CampaignCard({ campaign, onUpdate }) {
  const launch = async () => {
    await campaignsApi.launch(campaign.id, 100)
    onUpdate?.()
  }
  const pause = async () => {
    await campaignsApi.pause(campaign.id)
    onUpdate?.()
  }

  const openRate = campaign.sent > 0 ? `${(campaign.open_rate * 100).toFixed(0)}%` : '--'
  const clickRate = campaign.sent > 0 ? `${(campaign.click_rate * 100).toFixed(0)}%` : '--'

  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="font-semibold text-gray-900">{campaign.name}</div>
          <div className="text-xs text-gray-400 mt-0.5">
            {campaign.is_dry_run && <span className="mr-2 text-yellow-600 font-semibold">DRY RUN</span>}
            {campaign.target_tier && <span className="capitalize">{campaign.target_tier} </span>}
            {campaign.target_state && <span>{campaign.target_state}</span>}
          </div>
        </div>
        <span className={`text-xs px-2.5 py-0.5 rounded-full font-semibold capitalize ${STATUS_STYLES[campaign.status] || 'bg-gray-100'}`}>
          {campaign.status}
        </span>
      </div>
      <div className="grid grid-cols-4 gap-3 mb-4 text-center">
        {[
          { label: 'Prospects', value: campaign.prospects },
          { label: 'Sent', value: campaign.sent },
          { label: 'Open rate', value: openRate },
          { label: 'Conversions', value: campaign.conversions },
        ].map(s => (
          <div key={s.label} className="bg-gray-50 rounded-lg py-2">
            <div className="text-base font-bold text-gray-900">{s.value}</div>
            <div className="text-xs text-gray-400">{s.label}</div>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        {campaign.status === 'draft' && (
          <button onClick={launch}
            className="flex-1 bg-[#1B4F8A] text-white py-2 rounded-lg text-sm font-semibold hover:bg-blue-800 transition">
            {campaign.is_dry_run ? 'Launch (Dry Run)' : 'Launch Campaign'}
          </button>
        )}
        {campaign.status === 'active' && (
          <button onClick={pause}
            className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg text-sm font-semibold hover:bg-gray-50">
            Pause
          </button>
        )}
      </div>
    </div>
  )
}
