import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAnalyticsSummary, getTopMembers } from "../utils/api";
import StatCard from "../components/StatCard";

export default function AnalyticsPage() {
  const [summary, setSummary] = useState(null);
  const [topMembers, setTopMembers] = useState([]);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));

  useEffect(() => {
    getAnalyticsSummary(month).then((r) => setSummary(r.data));
    getTopMembers(month).then((r) => setTopMembers(r.data));
  }, [month]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          className="border rounded px-3 py-1.5 text-sm"
        />
      </div>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard label="Emails Sent" value={summary.sent ?? 0} color="blue" />
          <StatCard
            label="Open Rate"
            value={`${((summary.open_rate || 0) * 100).toFixed(1)}%`}
            color="green"
          />
          <StatCard
            label="Click Rate"
            value={`${((summary.click_rate || 0) * 100).toFixed(1)}%`}
            color="blue"
          />
          <StatCard
            label="Total Value Delivered"
            value={`$${((summary.total_value_delivered_usd || 0) / 1000).toFixed(1)}k`}
            color="green"
          />
          <StatCard
            label="Avg Benefit / Member"
            value={`$${(summary.avg_benefit_value_usd || 0).toFixed(0)}`}
            color="blue"
          />
          <StatCard
            label="Avg ROI"
            value={`${(summary.avg_roi_multiplier || 0).toFixed(1)}x`}
            color="green"
          />
          <StatCard
            label="Avg QC Score"
            value={`${((summary.avg_qc_score || 0) * 100).toFixed(0)}%`}
            color={summary.avg_qc_score >= 0.7 ? "green" : "amber"}
          />
          <StatCard
            label="Avg Personalization"
            value={`${((summary.avg_personalization_score || 0) * 100).toFixed(0)}%`}
            color="blue"
          />
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm p-5">
        <h2 className="font-semibold text-gray-800 mb-4">Top 10 Members by Benefit Value</h2>
        {topMembers.length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-8">No data for this period.</p>
        ) : (
          <table className="min-w-full text-sm">
            <thead className="text-gray-500 uppercase text-xs">
              <tr>
                {["Rank", "Member", "Tier", "Benefit Value", "Status", "Opened"].map((h) => (
                  <th key={h} className="pb-2 text-left font-medium pr-6">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {topMembers.map((m, i) => (
                <tr key={m.member_id}>
                  <td className="py-2 pr-6 text-gray-400 font-mono">#{i + 1}</td>
                  <td className="py-2 pr-6">
                    <Link to={`/members/${m.member_id}`} className="text-[#1B4F8A] hover:underline font-medium">
                      {m.name}
                    </Link>
                  </td>
                  <td className="py-2 pr-6">
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs capitalize">
                      {typeof m.tier === "object" ? m.tier?.value ?? m.tier : m.tier}
                    </span>
                  </td>
                  <td className="py-2 pr-6 font-semibold text-[#1B4F8A]">
                    ${m.total_value_usd?.toFixed(0)}
                  </td>
                  <td className="py-2 pr-6">{m.status}</td>
                  <td className="py-2 pr-6">{m.opened ? "✓" : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
