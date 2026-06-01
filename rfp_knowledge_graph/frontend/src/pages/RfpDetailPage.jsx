import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { rfpApi, applicationApi, matchApi } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import WinRoomModal from '../components/WinRoomModal'
import CoalitionPanel from '../components/CoalitionPanel'
import SimulatorPanel from '../components/SimulatorPanel'
import { sourceLabel } from '../utils/source'

function getRole() {
  return localStorage.getItem('role') || 'admin'
}

function ProposalModal({ rfpId, rfpTitle, onClose }) {
  const [proposal, setProposal] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    rfpApi.generateProposal(rfpId)
      .then(r => setProposal(r.data.proposal))
      .catch(() => setError('Failed to generate proposal. Please try again.'))
      .finally(() => setLoading(false))
  }, [rfpId])

  const copy = () => {
    navigator.clipboard.writeText(proposal)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const download = () => {
    const blob = new Blob([proposal], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `proposal-${rfpTitle.slice(0, 40).replace(/\s+/g, '-').toLowerCase()}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  const saveAsDraft = async () => {
    setSaving(true)
    try {
      await applicationApi.create(rfpId, { proposal_text: proposal, status: 'draft' })
      setSaved(true)
    } catch { /* ignore */ } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="font-bold text-gray-900">AI-Generated Proposal</h2>
            <p className="text-xs text-gray-500 mt-0.5 truncate max-w-md">{rfpTitle}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {loading && (
            <div className="flex items-center gap-3 text-gray-500">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              Generating proposal with AI...
            </div>
          )}
          {error && <p className="text-red-600 text-sm">{error}</p>}
          {proposal && (
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono leading-relaxed">
              {proposal}
            </pre>
          )}
        </div>

        {proposal && (
          <div className="flex gap-3 p-6 border-t">
            <button onClick={copy}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium">
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={download}
              className="px-4 py-2 bg-[#1B4F8A] text-white hover:bg-blue-800 rounded-lg text-sm font-medium">
              Download .md
            </button>
            <button onClick={saveAsDraft} disabled={saving || saved}
              className="px-4 py-2 bg-emerald-600 text-white hover:bg-emerald-700 rounded-lg text-sm font-medium disabled:opacity-50">
              {saved ? 'Saved!' : saving ? 'Saving...' : 'Save as Draft'}
            </button>
            <button onClick={onClose}
              className="ml-auto px-4 py-2 text-gray-500 hover:text-gray-700 text-sm">
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default function RfpDetailPage() {
  const { id } = useParams()
  const [rfp, setRfp] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showProposal, setShowProposal] = useState(false)
  const [showWinRoom, setShowWinRoom] = useState(false)
  const [explanation, setExplanation] = useState(null)
  const isPharmacist = getRole() === 'pharmacist'

  useEffect(() => {
    rfpApi.detail(id)
      .then(r => setRfp(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
    if (isPharmacist) {
      matchApi.explanation(id).then(r => setExplanation(r.data)).catch(() => {})
    }
  }, [id])

  if (loading) return <p className="text-gray-400">Loading...</p>
  if (!rfp) return <p className="text-red-500">RFP not found.</p>

  return (
    <div className="max-w-4xl space-y-6">
      <Link to="/rfps" className="text-sm text-blue-600 hover:underline">Back to RFPs</Link>

      {isPharmacist && explanation?.explanation && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex gap-3">
          <span className="text-blue-600 font-bold">Why this matched</span>
          <p className="text-sm text-blue-900 flex-1">{explanation.explanation}</p>
        </div>
      )}

      <div className="bg-white rounded-xl border p-6 space-y-4">
        <div className="flex items-start justify-between">
          <h1 className="text-xl font-bold text-gray-900 flex-1 mr-4">{rfp.title}</h1>
          <StatusBadge status={rfp.status} deadline={rfp.deadline} />
        </div>

        {rfp.organization && (
          <div className="text-sm">
            <span className="font-medium text-gray-700">Organization: </span>
            <span className="text-gray-600">{rfp.organization.name}</span>
            {rfp.organization.type && (
              <span className="ml-2 px-2 py-0.5 bg-gray-100 rounded text-xs">{rfp.organization.type}</span>
            )}
          </div>
        )}

        {rfp.location && (
          <div className="text-sm">
            <span className="font-medium text-gray-700">Location: </span>
            <span className="text-gray-600">{rfp.location.name}</span>
          </div>
        )}

        <div className="flex flex-wrap gap-1">
          {rfp.categories?.map(cat => (
            <span key={cat} className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">{cat}</span>
          ))}
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {rfp.deadline && (
            <div>
              <span className="text-gray-500 block">Deadline</span>
              <span className="font-medium">{rfp.deadline}</span>
            </div>
          )}
          {rfp.posted_date && (
            <div>
              <span className="text-gray-500 block">Posted</span>
              <span className="font-medium">{rfp.posted_date}</span>
            </div>
          )}
          {rfp.source_url && (
            <div>
              <span className="text-gray-500 block">Source</span>
              <a href={rfp.source_url} target="_blank" rel="noopener noreferrer"
                className="font-medium text-blue-600 hover:underline">
                {sourceLabel(rfp)}
              </a>
            </div>
          )}
          {rfp.budget_range && (
            <div>
              <span className="text-gray-500 block">Budget</span>
              <span className="font-medium">{rfp.budget_range}</span>
            </div>
          )}
          {rfp.contact_name && (
            <div>
              <span className="text-gray-500 block">Contact</span>
              <span className="font-medium">{rfp.contact_name}</span>
              {rfp.contact_email && (
                <a href={`mailto:${rfp.contact_email}`} className="block text-blue-600 text-xs">{rfp.contact_email}</a>
              )}
            </div>
          )}
        </div>

        <div>
          <h2 className="font-semibold text-gray-800 mb-2">Description</h2>
          <p className="text-sm text-gray-600 leading-relaxed">{rfp.description}</p>
        </div>

        {rfp.requirements?.length > 0 && (
          <div>
            <h2 className="font-semibold text-gray-800 mb-2">Requirements</h2>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
              {rfp.requirements.map((req, i) => <li key={i}>{req}</li>)}
            </ul>
          </div>
        )}

        <div className="flex gap-3 flex-wrap">
          {rfp.url && (
            <a href={rfp.url} target="_blank" rel="noopener noreferrer"
              className="inline-block bg-[#1B4F8A] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-800">
              View Original RFP
            </a>
          )}
          {isPharmacist && (
            <button onClick={() => setShowProposal(true)}
              className="inline-block bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700">
              Generate Proposal
            </button>
          )}
          {isPharmacist && (
            <button onClick={() => setShowWinRoom(true)}
              className="inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700">
              Open Win Room
            </button>
          )}
        </div>
      </div>

      {isPharmacist && <SimulatorPanel rfpId={id} />}

      {isPharmacist && <CoalitionPanel rfpId={id} />}

      {rfp.similar_rfps?.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Similar RFPs</h2>
          <div className="space-y-2">
            {rfp.similar_rfps.map(s => (
              <Link key={s.id} to={`/rfps/${s.id}`}
                className="block bg-white rounded-lg border p-4 hover:shadow-sm transition">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{s.title}</h3>
                    <p className="text-xs text-gray-500">{s.organization_name} - {s.location}</p>
                  </div>
                  {s.deadline && <span className="text-xs text-gray-400">Due: {s.deadline}</span>}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {showProposal && (
        <ProposalModal
          rfpId={id}
          rfpTitle={rfp.title}
          onClose={() => setShowProposal(false)}
        />
      )}

      {showWinRoom && (
        <WinRoomModal
          rfpId={id}
          rfpTitle={rfp.title}
          onClose={() => setShowWinRoom(false)}
        />
      )}
    </div>
  )
}
