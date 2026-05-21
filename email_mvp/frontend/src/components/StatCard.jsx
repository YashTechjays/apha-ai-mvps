export default function StatCard({ label, value, sub, color = "blue" }) {
  const colors = {
    blue: "border-[#1B4F8A] text-[#1B4F8A]",
    green: "border-green-600 text-green-700",
    amber: "border-amber-500 text-amber-600",
    red: "border-red-500 text-red-600",
  };
  return (
    <div className={`bg-white rounded-lg border-l-4 ${colors[color]} p-5 shadow-sm`}>
      <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${colors[color].split(" ")[1]}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}
