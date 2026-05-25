import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import SalaryPage from './pages/SalaryPage'
import InteractionPage from './pages/InteractionPage'
import CareerPage from './pages/CareerPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/salary" element={<SalaryPage />} />
        <Route path="/interactions" element={<InteractionPage />} />
        <Route path="/career" element={<CareerPage />} />
      </Routes>
    </BrowserRouter>
  )
}
