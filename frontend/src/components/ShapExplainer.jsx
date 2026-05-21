import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from 'recharts'

export default function ShapExplainer({ factors = [] }) {
  if (!factors.length) return <p className="text-gray-400 text-sm">No explanation available.</p>
  const data = factors.map(f => ({
    name: f.label,
    impact: parseFloat(f.impact.toFixed(3)),
    direction: f.direction,
  }))
  return (
    <div>
      <p className="text-xs text-gray-500 mb-3">
        Factors pushing this member's risk score up or down (SHAP values)
      </p>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 30 }}>
          <XAxis type="number" tick={{ fontSize: 11 }} />
          <YAxis type="category" dataKey="name" width={160} tick={{ fontSize: 11 }} />
          <Tooltip formatter={(v) => v.toFixed(3)} />
          <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.direction === 'increases_risk' ? '#ef4444' : '#22c55e'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex gap-4 mt-2 text-xs text-gray-500">
        <span><span className="inline-block w-3 h-3 bg-red-500 rounded-sm mr-1" />Increases risk</span>
        <span><span className="inline-block w-3 h-3 bg-green-500 rounded-sm mr-1" />Decreases risk</span>
      </div>
    </div>
  )
}
