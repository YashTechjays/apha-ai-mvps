import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function LeadCaptureModal({ isOpen, hoursGap, totalCourses, onSubmit, onClose }) {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!email) return
    setLoading(true)
    await onSubmit(email, name)
    setLoading(false)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: 'rgba(0,0,0,0.5)' }}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8"
          >
            <div className="text-center mb-6">
              <div className="text-4xl mb-3">📋</div>
              <h2 className="text-xl font-display font-bold text-gray-900 mb-2">
                Your full {hoursGap}h plan is ready
              </h2>
              <p className="text-gray-500 text-sm">
                Enter your email to unlock all {totalCourses} recommended courses
                and get a copy sent to your inbox.
              </p>
            </div>
            <div className="space-y-3 mb-5">
              <input type="text" placeholder="Your name (optional)" value={name}
                onChange={e => setName(e.target.value)}
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue" />
              <input type="email" placeholder="Your email address" value={email}
                onChange={e => setEmail(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSubmit()}
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-apha-blue" />
            </div>
            <button onClick={handleSubmit} disabled={!email || loading}
              className="w-full bg-apha-blue text-white py-3 rounded-xl font-semibold hover:bg-apha-dark transition disabled:opacity-50 mb-3">
              {loading ? 'Unlocking...' : 'Unlock my full CPE plan →'}
            </button>
            <div className="text-center">
              <p className="text-xs text-gray-400">
                No spam. We'll send your plan + a reminder closer to your renewal date.
              </p>
              <button onClick={onClose} className="text-xs text-gray-400 hover:text-gray-600 mt-2 underline">
                Skip for now
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
