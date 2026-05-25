import { useState } from 'react'
import { nudgesApi } from '../api/client'

const PRODUCT_COLORS = {
  education: 'from-blue-600 to-blue-800',
  publications: 'from-purple-600 to-purple-800',
  events: 'from-green-600 to-green-800',
  career: 'from-orange-600 to-orange-800',
  advocacy: 'from-red-600 to-red-800',
}

export default function CrossSellBanner({ banner, onDismiss }) {
  const [clicked, setClicked] = useState(false)
  if (!banner?.has_banner) return null

  const handleClick = async () => {
    setClicked(true)
    if (banner.nudge_id && banner.nudge_id !== 'none') {
      await nudgesApi.markClicked(banner.nudge_id).catch(() => {})
    }
    window.open(banner.cta_url, '_blank')
  }
  const gradient = PRODUCT_COLORS[banner.product] || 'from-gray-600 to-gray-800'

  return (
    <div className={`bg-gradient-to-r ${gradient} text-white rounded-2xl p-5 mb-6 flex items-center gap-5`}>
      <div className="text-4xl shrink-0">{banner.icon}</div>
      <div className="flex-1">
        <div className="font-bold text-base mb-0.5">{banner.headline}</div>
        <div className="text-sm text-white/80">{banner.body}</div>
      </div>
      <div className="flex items-center gap-3 shrink-0">
        <button onClick={handleClick} disabled={clicked}
          className="bg-white text-gray-900 px-4 py-2 rounded-xl text-sm font-semibold hover:bg-gray-100 transition disabled:opacity-70">
          {clicked ? '✓ Opened' : banner.cta_label}
        </button>
        <button onClick={onDismiss} className="text-white/60 hover:text-white text-xl">×</button>
      </div>
    </div>
  )
}
