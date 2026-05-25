export default function GapGauge({ pctComplete, hoursCompleted, hoursRequired }) {
  const radius = 54
  const circ = 2 * Math.PI * radius
  const filled = (pctComplete / 100) * circ
  const color = pctComplete >= 80 ? '#22c55e' : pctComplete >= 50 ? '#f59e0b' : '#ef4444'
  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="10" />
        <circle cx="70" cy="70" r={radius} fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={`${filled} ${circ}`} strokeLinecap="round"
          transform="rotate(-90 70 70)"
          style={{ transition: 'stroke-dasharray 1s ease' }}
        />
        <text x="70" y="65" textAnchor="middle" fontSize="22" fontWeight="600" fill={color}>
          {Math.round(pctComplete)}%
        </text>
        <text x="70" y="85" textAnchor="middle" fontSize="11" fill="#6b7280">complete</text>
      </svg>
      <div className="text-center mt-1">
        <span className="text-sm text-gray-600">
          <span className="font-semibold text-gray-900">{hoursCompleted}</span> of{' '}
          <span className="font-semibold text-gray-900">{hoursRequired}</span> hours
        </span>
      </div>
    </div>
  )
}
