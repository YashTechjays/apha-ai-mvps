import { useState, useCallback } from 'react'
import { leadApi } from '../api/client'

export function useLeadCapture(sessionId) {
  const [leadCaptured, setLeadCaptured] = useState(false)
  const [showModal, setShowModal] = useState(false)

  const captureLead = useCallback(async (email, name, extraData = {}) => {
    const res = await leadApi.capture({
      session_id: sessionId,
      email,
      name,
      ...extraData,
    })
    setLeadCaptured(true)
    setShowModal(false)
    return res.data
  }, [sessionId])

  return { leadCaptured, showModal, setShowModal, captureLead }
}
