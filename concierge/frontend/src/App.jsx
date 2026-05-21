import { BrowserRouter, Routes, Route } from 'react-router-dom'
import DemoPage from './pages/DemoPage'
import AnalyticsDashboard from './pages/AnalyticsDashboard'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DemoPage />} />
        <Route path="/analytics" element={<AnalyticsDashboard />} />
      </Routes>
    </BrowserRouter>
  )
}
