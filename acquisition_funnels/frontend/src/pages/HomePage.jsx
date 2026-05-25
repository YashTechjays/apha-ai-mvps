import { Link } from 'react-router-dom'
import APhAHeader from '../components/shared/APhAHeader'

const TOOLS = [
  {
    id: 'salary',
    path: '/salary',
    title: 'Salary Benchmarker',
    desc: 'See where your salary stands vs. peers in your state and specialty.',
    cta: 'Check my salary',
    stat: '3 free checks | Updated 2025',
    color: 'border-blue-200 hover:border-blue-400',
    badge: 'Most popular',
  },
  {
    id: 'interactions',
    path: '/interactions',
    title: 'Drug Interaction Checker',
    desc: 'Check clinically significant drug interactions with AI-powered summaries.',
    cta: 'Check interactions',
    stat: '3 free checks/day | 100+ drug pairs',
    color: 'border-green-200 hover:border-green-400',
    badge: null,
  },
  {
    id: 'career',
    path: '/career',
    title: 'Career Readiness Scorer',
    desc: 'Score your career across 6 competency dimensions + get a personalized action plan.',
    cta: 'Score my career',
    stat: 'Free assessment | Takes 3 minutes',
    color: 'border-purple-200 hover:border-purple-400',
    badge: null,
  },
]

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50 font-body">
      <APhAHeader activeTool={null} />
      <main className="max-w-4xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="font-display text-4xl font-bold text-gray-900 mb-4">
            Free AI Tools for Pharmacists
          </h1>
          <p className="text-gray-500 text-lg max-w-xl mx-auto">
            Powered by APhA data and AI. No account required.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {TOOLS.map((t) => (
            <Link
              key={t.id}
              to={t.path}
              className={`bg-white border-2 rounded-2xl p-6 transition-all hover:shadow-lg group ${t.color}`}
            >
              {t.badge && (
                <div className="text-xs font-semibold text-apha-blue bg-blue-50 px-2.5 py-1 rounded-full inline-block mb-3">
                  {t.badge}
                </div>
              )}
              <h2 className="font-bold text-lg text-gray-900 mb-2 group-hover:text-apha-blue transition">
                {t.title}
              </h2>
              <p className="text-sm text-gray-500 mb-4 leading-relaxed">{t.desc}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">{t.stat}</span>
                <span className="text-sm text-apha-blue font-semibold group-hover:translate-x-1 transition">
                  {t.cta} &rarr;
                </span>
              </div>
            </Link>
          ))}
        </div>
        <div className="text-center mt-12 text-sm text-gray-400">
          All tools are free &middot; Powered by the American Pharmacists Association &middot;
          <a
            href="https://pharmacist.com/join"
            target="_blank"
            rel="noopener noreferrer"
            className="text-apha-blue hover:underline ml-1"
          >
            Join APhA for unlimited access &rarr;
          </a>
        </div>
      </main>
    </div>
  )
}
