import { Link, useLocation, useNavigate } from 'react-router-dom'

const NAV = [
  { path: '/outreach', label: 'Dashboard' },
  { path: '/outreach/prospects', label: 'Prospects' },
  { path: '/outreach/campaigns', label: 'Campaigns' },
]

export default function Layout({ children }) {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-56 bg-[#1B4F8A] text-white flex flex-col">
        <div className="p-5 border-b border-blue-700">
          <div className="text-xs font-semibold text-blue-300 uppercase tracking-widest mb-1">APhA</div>
          <div className="font-bold text-lg">Outreach Automation</div>
          <div className="text-xs text-blue-300 mt-0.5">by Techjays</div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map(({ path, label }) => (
            <Link key={path} to={path}
              className={`flex items-center px-3 py-2 rounded-lg text-sm transition ${pathname === path ? 'bg-blue-700 font-semibold' : 'hover:bg-blue-700/60'}`}>
              {label}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-blue-700">
          <button onClick={() => { localStorage.removeItem('outreach_token'); navigate('/outreach/login') }}
            className="text-xs text-blue-300 hover:text-white">Log out</button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-8">{children}</main>
    </div>
  )
}
