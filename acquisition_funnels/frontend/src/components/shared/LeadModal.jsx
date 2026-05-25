import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const UNLOCK_MESSAGES = {
  salary: {
    title: 'Unlock your full salary report',
    body: 'Get your complete percentile breakdown, gap analysis, and a copy sent to your inbox.',
  },
  interactions: {
    title: 'Unlock unlimited checks',
    body: 'Get unlimited drug interaction checks today, plus your results saved for easy reference.',
  },
  career: {
    title: 'Unlock your 90-day action plan',
    body: 'Get your personalized action plan — 3 specific steps to close your biggest career gap.',
  },
}

export default function LeadModal({ isOpen, tool, onSubmit, onClose }) {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const msg = UNLOCK_MESSAGES[tool] || UNLOCK_MESSAGES.salary

  const handleSubmit = async () => {
    if (!email) return
    setLoading(true)
    await onSubmit(email, name)
    setLoading(false)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4"
          style={{ background: 'rgba(0,0,0,0.6)' }}
        >
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 40 }}
            className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8"
          >
            <div className="text-center mb-6">
              <h2 className="text-xl font-display font-bold text-gray-900 mb-2">
                {msg.title}
              </h2>
              <p className="text-gray-500 text-sm">{msg.body}</p>
            </div>
            <div className="space-y-3 mb-5">
              <input
                type="text"
                placeholder="Your name (optional)"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue"
              />
              <input
                type="email"
                placeholder="Your email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && email && handleSubmit()}
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue"
              />
            </div>
            <button
              onClick={handleSubmit}
              disabled={!email || loading}
              className="w-full bg-apha-blue text-white py-3 rounded-xl font-semibold hover:bg-apha-dark transition disabled:opacity-50 mb-3"
            >
              {loading ? 'Unlocking...' : 'Unlock my full report'}
            </button>
            <div className="text-center">
              <p className="text-xs text-gray-400">
                No spam. Just your report + occasional APhA updates.
              </p>
              <button
                onClick={onClose}
                className="text-xs text-gray-400 hover:text-gray-600 mt-2 underline"
              >
                Skip for now
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
