import { useState, useRef, useEffect } from 'react'
import { copilotApi } from '../api/client'

const SUGGESTIONS = [
  'Which RFPs are likely to be posted in the next 6 months?',
  'Find me an oncology specialty pharmacy RFP and build a coalition for it',
  'How can I improve my win probability for the 340B compliance RFP?',
  'Show me open MTM and Medicare RFPs',
]

function ToolStep({ step }) {
  const count = step.result?.items?.length ?? step.result?.team?.length
  return (
    <div className="border-l-2 border-indigo-300 pl-3 py-1">
      <span className="text-xs font-mono text-indigo-600">{step.tool}</span>
      {step.args && Object.keys(step.args).length > 0 && (
        <span className="text-xs text-gray-400 ml-2">
          {Object.entries(step.args).map(([k, v]) => `${k}=${JSON.stringify(v)}`).join(', ')}
        </span>
      )}
      {count != null && <span className="text-xs text-gray-400 ml-2">→ {count} result(s)</span>}
    </div>
  )
}

function Message({ m }) {
  if (m.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-[#1B4F8A] text-white rounded-2xl rounded-br-sm px-4 py-2 max-w-lg text-sm">
          {m.content}
        </div>
      </div>
    )
  }
  return (
    <div className="flex justify-start">
      <div className="bg-white border rounded-2xl rounded-bl-sm px-4 py-3 max-w-2xl">
        {m.steps?.length > 0 && (
          <div className="mb-3 space-y-1">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Reasoning</p>
            {m.steps.map((s, i) => <ToolStep key={i} step={s} />)}
          </div>
        )}
        <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">{m.content}</p>
        {m.used_llm === false && (
          <p className="text-[10px] text-gray-300 mt-2">offline mode</p>
        )}
      </div>
    </div>
  )
}

export default function CopilotPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])

  const send = async (text) => {
    const q = (text ?? input).trim()
    if (!q || loading) return
    setMessages(prev => [...prev, { role: 'user', content: q }])
    setInput('')
    setLoading(true)
    try {
      const r = await copilotApi.chat(q)
      setMessages(prev => [...prev, {
        role: 'assistant', content: r.data.answer,
        steps: r.data.steps, used_llm: r.data.used_llm,
      }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-full">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900">RFP Copilot</h1>
        <p className="text-sm text-gray-500 mt-1">
          Ask about upcoming RFPs, build coalitions, or simulate your win odds — it plans and acts across the knowledge graph.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-4">
            {SUGGESTIONS.map(s => (
              <button key={s} onClick={() => send(s)}
                className="text-left text-sm text-gray-600 border border-gray-200 rounded-xl px-4 py-3 hover:border-indigo-400 hover:bg-indigo-50 transition">
                {s}
              </button>
            ))}
          </div>
        )}
        {messages.map((m, i) => <Message key={i} m={m} />)}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border rounded-2xl px-4 py-3 text-sm text-gray-400">
              Thinking and acting...
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={e => { e.preventDefault(); send() }} className="flex gap-2 pt-3 border-t">
        <input value={input} onChange={e => setInput(e.target.value)}
          placeholder="Ask the Copilot..."
          className="flex-1 border rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        <button type="submit" disabled={loading}
          className="bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-50">
          Send
        </button>
      </form>
    </div>
  )
}
