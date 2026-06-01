import { useState, useEffect, useRef } from 'react'
import { crawlApi } from '../api/client'

export default function CrawlPage() {
  const [url, setUrl] = useState('')
  const [jobs, setJobs] = useState([])
  const [triggering, setTriggering] = useState(false)
  const intervalRef = useRef(null)

  const loadJobs = () => {
    crawlApi.status().then(r => setJobs(r.data)).catch(() => {})
  }

  useEffect(() => {
    loadJobs()
    intervalRef.current = setInterval(loadJobs, 5000)
    return () => clearInterval(intervalRef.current)
  }, [])

  const trigger = async () => {
    setTriggering(true)
    try {
      await crawlApi.trigger(url || null)
      setUrl('')
      loadJobs()
    } catch { /* ignore */ }
    setTriggering(false)
  }

  const statusColor = (s) => {
    if (s === 'completed') return 'bg-green-100 text-green-700'
    if (s === 'running') return 'bg-blue-100 text-blue-700'
    if (s === 'failed') return 'bg-red-100 text-red-700'
    return 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Crawl Manager</h1>
        <p className="text-sm text-gray-500 mt-1">Trigger and monitor Firecrawl jobs</p>
      </div>

      <div className="bg-white rounded-xl border p-6">
        <h2 className="font-semibold text-gray-800 mb-3">Trigger New Crawl</h2>
        <div className="flex gap-3">
          <input
            className="border rounded-lg px-3 py-2 text-sm flex-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="URL to crawl (default: pharmacist.com)"
            value={url}
            onChange={e => setUrl(e.target.value)}
          />
          <button
            onClick={trigger}
            disabled={triggering}
            className="bg-[#1B4F8A] text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-blue-800 disabled:opacity-50">
            {triggering ? 'Starting...' : 'Start Crawl'}
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="font-semibold text-gray-800">Recent Crawl Jobs</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
            <tr>
              <th className="px-6 py-3 text-left">URL</th>
              <th className="px-6 py-3 text-left">Status</th>
              <th className="px-6 py-3 text-right">Pages</th>
              <th className="px-6 py-3 text-right">RFPs Found</th>
              <th className="px-6 py-3 text-left">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {jobs.map(job => (
              <tr key={job.id} className="hover:bg-gray-50">
                <td className="px-6 py-3 text-gray-700 max-w-xs truncate">{job.url}</td>
                <td className="px-6 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColor(job.status)}`}>
                    {job.status}
                  </span>
                </td>
                <td className="px-6 py-3 text-right">{job.pages_crawled}</td>
                <td className="px-6 py-3 text-right">{job.rfps_extracted}</td>
                <td className="px-6 py-3 text-gray-400">
                  {job.created_at ? new Date(job.created_at).toLocaleString() : '-'}
                </td>
              </tr>
            ))}
            {jobs.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-400">
                  No crawl jobs yet. Trigger one above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
