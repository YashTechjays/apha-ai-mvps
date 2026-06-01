import { useState, useEffect, useRef } from 'react'
import { rfpApi } from '../api/client'

function ScoreDial({ score }) {
  const color = score >= 85 ? 'text-green-600' : score >= 65 ? 'text-yellow-600' : 'text-red-500'
  return (
    <div className="flex flex-col items-center">
      <span className={`text-5xl font-bold tabular-nums ${color}`}>{score}</span>
      <span className="text-xs text-gray-400 uppercase tracking-wide">/ 100</span>
    </div>
  )
}

function RoundRow({ r, active }) {
  return (
    <div className={`rounded-lg border p-3 transition ${active ? 'border-emerald-400 bg-emerald-50' : 'border-gray-200'}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-semibold text-gray-600">
          {r.round === 0 ? 'Initial draft' : `Revision ${r.round}`}
        </span>
        <span className="text-sm font-bold tabular-nums">{r.score}</span>
      </div>
      {r.verdict && <p className="text-xs text-gray-500">{r.verdict}</p>}
      {r.gaps?.length > 0 && (
        <ul className="mt-1 list-disc list-inside text-xs text-gray-500 space-y-0.5">
          {r.gaps.slice(0, 3).map((g, i) => <li key={i}>{g}</li>)}
        </ul>
      )}
    </div>
  )
}

export default function WinRoomModal({ rfpId, rfpTitle, onClose }) {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [displayScore, setDisplayScore] = useState(0)
  const [revealed, setRevealed] = useState(0)
  const timers = useRef([])

  useEffect(() => {
    rfpApi.winRoom(rfpId)
      .then(r => setResult(r.data))
      .catch(() => setError('Win Room failed. Please try again.'))
      .finally(() => setLoading(false))
    return () => timers.current.forEach(clearTimeout)
  }, [rfpId])

  // Animate rounds revealing one-by-one with the score climbing.
  useEffect(() => {
    if (!result?.rounds?.length) return
    result.rounds.forEach((round, i) => {
      const t = setTimeout(() => {
        setRevealed(i + 1)
        animateTo(round.score)
      }, i * 1400)
      timers.current.push(t)
    })
  }, [result])

  const animateTo = (target) => {
    setDisplayScore(prev => {
      const start = prev
      const steps = 20
      for (let s = 1; s <= steps; s++) {
        const t = setTimeout(() => {
          setDisplayScore(Math.round(start + (target - start) * (s / steps)))
        }, s * 30)
        timers.current.push(t)
      }
      return prev
    })
  }

  const finalProposal = result?.final_proposal
  const download = () => {
    const blob = new Blob([finalProposal], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `win-room-${rfpTitle.slice(0, 40).replace(/\s+/g, '-').toLowerCase()}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="font-bold text-gray-900">Win Room — AI Evaluation Committee</h2>
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
              The committee is reviewing and revising your proposal...
            </div>
          )}
          {error && <p className="text-red-600 text-sm">{error}</p>}

          {result && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="flex flex-col items-center justify-center gap-3 md:border-r md:pr-6">
                <ScoreDial score={displayScore} />
                {revealed >= result.rounds.length && (
                  <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">
                    +{result.improvement} points after review
                  </span>
                )}
              </div>
              <div className="md:col-span-2 space-y-2">
                {result.rounds.slice(0, revealed).map((r, i) => (
                  <RoundRow key={i} r={r} active={i === revealed - 1} />
                ))}
              </div>
            </div>
          )}
        </div>

        {result && (
          <div className="flex gap-3 p-6 border-t">
            <button onClick={download}
              className="px-4 py-2 bg-[#1B4F8A] text-white hover:bg-blue-800 rounded-lg text-sm font-medium">
              Download Final Proposal
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
