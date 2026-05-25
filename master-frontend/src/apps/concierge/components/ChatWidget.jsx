import { useState, useRef, useEffect } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { chatApi, leadApi } from '../api/client'
import ChatMessage from './ChatMessage'
import TypingIndicator from './TypingIndicator'
import TierCard from './TierCard'
import LeadCaptureForm from './LeadCaptureForm'

const GREETING = "Hi there! 👋 I'm the APhA Membership Concierge. Are you looking to join APhA, renew your membership, or do you have a question about what we offer?"

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([{ role: 'assistant', content: GREETING }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionToken] = useState(() => uuidv4())
  const [tierRec, setTierRec] = useState(null)
  const [showLeadForm, setShowLeadForm] = useState(false)
  const [leadCaptured, setLeadCaptured] = useState(false)
  const [joinUrl, setJoinUrl] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)
    try {
      const res = await chatApi.sendMessage(sessionToken, userMsg, window.location.href)
      const data = res.data
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
      if (data.tier_recommendation) setTierRec(data.tier_recommendation)
      if (data.should_capture_lead && !leadCaptured) setShowLeadForm(true)
      if (data.join_url) setJoinUrl(data.join_url)
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Sorry, I'm having a brief technical issue. Please try again in a moment.",
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleLeadSubmit = async (email, name) => {
    await leadApi.captureLead(sessionToken, email, name, tierRec)
    setLeadCaptured(true)
    setShowLeadForm(false)
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: `Thanks, ${name || 'there'}! We'll send some info to ${email}. Is there anything else I can help you with?`,
    }])
  }

  return (
    <>
      {/* Floating Button */}
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-[#1B4F8A] text-white rounded-full shadow-lg flex items-center justify-center text-2xl hover:bg-blue-800 transition z-50"
          title="Chat with APhA Membership Concierge"
        >
          💬
        </button>
      )}

      {/* Chat Panel */}
      {open && (
        <div className="fixed bottom-6 right-6 w-96 h-[580px] bg-gray-50 rounded-2xl shadow-2xl flex flex-col z-50 border border-gray-200">
          {/* Header */}
          <div className="bg-[#1B4F8A] text-white rounded-t-2xl px-4 py-3 flex items-center justify-between">
            <div>
              <div className="font-bold text-sm">APhA Membership Concierge</div>
              <div className="text-xs text-blue-200">Powered by AI · pharmacist.com</div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-white/70 hover:text-white text-xl leading-none"
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((m, i) => <ChatMessage key={i} role={m.role} content={m.content} />)}
            {loading && <TypingIndicator />}
            {tierRec && !loading && (
              <TierCard
                tier={tierRec}
                onJoinClick={() => window.open(joinUrl || 'https://pharmacist.com/join', '_blank')}
              />
            )}
            {showLeadForm && (
              <LeadCaptureForm
                onSubmit={handleLeadSubmit}
                onSkip={() => setShowLeadForm(false)}
              />
            )}
            {joinUrl && !showLeadForm && !loading && (
              <div className="text-center">
                <a
                  href={joinUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block bg-green-600 text-white text-sm px-5 py-2 rounded-full font-semibold hover:bg-green-700 transition"
                >
                  → Go to Join / Renew Page
                </a>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t bg-white rounded-b-2xl">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder="Ask me anything about APhA membership..."
                className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="bg-[#1B4F8A] text-white px-4 py-2 rounded-full text-sm font-semibold hover:bg-blue-800 transition disabled:opacity-50"
              >
                Send
              </button>
            </div>
            <div className="text-center text-xs text-gray-400 mt-1.5">
              AI-powered · Built by Techjays for APhA
            </div>
          </div>
        </div>
      )}
    </>
  )
}
