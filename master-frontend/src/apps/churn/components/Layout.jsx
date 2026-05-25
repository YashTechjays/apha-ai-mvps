import { Link, useLocation, useNavigate } from 'react-router-dom'

const NAV = [
  { path: '/churn', label: 'Dashboard' },
  { path: '/churn/members', label: 'Members' },
]

export default function Layout({ children }) {
  const { pathname } = useLocation()
  const navigate = useNavigate()

  const logout = () => {
    localStorage.removeItem('churn_token')
    navigate('/churn/login')
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-56 bg-[#1B4F8A] text-white flex flex-col">
        <div className="p-5 border-b border-blue-700">
          <div className="text-xs font-semibold text-blue-300 uppercase tracking-widest mb-1">APhA</div>
          <div className="font-bold text-lg leading-tight">Churn Prediction</div>
          <div className="text-xs text-blue-300 mt-0.5">by Techjays</div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map(({ path, label }) => (
            <Link
              key={path}
              to={path}
              className={`flex items-center px-3 py-2 rounded-lg text-sm transition-colors ${
                pathname === path ? 'bg-blue-700 font-semibold' : 'hover:bg-blue-700/60'
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-blue-700">
          <button onClick={logout} className="text-xs text-blue-300 hover:text-white w-full text-left">
            Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  )
}
