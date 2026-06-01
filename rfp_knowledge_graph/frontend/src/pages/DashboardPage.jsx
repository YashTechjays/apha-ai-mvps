import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { graphApi, rfpApi, recommendationApi, crawlApi, matchApi } from '../api/client'
import GraphStats from '../components/GraphStats'
import RfpCard from '../components/RfpCard'
import PredictedOpportunities from '../components/PredictedOpportunities'

function getRole() {
  return localStorage.getItem('role') || 'admin'
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [recent, setRecent] = useState([])
  const [recommended, setRecommended] = useState([])
  const [collaborative, setCollaborative] = useState([])
  const [insights, setInsights] = useState(null)
  const [crawling, setCrawling] = useState(false)
  const isPharmacist = getRole() === 'pharmacist'

  useEffect(() => {
    graphApi.stats().then(r => setStats(r.data)).catch(() => {})
    rfpApi.list({ limit: 5 }).then(r => setRecent(r.data.items)).catch(() => {})
    if (isPharmacist) {
      matchApi.getMatches({ limit: 5 }).then(r => setRecommended(r.data.items)).catch(() => {})
      matchApi.collaborative({ limit: 5 }).then(r => setCollaborative(r.data.items)).catch(() => {})
    } else {
      recommendationApi.get({ limit: 5 }).then(r => setRecommended(r.data)).catch(() => {})
      graphApi.insights({ limit: 5 }).then(r => setInsights(r.data)).catch(() => {})
    }
  }, [])

  const triggerCrawl = async () => {
    setCrawling(true)
    try {
      await crawlApi.trigger()
    } catch { /* ignore */ }
    setCrawling(false)
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">RFP Knowledge Graph</h1>
          <p className="text-sm text-gray-500 mt-1">Pharmacy RFP discovery powered by Firecrawl + Neo4j</p>
        </div>
        {!isPharmacist && (
          <button
            onClick={triggerCrawl}
            disabled={crawling}
            className="bg-[#1B4F8A] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-800 disabled:opacity-50">
            {crawling ? 'Crawling...' : 'Trigger Crawl'}
          </button>
        )}
      </div>

      <GraphStats stats={stats} />

      <PredictedOpportunities personalized={isPharmacist} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent RFPs</h2>
            <Link to="/rfps" className="text-sm text-blue-600 hover:underline">View all</Link>
          </div>
          <div className="space-y-3">
            {recent.map(rfp => <RfpCard key={rfp.id} rfp={rfp} />)}
            {recent.length === 0 && (
              <p className="text-sm text-gray-400">No RFPs found. Try triggering a crawl.</p>
            )}
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            {isPharmacist ? 'Your Top Matches' : 'Recommended RFPs'}
          </h2>
          <div className="space-y-3">
            {recommended.map(rfp => <RfpCard key={rfp.id} rfp={rfp} />)}
            {recommended.length === 0 && (
              <p className="text-sm text-gray-400">
                {isPharmacist ? 'Complete your profile to see matches.' : 'No recommendations yet.'}
              </p>
            )}
          </div>
          {isPharmacist && (
            <Link to="/rfps" className="text-sm text-blue-600 hover:underline mt-3 inline-block">
              Browse all RFPs
            </Link>
          )}
        </div>
      </div>

      {isPharmacist && collaborative.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-1">Pharmacists Like You Also Pursued</h2>
          <p className="text-sm text-gray-500 mb-4">Recommended from shared application history in the knowledge graph</p>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {collaborative.map(rfp => (
              <Link key={rfp.id} to={`/rfps/${rfp.id}`}
                className="block border border-gray-200 rounded-lg p-4 hover:border-blue-400 transition">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-gray-900 text-sm">{rfp.title}</h3>
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full whitespace-nowrap ml-2">
                    {rfp.peer_count} peer{rfp.peer_count === 1 ? '' : 's'}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{rfp.organization_name || 'Unknown org'}</p>
              </Link>
            ))}
          </div>
        </div>
      )}

      {!isPharmacist && insights && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Most Active Organizations</h2>
            <div className="space-y-2">
              {(insights.top_organizations || []).map((o, i) => (
                <div key={i} className="flex items-center justify-between border border-gray-200 rounded-lg px-4 py-2">
                  <span className="text-sm text-gray-900">{o.organization}</span>
                  <span className="text-xs text-gray-500">{o.rfp_count} RFPs · {o.open_count} open</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Trending Categories</h2>
            <div className="space-y-2">
              {(insights.trending_categories || []).map((c, i) => (
                <div key={i} className="flex items-center justify-between border border-gray-200 rounded-lg px-4 py-2">
                  <span className="text-sm text-gray-900">{c.category}</span>
                  <span className="text-xs text-gray-500">{c.demand} RFPs</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
