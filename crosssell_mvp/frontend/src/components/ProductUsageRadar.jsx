import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts'

const PRODUCT_LABELS = {
  education: 'CPE', publications: 'Publications',
  events: 'Events', career: 'Career', advocacy: 'Advocacy',
}

export default function ProductUsageRadar({ scores = {} }) {
  const data = Object.entries(PRODUCT_LABELS).map(([key, label]) => ({
    product: label,
    score: scores[key] || 0,
  }))
  return (
    <ResponsiveContainer width="100%" height={220}>
      <RadarChart data={data}>
        <PolarGrid stroke="#e5e7eb" />
        <PolarAngleAxis dataKey="product" tick={{ fontSize: 11, fill: '#6b7280' }} />
        <Radar name="Expansion Score" dataKey="score" stroke="#1B4F8A" fill="#1B4F8A" fillOpacity={0.15} strokeWidth={2} />
        <Tooltip formatter={(v) => `${v.toFixed(0)}/100`} />
      </RadarChart>
    </ResponsiveContainer>
  )
}
