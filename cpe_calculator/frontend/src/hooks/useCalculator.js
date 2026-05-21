import { useState } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { calculatorApi, leadApi } from '../api/client'

const SESSION_ID = uuidv4()

export function useCalculator() {
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [fullPlan, setFullPlan] = useState(null)
  const [leadCaptured, setLeadCaptured] = useState(false)
  const [showLeadModal, setShowLeadModal] = useState(false)

  const calculate = async (formData) => {
    setLoading(true)
    setError(null)
    try {
      const res = await calculatorApi.calculate({ ...formData, session_id: SESSION_ID })
      setResult(res.data)
      setStep(2)
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const captureLead = async (email, name) => {
    try {
      await leadApi.capture({
        session_id: SESSION_ID,
        email,
        name,
        calculation_id: result?.calculation_id,
      })
      setLeadCaptured(true)
      setShowLeadModal(false)
      const fullRes = await calculatorApi.getFullPlan(result.calculation_id, SESSION_ID)
      setFullPlan(fullRes.data)
      setStep(3)
    } catch (e) {
      console.error('Lead capture failed:', e)
    }
  }

  const reset = () => {
    setStep(1)
    setResult(null)
    setFullPlan(null)
    setLeadCaptured(false)
    setError(null)
  }

  return {
    step, loading, error, result, fullPlan, leadCaptured,
    showLeadModal, setShowLeadModal,
    calculate, captureLead, reset, sessionId: SESSION_ID,
  }
}
