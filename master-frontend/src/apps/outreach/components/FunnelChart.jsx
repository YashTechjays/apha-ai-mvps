import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from 'recharts'

export default function FunnelChart({ data }) {
  const stages = [
    { key: 'total_prospects', label: 'Prospects', color: '#dbeafe' },
    { key: 'scored', label: 'Scored', color: '#93c5fd' },
    { key: 'contacted', label: 'Contacted', color: '#3b82f6' },
    { key: 'converted', label: 'Converted', color: '#1d4ed8' },
  ]
  const chartData = stages.map(s => ({ name: s.label, value: data?.[s.key] || 0, color: s.color }))
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={chartData}>
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey="value" radius={[6, 6, 0, 0]}>
          {chartData.map((d, i) => <Cell key={i} fill={d.color} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
