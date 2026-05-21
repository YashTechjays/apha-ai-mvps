import { useState } from 'react'

export default function LeadCaptureForm({ onSubmit, onSkip }) {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 mt-2">
      <div className="text-sm font-semibold text-[#1B4F8A] mb-2">
        Want us to send you more info?
      </div>
      <input
        type="text"
        placeholder="Your name (optional)"
        value={name}
        onChange={e => setName(e.target.value)}
        className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
      <input
        type="email"
        placeholder="Your email address"
        value={email}
        onChange={e => setEmail(e.target.value)}
        className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
      />
      <div className="flex gap-2">
        <button
          onClick={() => email && onSubmit(email, name)}
          disabled={!email}
          className="flex-1 bg-[#1B4F8A] text-white text-sm py-1.5 rounded-lg font-semibold hover:bg-blue-800 transition disabled:opacity-50"
        >
          Send me info
        </button>
        <button onClick={onSkip} className="text-xs text-gray-400 hover:text-gray-600 px-2">
          Skip
        </button>
      </div>
    </div>
  )
}
