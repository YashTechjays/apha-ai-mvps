import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { scoresApi } from '../api/client'

const PRODUCT_ICONS = { education:'🎓', publications:'📖', events:'🎪', career:'💼', advocacy:'🏛️' }

export default function MembersPage() {
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [productFilter, setProductFilter] = useState('all')
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    const params = productFilter !== 'all' ? { product: productFilter } : {}
    scoresApi.listMembers(params)
      .then(r => { setMembers(r.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [productFilter])

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Expansion Opportunities</h1>
      <p className="text-sm text-gray-500 mb-5">Members ranked by cross-sell opportunity score</p>

      <div className="flex gap-2 mb-5 flex-wrap">
        {['all', 'education', 'publications', 'events', 'career', 'advocacy'].map(p => (
          <button key={p} onClick={() => setProductFilter(p)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium capitalize transition ${productFilter === p ? 'bg-[#1B4F8A] text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}>
            {PRODUCT_ICONS[p] || ''} {p === 'all' ? 'All products' : p}
          </button>
        ))}
      </div>

      {loading ? <p className="text-gray-400">Loading...</p> : (
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                {['Member', 'Tier', 'Active streams', 'Top opportunity', 'Score', 'Churn risk'].map(h => (
                  <th key={h} className="text-left px-4 py-3 font-semibold text-gray-600 text-xs uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y">
              {members.map(m => (
                <tr key={m.member_id} onClick={() => navigate(`/members/${m.member_id}`)}
                  className="hover:bg-blue-50 cursor-pointer transition">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{m.first_name} {m.last_name}</div>
                    <div className="text-xs text-gray-400">{m.email}</div>
                  </td>
                  <td className="px-4 py-3 capitalize text-gray-600">{m.tier?.replace('_',' ')}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <div className="w-24 bg-gray-200 rounded-full h-1.5">
                        <div className="bg-[#1B4F8A] h-1.5 rounded-full" style={{ width: `${(m.active_stream_count / 5) * 100}%` }} />
                      </div>
                      <span className="text-xs text-gray-500">{m.active_stream_count}/5</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-1.5 text-sm">
                      {PRODUCT_ICONS[m.top_opportunity_product]}
                      <span className="capitalize">{m.top_opportunity_product?.replace('_',' ')}</span>
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`font-bold text-sm ${(m.top_opportunity_score||0) >= 80 ? 'text-red-600' : (m.top_opportunity_score||0) >= 65 ? 'text-orange-500' : 'text-yellow-500'}`}>
                      {m.top_opportunity_score?.toFixed(0)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${(m.churn_score||0) >= 70 ? 'bg-red-100 text-red-700' : (m.churn_score||0) >= 50 ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}`}>
                      {m.churn_score?.toFixed(0) ?? '—'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {members.length === 0 && <div className="text-center py-12 text-gray-400">No opportunities found.</div>}
        </div>
      )}
    </div>
  )
}
