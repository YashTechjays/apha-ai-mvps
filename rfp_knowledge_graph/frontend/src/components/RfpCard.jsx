import { Link } from 'react-router-dom'
import StatusBadge from './StatusBadge'
import { sourceLabel } from '../utils/source'

function MatchBadge({ score }) {
  if (score == null) return null
  const color = score >= 80 ? 'bg-green-100 text-green-700' : score >= 60 ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-500'
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${color}`}>{score}% match</span>
  )
}

export default function RfpCard({ rfp }) {
  const daysLeft = rfp.deadline
    ? Math.ceil((new Date(rfp.deadline) - new Date()) / 86400000)
    : null

  return (
    <Link to={`/rfps/${rfp.id}`}
      className="block bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition">
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-gray-900 text-sm leading-snug flex-1 mr-3">
          {rfp.title}
        </h3>
        <div className="flex items-center gap-2 shrink-0">
          <MatchBadge score={rfp.match_score} />
          <StatusBadge status={rfp.status} deadline={rfp.deadline} />
        </div>
      </div>

      {rfp.organization_name && (
        <p className="text-xs text-gray-500 mb-1">{rfp.organization_name}</p>
      )}

      {rfp.location && (
        <p className="text-xs text-gray-400 mb-2">{rfp.location}</p>
      )}

      {sourceLabel(rfp) && (
        <p className="text-xs text-gray-400 mb-2">Source: {sourceLabel(rfp)}</p>
      )}

      <div className="flex flex-wrap gap-1 mb-3">
        {rfp.categories?.map(cat => (
          <span key={cat} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">
            {cat}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between text-xs text-gray-400">
        {rfp.budget_range && <span>{rfp.budget_range}</span>}
        {rfp.deadline && (
          <span className={daysLeft <= 7 ? 'text-red-500 font-medium' : ''}>
            Due: {rfp.deadline} {daysLeft > 0 ? `(${daysLeft}d left)` : '(past due)'}
          </span>
        )}
      </div>
    </Link>
  )
}
