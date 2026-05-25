export default function MembershipUpsell({ savings, totalHours, joinUrl }) {
  return (
    <div className="bg-gradient-to-br from-apha-blue to-apha-dark rounded-2xl p-6 text-white mt-6">
      <div className="flex items-start gap-4">
        <div className="text-3xl">🎓</div>
        <div className="flex-1">
          <h3 className="font-display text-lg font-bold mb-1">
            Get all {totalHours} hours free with APhA membership
          </h3>
          <p className="text-blue-100 text-sm mb-4">
            Every course in your plan is included free with APhA membership —
            saving you <span className="font-bold text-white">${savings}</span> vs.
            buying individually. Plus 300+ more CPE hours, journals, career tools, and advocacy.
          </p>
          <div className="flex flex-wrap gap-2 mb-4">
            {['300+ CPE hours included', 'JAPhA journal access', 'Career resources', 'Annual Meeting discounts'].map(b => (
              <span key={b} className="text-xs bg-white/20 text-white px-3 py-1 rounded-full">{b}</span>
            ))}
          </div>
          <a href={joinUrl || 'https://pharmacist.com/join'} target="_blank" rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-white text-apha-blue px-5 py-2.5 rounded-xl font-semibold text-sm hover:bg-blue-50 transition">
            Join APhA — from $50/year →
          </a>
        </div>
      </div>
    </div>
  )
}
