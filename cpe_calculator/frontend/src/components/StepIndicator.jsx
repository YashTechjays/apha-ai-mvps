export default function StepIndicator({ currentStep }) {
  const steps = ['Your info', 'Your plan', 'Full access']
  return (
    <div className="flex items-center justify-center gap-2 mb-8">
      {steps.map((label, i) => {
        const step = i + 1
        const done = step < currentStep
        const active = step === currentStep
        return (
          <div key={step} className="flex items-center gap-2">
            <div className={`flex items-center gap-1.5 ${active ? 'opacity-100' : done ? 'opacity-70' : 'opacity-40'}`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold
                ${active ? 'bg-apha-blue text-white' : done ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'}`}>
                {done ? '✓' : step}
              </div>
              <span className={`text-sm ${active ? 'font-semibold text-apha-blue' : 'text-gray-500'}`}>{label}</span>
            </div>
            {i < steps.length - 1 && <div className="w-8 h-px bg-gray-300 mx-1" />}
          </div>
        )
      })}
    </div>
  )
}
