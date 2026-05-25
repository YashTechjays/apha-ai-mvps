export default function UsageMeter({ used, limit }) {
  const remaining = Math.max(0, limit - used)
  const pct = (used / limit) * 100

  if (remaining === 0) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-3 flex items-center gap-3">
        <span className="text-red-600 text-sm font-semibold">
          Free limit reached ({limit}/{limit} used today)
        </span>
        <a
          href="https://pharmacist.com/join"
          target="_blank"
          rel="noopener noreferrer"
          className="ml-auto text-xs bg-red-600 text-white px-3 py-1.5 rounded-lg font-semibold"
        >
          Unlock unlimited &rarr;
        </a>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 bg-gray-50 rounded-xl px-4 py-2.5">
      <div className="flex-1">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Free checks today</span>
          <span className="font-semibold text-gray-700">
            {used}/{limit} used
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full ${pct >= 66 ? 'bg-orange-400' : 'bg-green-500'}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
      {remaining <= 1 && (
        <a
          href="https://pharmacist.com/join"
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-apha-blue font-semibold hover:underline whitespace-nowrap"
        >
          Get unlimited &rarr;
        </a>
      )}
    </div>
  )
}
