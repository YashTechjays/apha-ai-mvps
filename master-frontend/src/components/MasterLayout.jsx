import { NavLink, useLocation } from 'react-router-dom'
import { useState } from 'react'

const MVPS = [
  {
    path: '/churn',
    label: 'Churn Prediction',
    icon: '📉',
    desc: 'ML risk scoring',
    summary: 'ML-powered system that predicts which APhA members are likely to cancel their membership, so the retention team can intervene before it happens.',
    kpis: [
      { name: 'Critical Risk (85-100)', meaning: 'Members almost certain to churn — need immediate personal outreach (phone call, special offer)' },
      { name: 'High Risk (70-84)', meaning: 'Members showing strong churn signals — trigger automated retention campaigns' },
      { name: 'Medium Risk (50-69)', meaning: 'Members disengaging — send re-engagement emails highlighting unused benefits' },
      { name: 'Low Risk (0-49)', meaning: 'Healthy members — maintain regular engagement, no intervention needed' },
    ],
    features: [
      'Risk Distribution — visual breakdown of all members across 4 risk tiers',
      'Recent Alerts — real-time notifications when members cross risk thresholds',
      'Run Scoring — on-demand ML scoring across all 200+ members using XGBoost model',
      'Member Details — drill into individual member engagement data and risk factors',
    ],
    revenue: [
      'Prevents revenue loss — each saved member = $195/yr retained. Saving 5% of 63,000 members = $614K/yr',
      'Prioritizes retention spend — focus expensive outreach (phone calls) only on Critical/High risk members',
      'Early warning system — catches disengagement 60-90 days before renewal date, giving time to act',
      'Data-driven decisions — replaces gut-feel retention with ML-powered scoring using 25+ engagement signals',
    ],
  },
  {
    path: '/concierge',
    label: 'AI Concierge',
    icon: '💬',
    desc: 'Chat assistant',
    summary: 'AI-powered chatbot that sits on pharmacist.com to answer visitor questions about membership, CPE, events, and benefits — converting website visitors into paying members 24/7.',
    kpis: [
      { name: 'Chat Widget', meaning: 'RAG-powered chatbot with 21 knowledge chunks (membership tiers, CPE programs, renewal FAQs, benefits)' },
      { name: 'Lead Capture', meaning: 'After a few conversation turns, captures visitor name/email/interest as a CRM lead' },
      { name: 'Tier Guidance', meaning: 'Helps visitors choose between Student ($50), Pharmacist ($195), and Technician ($75) tiers' },
    ],
    features: [
      'RAG retrieval from APhA knowledge base — membership_benefits.md, cpe_programs.md, renewal_faq.md, etc.',
      'Automatic lead capture after 3 conversation turns',
      'Analytics dashboard at /analytics — tracks conversations, leads, popular questions',
      'CRM integration ready (HubSpot/Personify) — currently mocked, waiting for API keys',
    ],
    revenue: [
      'Converts more website visitors into members — instant answers vs. bouncing to competitor sites',
      'Reduces support staff workload — AI handles common questions 24/7 at zero marginal cost',
      'Captures leads automatically — no more lost prospects who browse and leave',
      'Guides visitors to the right tier — increases sign-up confidence and reduces decision paralysis',
    ],
  },
  {
    path: '/cpe',
    label: 'CPE Calculator',
    icon: '🧮',
    desc: 'Gap analysis',
    summary: 'Free tool that calculates a pharmacist\'s CPE (Continuing Pharmacy Education) gap based on their state requirements, and generates a personalized study plan using APhA courses.',
    kpis: [
      { name: 'License State', meaning: 'Each state has different CPE requirements (hours, topics, cycle length)' },
      { name: 'License Type', meaning: 'Pharmacist (RPh/PharmD) vs Technician — different hour requirements' },
      { name: 'Renewal Date', meaning: 'Calculates urgency — how many days/weeks until license expires' },
      { name: 'CPE Gap', meaning: 'Exactly how many hours and which topic areas still need to be completed' },
    ],
    features: [
      'Step 1: Your Info — enter state, license type, renewal date, hours completed, specialty',
      'Step 2: Your Plan — AI generates personalized study plan with specific APhA courses',
      'Step 3: Full Access — conversion gate: join APhA or provide email for detailed plan',
      'SEO landing pages for each state (e.g., "California Pharmacist CPE Requirements 2026")',
    ],
    revenue: [
      'Lead generation machine — every user gives APhA their state, license type, specialty, renewal date (high-intent data)',
      'Direct course sales — personalized plan recommends APhA\'s own CPE courses ($$$)',
      'Membership conversion — shows non-member vs. member pricing ("Join for $195/yr, save $400 on CPE")',
      'Urgency-driven action — "Your renewal is in 60 days, you\'re 15 hours short" drives immediate purchases',
    ],
  },
  {
    path: '/crosssell',
    label: 'Cross-Sell',
    icon: '🎯',
    desc: 'Expansion engine',
    summary: 'AI engine that scores each member\'s likelihood to purchase additional APhA products across 5 streams (education, publications, events, career, advocacy), then triggers personalized nudges.',
    kpis: [
      { name: 'Expansion Scores', meaning: 'Per-member scores (0-100) across 5 product streams showing purchase likelihood' },
      { name: 'Nudge Engine', meaning: 'Automated personalized emails/messages triggered when expansion score exceeds threshold' },
      { name: 'Conversion Tracking', meaning: 'Tracks which nudges led to actual purchases — measures ROI of cross-sell campaigns' },
      { name: 'Product Affinity', meaning: 'Shows which products each member is most likely to buy based on behavior patterns' },
    ],
    features: [
      'ML scoring across 5 product streams: education, publications, events, career, advocacy',
      'Automated nudge campaigns with cooldown logic (max 2 nudges/member/month)',
      'Member detail pages with engagement data and cross-sell opportunity scores',
      'Analytics dashboard with conversion rates and revenue attribution',
    ],
    revenue: [
      'Increases ARPU (Average Revenue Per User) — members buy more products beyond basic membership',
      'Data-driven upselling — replaces "blast everyone" emails with targeted, high-probability nudges',
      'Identifies hidden opportunities — surfaces members likely to buy events/publications they haven\'t discovered',
      'Measurable ROI — tracks nudge-to-purchase conversion, proving campaign value to leadership',
    ],
  },
  {
    path: '/drug-ref',
    label: 'Drug Reference',
    icon: '💊',
    desc: 'Clinical Q&A',
    summary: 'AI-powered clinical drug reference tool that pharmacists can query for drug interactions, dosing, contraindications — positioned as a subscription SaaS product generating recurring revenue.',
    kpis: [
      { name: 'Query Interface', meaning: 'Natural language clinical queries ("What are the interactions between warfarin and amiodarone?")' },
      { name: 'Subscription Tiers', meaning: 'Individual ($29/mo), Team ($99/mo), Institution ($299/mo), Enterprise (custom) — recurring revenue' },
      { name: 'API Keys', meaning: 'Developers/institutions can integrate drug reference into their own systems via API' },
      { name: 'Usage Analytics', meaning: 'Tracks queries per user, popular drug lookups, API usage against rate limits' },
    ],
    features: [
      'RAG-powered answers from curated drug content (ChromaDB vector store)',
      'Rate-limited API access per subscription tier',
      'Stripe integration for subscription billing (currently mocked)',
      'Organization management — team admins can manage seats and API keys',
    ],
    revenue: [
      'New recurring revenue stream — subscription SaaS product independent of membership dues',
      'Scales to institutions — hospitals and pharmacy chains pay $299+/mo for team/institution access',
      'API monetization — third-party EHR/pharmacy systems pay for integration access',
      'Membership value-add — basic access included with APhA membership, driving sign-ups',
    ],
  },
  {
    path: '/email',
    label: 'Value Emails',
    icon: '📧',
    desc: 'Personalized emails',
    summary: 'Personalized member value email system. Every month, generates a unique email for each member showing exactly how much dollar value they\'ve gotten from their membership — CPE courses, journals, events.',
    kpis: [
      { name: 'Total Sends', meaning: 'Number of personalized emails sent this month — more sends = more members reminded of value' },
      { name: 'Open Rate', meaning: '% of members who opened the email (industry avg ~20%). Higher = better subject lines & personalization' },
      { name: 'Avg Benefit Value', meaning: 'Average dollar value of benefits each member used (e.g., "$847 in CPE, journals"). ROI multiplier makes it visceral' },
      { name: 'Total Value Delivered', meaning: 'Sum of all benefit value across all members — proves program impact to leadership' },
    ],
    features: [
      'Dry Run — generates all emails without sending, for QC preview',
      'Send Batch — sends personalized emails to all members via Postmark SMTP',
      'QC & Personalization Scores — AI quality checks ensure accuracy and personalization',
      'Email Status Breakdown — tracks sent, QC passed/failed, delivery failures',
      'Members table — 200 members with CPE credits, webinars, portal sessions, open rates',
    ],
    revenue: [
      'Reduces churn — members who see "$847 value from $195 membership" are far more likely to renew (15-25% improvement)',
      'Recovers at-risk members — highlights unused benefits to re-engage before they lapse',
      'Quantifies ROI for leadership — "We delivered $X million in member value this quarter"',
      'Upsell opportunity — emails highlight premium benefits the member hasn\'t tried yet',
    ],
  },
  {
    path: '/acquisition',
    label: 'Acquisition Funnels',
    icon: '🚀',
    desc: 'Lead generation tools',
    summary: 'Suite of free public tools (salary calculator, interaction checker, career assessment) designed to attract non-member pharmacists and convert them into APhA members through value-first engagement.',
    kpis: [
      { name: 'Salary Calculator', meaning: 'Free tool: "What should a pharmacist in [state] with [years] experience earn?" Captures leads from job-seeking pharmacists' },
      { name: 'Interaction Checker', meaning: 'Free drug interaction lookup — demonstrates APhA\'s clinical value, captures healthcare professional leads' },
      { name: 'Career Assessment', meaning: 'AI-powered career path assessment for pharmacy professionals — captures career-stage data for targeting' },
      { name: 'Lead Analytics', meaning: 'Tracks funnel metrics: tool usage, email captures, conversion to membership' },
    ],
    features: [
      'Rate-limited free usage (3 salary checks/day, 3 interaction checks/day, 1 career assessment/day)',
      'Email gate after free limit — "Get unlimited access with APhA membership"',
      'Lead scoring based on engagement depth and professional profile',
      'SEO-optimized landing pages for organic traffic acquisition',
    ],
    revenue: [
      'Top-of-funnel lead generation — attracts non-members with free tools they actually need',
      'Captures high-intent professional data — state, specialty, career stage, salary expectations',
      'Converts free users to members — "You used $X worth of tools this month. Join for unlimited access at $195/yr"',
      'Low CAC (Customer Acquisition Cost) — organic/SEO traffic vs. expensive paid ads',
    ],
  },
  {
    path: '/outreach',
    label: 'Outreach Automation',
    icon: '📡',
    desc: 'AI prospect outreach',
    summary: 'AI-powered outreach system that identifies non-member pharmacists via NPI registry, scores them with an Ideal Customer Profile (ICP), and runs automated email sequences to convert them into members.',
    kpis: [
      { name: 'Prospects', meaning: 'Non-member pharmacists imported from NPI registry, scored by ICP fit (location, specialty, practice setting)' },
      { name: 'Campaigns', meaning: 'Multi-step email sequences (e.g., 5-email drip over 3 weeks) with AI-personalized content' },
      { name: 'Send Analytics', meaning: 'Tracks opens, clicks, replies, unsubscribes per campaign — measures outreach effectiveness' },
      { name: 'Suppression List', meaning: 'Manages unsubscribes and do-not-contact lists for CAN-SPAM compliance' },
    ],
    features: [
      'NPI registry import — bulk import of licensed pharmacists with mock data (500 prospects seeded)',
      'ICP scoring — ranks prospects by likelihood to join based on demographics and practice type',
      'AI email generation — personalized outreach emails crafted per prospect profile',
      'Send window controls — respects business hours, rate limits (200/hr, 2000/day)',
    ],
    revenue: [
      'Scales member acquisition — automates outreach to thousands of non-member pharmacists',
      'AI personalization at scale — each prospect gets a tailored message, not a generic blast',
      'Measurable pipeline — tracks prospect-to-member conversion rates and cost per acquisition',
      'Compounds over time — builds a growing database of engaged prospects for future campaigns',
    ],
  },
]

export default function MasterLayout({ children }) {
  const { pathname } = useLocation()
  const [openDetail, setOpenDetail] = useState(null)

  if (pathname === '/') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <header className="bg-[#1B4F8A] text-white px-8 py-6 shadow-lg">
          <h1 className="text-2xl font-bold">APhA AI Platform</h1>
          <p className="text-blue-200 text-sm mt-1">8 MVPs — Unified Dashboard</p>
        </header>
        <main className="max-w-5xl mx-auto py-12 px-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {MVPS.map(({ path, label, icon, desc }, idx) => (
              <div key={path} className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all border border-gray-100 hover:border-blue-300 group">
                <NavLink to={path} className="block p-6 pb-3">
                  <div className="text-3xl mb-3">{icon}</div>
                  <h2 className="text-lg font-bold text-gray-800 group-hover:text-[#1B4F8A] transition-colors">{label}</h2>
                  <p className="text-sm text-gray-500 mt-1">{desc}</p>
                </NavLink>
                <div className="px-6 pb-4">
                  <button
                    onClick={(e) => { e.preventDefault(); setOpenDetail(openDetail === idx ? null : idx) }}
                    className="text-xs text-[#1B4F8A] font-semibold hover:underline cursor-pointer"
                  >
                    {openDetail === idx ? 'Hide Details ▲' : 'View Details ▼'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </main>

        {/* Detail Modal */}
        {openDetail !== null && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-12 px-4 overflow-y-auto" onClick={() => setOpenDetail(null)}>
            <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full mb-12" onClick={e => e.stopPropagation()}>
              <div className="bg-[#1B4F8A] text-white px-8 py-5 rounded-t-2xl flex items-center justify-between">
                <div>
                  <span className="text-2xl mr-3">{MVPS[openDetail].icon}</span>
                  <span className="text-xl font-bold">{MVPS[openDetail].label}</span>
                </div>
                <button onClick={() => setOpenDetail(null)} className="text-white/80 hover:text-white text-2xl leading-none">&times;</button>
              </div>

              <div className="p-8 space-y-6">
                {/* Summary */}
                <div>
                  <h3 className="text-sm font-semibold text-[#1B4F8A] uppercase tracking-wide mb-2">What This MVP Does</h3>
                  <p className="text-gray-700 leading-relaxed">{MVPS[openDetail].summary}</p>
                </div>

                {/* KPIs */}
                <div>
                  <h3 className="text-sm font-semibold text-[#1B4F8A] uppercase tracking-wide mb-3">Key Metrics & KPIs</h3>
                  <div className="space-y-3">
                    {MVPS[openDetail].kpis.map(({ name, meaning }) => (
                      <div key={name} className="flex gap-3 items-start">
                        <span className="bg-blue-50 text-[#1B4F8A] text-xs font-bold px-3 py-1 rounded-full whitespace-nowrap mt-0.5">{name}</span>
                        <span className="text-sm text-gray-600">{meaning}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Features */}
                <div>
                  <h3 className="text-sm font-semibold text-[#1B4F8A] uppercase tracking-wide mb-3">Features</h3>
                  <ul className="space-y-2">
                    {MVPS[openDetail].features.map((f, i) => (
                      <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-[#1B4F8A] mt-1">•</span>
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Revenue Impact */}
                <div>
                  <h3 className="text-sm font-semibold text-green-700 uppercase tracking-wide mb-3">How This Drives Revenue for APhA</h3>
                  <div className="bg-green-50 border border-green-200 rounded-xl p-5 space-y-3">
                    {MVPS[openDetail].revenue.map((r, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm text-green-800">
                        <span className="font-bold text-green-600 mt-0.5">{i + 1}.</span>
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Open MVP button */}
                <div className="pt-2">
                  <NavLink to={MVPS[openDetail].path}
                    className="inline-block bg-[#1B4F8A] text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-blue-800 transition text-sm">
                    Open {MVPS[openDetail].label} →
                  </NavLink>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }

  return <>{children}</>
}
