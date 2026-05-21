import { BrowserRouter, Routes, Route } from 'react-router-dom'
import CalculatorPage from './pages/CalculatorPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CalculatorPage />} />
        <Route path="/state/:stateCode" element={<CalculatorPage />} />
      </Routes>
    </BrowserRouter>
  )
}
