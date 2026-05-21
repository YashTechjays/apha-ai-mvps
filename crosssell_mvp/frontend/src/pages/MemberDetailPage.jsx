import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { scoresApi, nudgesApi } from '../api/client'
import ProductUsageRadar from '../components/ProductUsageRadar'
import ExpansionScoreCard from '../components/ExpansionScoreCard'

export default function MemberDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [scores, setScores] = useState([])
  const [nudging, setNudging] = useState(null)

  useEffect(() => {
    scoresApi.getMemberScores(id).then(r => setScores(r.data))
  }, [id])

  const productScores = Object.fromEntries(scores.map(s => [s.product, s.score]))

  const sendNudge = async (product) => {
    setNudging(product)
    await nudgesApi.send(false, product)
    setNudging(null)
  }

  return (
    <div>
      <button onClick={() => navigate('/members')} className="text-blue-600 text-sm hover:underline mb-6 block">← Back</button>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Member Expansion Profile</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-4">Product usage radar</h2>
          <ProductUsageRadar scores={productScores} />
        </div>
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <h2 className="font-semibold text-gray-800 mb-4">Expansion opportunities</h2>
          <div className="space-y-3">
            {scores.filter(s => !s.already_active).map(s => (
              <div key={s.product}>
                <ExpansionScoreCard
                  product={s.product}
                  score={s.score}
                  reasons={s.top_reasons}
                  alreadyActive={s.already_active}
                />
                {s.score >= 60 && (
                  <button onClick={() => sendNudge(s.product)} disabled={nudging === s.product}
                    className="w-full mt-1 border border-gray-300 text-gray-700 text-xs py-1.5 rounded-lg hover:bg-gray-50 transition disabled:opacity-50">
                    {nudging === s.product ? 'Sending...' : `Send ${s.product} nudge →`}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
