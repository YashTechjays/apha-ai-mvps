export default function ScoreBar({ score }) {
  if (score == null) return <span className="text-gray-400 text-sm">—</span>
  const color =
    score >= 85 ? 'bg-red-500' :
    score >= 70 ? 'bg-orange-400' :
    score >= 50 ? 'bg-yellow-400' :
    'bg-green-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-200 rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-sm font-semibold w-10 text-right">{score.toFixed(0)}</span>
    </div>
  )
}
