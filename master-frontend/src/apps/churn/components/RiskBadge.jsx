const TIER_STYLES = {
  critical: 'bg-red-100 text-red-800 border border-red-300',
  high:     'bg-orange-100 text-orange-800 border border-orange-300',
  medium:   'bg-yellow-100 text-yellow-800 border border-yellow-300',
  low:      'bg-green-100 text-green-800 border border-green-300',
}

export default function RiskBadge({ tier }) {
  if (!tier) return <span className="text-gray-400 text-xs">Unscored</span>
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize ${TIER_STYLES[tier] || 'bg-gray-100 text-gray-600'}`}>
      {tier === 'critical' && <span className="mr-1">🔴</span>}
      {tier === 'high' && <span className="mr-1">🟠</span>}
      {tier === 'medium' && <span className="mr-1">🟡</span>}
      {tier === 'low' && <span className="mr-1">🟢</span>}
      {tier}
    </span>
  )
}
