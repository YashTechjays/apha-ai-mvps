const STAT_ITEMS = [
  { key: 'total_rfps', label: 'Total RFPs', color: 'text-blue-600' },
  { key: 'open_rfps', label: 'Open RFPs', color: 'text-green-600' },
  { key: 'total_organizations', label: 'Organizations', color: 'text-purple-600' },
  { key: 'total_locations', label: 'Locations', color: 'text-orange-600' },
  { key: 'total_categories', label: 'Categories', color: 'text-teal-600' },
  { key: 'total_relationships', label: 'Relationships', color: 'text-pink-600' },
]

export default function GraphStats({ stats }) {
  if (!stats) return null
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {STAT_ITEMS.map(({ key, label, color }) => (
        <div key={key} className="bg-white rounded-xl border p-4 text-center">
          <div className={`text-2xl font-bold ${color}`}>{stats[key] ?? 0}</div>
          <div className="text-xs text-gray-500 mt-1">{label}</div>
        </div>
      ))}
    </div>
  )
}
