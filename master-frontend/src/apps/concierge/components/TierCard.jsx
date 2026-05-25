const TIER_INFO = {
  student:          { label: 'Student Pharmacist',  price: '~$50/year',  color: 'bg-purple-50 border-purple-200' },
  new_practitioner: { label: 'New Practitioner',    price: '~$115/year', color: 'bg-blue-50 border-blue-200' },
  pharmacist:       { label: 'Full Pharmacist',     price: '~$195/year', color: 'bg-green-50 border-green-200' },
  technician:       { label: 'Pharmacy Technician', price: '~$75/year',  color: 'bg-yellow-50 border-yellow-200' },
  researcher:       { label: 'Researcher',          price: '~$195/year', color: 'bg-red-50 border-red-200' },
}

export default function TierCard({ tier, onJoinClick }) {
  const info = TIER_INFO[tier]
  if (!info) return null
  return (
    <div className={`border rounded-xl p-3 mt-2 ${info.color}`}>
      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Recommended for you</div>
      <div className="font-bold text-gray-900">{info.label}</div>
      <div className="text-sm text-gray-600">{info.price}</div>
      <button
        onClick={onJoinClick}
        className="mt-2 w-full bg-[#1B4F8A] text-white text-sm py-1.5 rounded-lg font-semibold hover:bg-blue-800 transition"
      >
        Join Now →
      </button>
    </div>
  )
}
