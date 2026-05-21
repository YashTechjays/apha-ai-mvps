export default function StatCard({ label, value, sublabel, color = 'blue' }) {
  const colors = {
    red:    'border-red-400 bg-red-50 text-red-700',
    orange: 'border-orange-400 bg-orange-50 text-orange-700',
    yellow: 'border-yellow-400 bg-yellow-50 text-yellow-700',
    green:  'border-green-400 bg-green-50 text-green-700',
    blue:   'border-blue-400 bg-blue-50 text-blue-700',
  }
  return (
    <div className={`rounded-xl border-l-4 p-4 shadow-sm ${colors[color]}`}>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-sm font-semibold mt-1">{label}</div>
      {sublabel && <div className="text-xs mt-0.5 opacity-70">{sublabel}</div>}
    </div>
  )
}
