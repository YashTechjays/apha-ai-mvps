export default function PlanCard({ course, index, isLocked = false }) {
  return (
    <div className={`relative border rounded-xl p-4 transition-all ${
      isLocked ? 'blur-sm pointer-events-none' : 'hover:border-apha-blue hover:shadow-sm'
    } ${course.is_mandatory ? 'border-orange-300 bg-orange-50' : 'border-gray-200 bg-white'}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-gray-400">#{index + 1}</span>
            {course.is_mandatory && (
              <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full font-semibold">
                Required by your state
              </span>
            )}
          </div>
          <h3 className="font-semibold text-gray-900 text-sm leading-tight mb-1">{course.title}</h3>
          <p className="text-xs text-gray-500 mb-2 leading-relaxed">{course.why_recommended}</p>
          {course.is_mandatory && course.mandatory_reason && (
            <p className="text-xs text-orange-600 mb-2">📋 {course.mandatory_reason}</p>
          )}
        </div>
        <div className="text-right shrink-0">
          <div className="text-lg font-bold text-apha-blue">{course.cpe_hours}h</div>
          <div className="text-xs text-gray-400">CPE</div>
        </div>
      </div>
      <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-100">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 line-through">${course.price_nonmember}</span>
          <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-semibold">
            Free with membership
          </span>
        </div>
        <a href={course.url} target="_blank" rel="noopener noreferrer"
          className="text-xs text-apha-blue font-semibold hover:underline">
          View course →
        </a>
      </div>
    </div>
  )
}
