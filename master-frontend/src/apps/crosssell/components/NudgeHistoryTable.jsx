const CHANNEL_BADGE = {
  email: 'bg-blue-100 text-blue-700',
  banner: 'bg-purple-100 text-purple-700',
  concierge: 'bg-orange-100 text-orange-700',
}

export default function NudgeHistoryTable({ nudges = [] }) {
  if (nudges.length === 0) {
    return <p className="text-gray-400 text-sm text-center py-8">No nudges yet.</p>
  }
  return (
    <table className="w-full text-sm">
      <thead className="bg-gray-50 border-b">
        <tr>
          {['Member', 'Product', 'Channel', 'Score', 'Sent', 'Engagement'].map(h => (
            <th key={h} className="text-left px-4 py-3 font-semibold text-gray-600 text-xs uppercase">{h}</th>
          ))}
        </tr>
      </thead>
      <tbody className="divide-y">
        {nudges.map(n => (
          <tr key={n.id} className="hover:bg-gray-50">
            <td className="px-4 py-3 font-mono text-xs text-gray-500">{n.member_id.slice(0, 8)}…</td>
            <td className="px-4 py-3 capitalize">{n.product}</td>
            <td className="px-4 py-3">
              <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${CHANNEL_BADGE[n.channel] || ''}`}>
                {n.channel}
              </span>
            </td>
            <td className="px-4 py-3 font-semibold">{n.expansion_score?.toFixed(0)}</td>
            <td className="px-4 py-3 text-gray-500">{n.sent_at ? new Date(n.sent_at).toLocaleDateString() : '—'}</td>
            <td className="px-4 py-3 text-xs">
              {n.clicked_at ? '✓ Clicked' : n.opened_at ? '👁 Opened' : '—'}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
