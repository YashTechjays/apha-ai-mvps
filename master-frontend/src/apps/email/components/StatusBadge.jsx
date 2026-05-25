const COLORS = {
  sent: "bg-green-100 text-green-800",
  qc_passed: "bg-blue-100 text-blue-800",
  qc_failed: "bg-amber-100 text-amber-800",
  failed: "bg-red-100 text-red-800",
  pending: "bg-gray-100 text-gray-700",
};

export default function StatusBadge({ status }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${COLORS[status] || COLORS.pending}`}>
      {status?.replace("_", " ")}
    </span>
  );
}
