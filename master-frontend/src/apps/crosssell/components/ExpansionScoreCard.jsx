const PRODUCT_META = {
  education:    { icon: '🎓', label: 'CPE & Training',      color: 'border-blue-200 bg-blue-50',    text: 'text-blue-700' },
  publications: { icon: '📖', label: 'Publications',         color: 'border-purple-200 bg-purple-50', text: 'text-purple-700' },
  events:       { icon: '🎪', label: 'Events & Conferences', color: 'border-green-200 bg-green-50',   text: 'text-green-700' },
  career:       { icon: '💼', label: 'Career Services',      color: 'border-orange-200 bg-orange-50', text: 'text-orange-700' },
  advocacy:     { icon: '🏛️', label: 'Advocacy',             color: 'border-red-200 bg-red-50',       text: 'text-red-700' },
}

export default function ExpansionScoreCard({ product, score, reasons = [], alreadyActive = false }) {
  const meta = PRODUCT_META[product] || {}
  if (alreadyActive) return null
  return (
    <div className={`border rounded-xl p-4 ${meta.color}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{meta.icon}</span>
          <span className={`font-semibold text-sm ${meta.text}`}>{meta.label}</span>
        </div>
        <div className={`text-xl font-bold ${meta.text}`}>{score?.toFixed(0)}</div>
      </div>
      <div className="w-full bg-white rounded-full h-1.5 mb-3">
        <div className={`h-1.5 rounded-full ${meta.text.replace('text', 'bg')}`}
          style={{ width: `${score}%` }} />
      </div>
      {reasons.slice(0, 2).map((r, i) => (
        <p key={i} className={`text-xs ${meta.text} opacity-80 mb-1`}>• {r}</p>
      ))}
    </div>
  )
}
