export default function StatusBadge({ status, deadline }) {
  let color = 'bg-gray-100 text-gray-700'
  if (status === 'open') {
    if (deadline) {
      const days = Math.ceil((new Date(deadline) - new Date()) / 86400000)
      if (days <= 7) color = 'bg-red-100 text-red-700'
      else if (days <= 30) color = 'bg-yellow-100 text-yellow-700'
      else color = 'bg-green-100 text-green-700'
    } else {
      color = 'bg-green-100 text-green-700'
    }
  } else if (status === 'closed') {
    color = 'bg-gray-200 text-gray-500'
  }

  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {status}
    </span>
  )
}
