import { Link } from 'react-router-dom'

export default function APhAHeader({ activeTool }) {
  const tools = [
    { path: '/acquisition/salary', label: 'Salary Check', id: 'salary' },
    { path: '/acquisition/interactions', label: 'Drug Interactions', id: 'interactions' },
    { path: '/acquisition/career', label: 'Career Score', id: 'career' },
  ]

  return (
    <header className="bg-apha-blue text-white">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/acquisition">
          <div className="text-xs text-blue-200 font-semibold uppercase tracking-widest">
            American Pharmacists Association
          </div>
          <div className="font-display text-lg font-bold">Free Tools for Pharmacists</div>
        </Link>
        <a
          href="https://pharmacist.com/join"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs bg-white text-apha-blue px-4 py-1.5 rounded-lg font-semibold hover:bg-blue-50 transition hidden sm:block"
        >
          Join APhA
        </a>
      </div>
      <div className="border-t border-blue-700 max-w-5xl mx-auto px-4">
        <nav className="flex gap-1">
          {tools.map((t) => (
            <Link
              key={t.id}
              to={t.path}
              className={`text-sm px-4 py-2.5 font-medium transition border-b-2 ${
                activeTool === t.id
                  ? 'border-white text-white'
                  : 'border-transparent text-blue-200 hover:text-white hover:border-blue-400'
              }`}
            >
              {t.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  )
}
