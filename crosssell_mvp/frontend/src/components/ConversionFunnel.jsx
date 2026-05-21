import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function ConversionFunnel({ total, opens, clicks, conversions }) {
  const data = [
    { stage: 'Sent', value: total, color: '#93c5fd' },
    { stage: 'Opened', value: opens, color: '#60a5fa' },
    { stage: 'Clicked', value: clicks, color: '#3b82f6' },
    { stage: 'Converted', value: conversions, color: '#1d4ed8' },
  ]
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 40 }}>
        <XAxis type="number" tick={{ fontSize: 11 }} />
        <YAxis type="category" dataKey="stage" width={70} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Bar dataKey="value" radius={[0, 6, 6, 0]}>
          {data.map((d, i) => <Cell key={i} fill={d.color} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
