const UPSELL_CONTENT = {
  salary: {
    headline: 'APhA members earn 8% more on average',
    body: 'CPE access, credentials, and a professional network that signals value to employers.',
    cta: 'Join APhA — boost your earning potential',
  },
  interactions: {
    headline: 'Get unlimited drug interaction checks',
    body: 'Plus 300+ CPE hours, PharmacyLibrary access, and clinical guidelines — all in one membership.',
    cta: 'Join APhA for unlimited access',
  },
  career: {
    headline: 'APhA has resources for every gap in your plan',
    body: 'Certificates, mentorship, advocacy tools, and a national network — one membership covers it all.',
    cta: 'Join APhA — start your 90-day plan',
  },
}

export default function MemberUpsell({ tool }) {
  const content = UPSELL_CONTENT[tool] || UPSELL_CONTENT.salary

  return (
    <div className="bg-gradient-to-r from-apha-blue to-apha-dark text-white rounded-2xl p-6 mt-6">
      <div className="flex items-start gap-4">
        <div className="text-3xl shrink-0">&#127942;</div>
        <div className="flex-1">
          <h3 className="font-display text-lg font-bold mb-1">{content.headline}</h3>
          <p className="text-blue-100 text-sm mb-4">{content.body}</p>
          <a
            href={`https://pharmacist.com/join?utm_source=${tool}_tool`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center bg-white text-apha-blue px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-blue-50 transition"
          >
            {content.cta} &rarr;
          </a>
        </div>
      </div>
    </div>
  )
}
