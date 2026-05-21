import { useState, useEffect } from 'react'
import { nudgesApi } from '../api/client'
import NudgeHistoryTable from '../components/NudgeHistoryTable'

export default function NudgesPage() {
  const [nudges, setNudges] = useState([])
  const [channel, setChannel] = useState('')
  const [product, setProduct] = useState('')

  useEffect(() => {
    const params = {}
    if (channel) params.channel = channel
    if (product) params.product = product
    nudgesApi.list(params).then(r => setNudges(r.data)).catch(() => {})
  }, [channel, product])

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Nudge History</h1>
      <p className="text-sm text-gray-500 mb-5">All cross-sell nudges sent across email + banner channels</p>

      <div className="flex gap-3 mb-5">
        <select value={channel} onChange={e => setChannel(e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm">
          <option value="">All channels</option>
          <option value="email">Email</option>
          <option value="banner">Banner</option>
        </select>
        <select value={product} onChange={e => setProduct(e.target.value)}
          className="border rounded-lg px-3 py-1.5 text-sm">
          <option value="">All products</option>
          <option value="education">Education</option>
          <option value="publications">Publications</option>
          <option value="events">Events</option>
          <option value="career">Career</option>
          <option value="advocacy">Advocacy</option>
        </select>
      </div>

      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        <NudgeHistoryTable nudges={nudges} />
      </div>
    </div>
  )
}
