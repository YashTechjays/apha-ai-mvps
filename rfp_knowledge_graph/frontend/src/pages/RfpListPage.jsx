import { useState, useEffect } from 'react'
import { rfpApi } from '../api/client'
import RfpCard from '../components/RfpCard'
import FilterPanel from '../components/FilterPanel'

export default function RfpListPage() {
  const [rfps, setRfps] = useState([])
  const [total, setTotal] = useState(0)
  const [filters, setFilters] = useState({ q: '', status: '', state: '', category: '' })
  const [page, setPage] = useState(0)
  const limit = 12

  useEffect(() => {
    const controller = new AbortController()
    const params = { limit, offset: page * limit }
    if (filters.q) params.q = filters.q
    if (filters.status) params.status = filters.status
    if (filters.state) params.state = filters.state
    if (filters.category) params.category = filters.category
    rfpApi.list(params, { signal: controller.signal }).then(r => {
      setRfps(r.data.items)
      setTotal(r.data.total)
    }).catch(() => {})
    return () => controller.abort()
  }, [filters, page])

  useEffect(() => { setPage(0) }, [filters])

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">RFP Explorer</h1>
        <p className="text-sm text-gray-500 mt-1">{total} RFPs in knowledge graph</p>
      </div>

      <FilterPanel filters={filters} onChange={setFilters} />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {rfps.map(rfp => <RfpCard key={rfp.id} rfp={rfp} />)}
      </div>

      {rfps.length === 0 && (
        <p className="text-center text-gray-400 py-12">No RFPs match your filters.</p>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-3 py-1 border rounded text-sm disabled:opacity-30">
            Prev
          </button>
          <span className="text-sm text-gray-500">
            Page {page + 1} of {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="px-3 py-1 border rounded text-sm disabled:opacity-30">
            Next
          </button>
        </div>
      )}
    </div>
  )
}
