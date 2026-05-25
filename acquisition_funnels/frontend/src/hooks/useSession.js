import { useState } from 'react'
import { v4 as uuidv4 } from 'uuid'

export function useSession() {
  const [sessionId] = useState(() => {
    const stored = sessionStorage.getItem('apha_session_id')
    if (stored) return stored
    const newId = uuidv4()
    sessionStorage.setItem('apha_session_id', newId)
    return newId
  })
  return sessionId
}
