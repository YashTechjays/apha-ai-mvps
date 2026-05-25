import { useEffect, useState } from "react";
import { getAnalyticsSummary, getByStatus, runBatch } from "../utils/api";
import StatCard from "../components/StatCard";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

const STATUS_COLORS = {
  sent: "#16a34a",
  qc_passed: "#1B4F8A",
  qc_failed: "#d97706",
  failed: "#dc2626",
  pending: "#9ca3af",
};

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [statusData, setStatusData] = useState([]);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [running, setRunning] = useState(false);
  const [batchResult, setBatchResult] = useState(null);

  useEffect(() => {
    getAnalyticsSummary(month).then((r) => setSummary(r.data));
    getByStatus(month).then((r) => setStatusData(r.data));
  }, [month]);

  const handleRunBatch = async (dryRun) => {
    setRunning(true);
    setBatchResult(null);
    try {
      const r = await runBatch(month, dryRun);
      setBatchResult(r.data);
      getAnalyticsSummary(month).then((r) => setSummary(r.data));
      getByStatus(month).then((r) => setStatusData(r.data));
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Email Campaign Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">Monthly personalized member value emails</p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm"
          />
          <button
            onClick={() => handleRunBatch(true)}
            disabled={running}
            className="px-4 py-1.5 text-sm border border-[#1B4F8A] text-[#1B4F8A] rounded hover:bg-blue-50 disabled:opacity-50"
          >
            Dry Run
          </button>
          <button
            onClick={() => handleRunBatch(false)}
            disabled={running}
            className="px-4 py-1.5 text-sm bg-[#1B4F8A] text-white rounded hover:bg-blue-800 disabled:opacity-50"
          >
            {running ? "Running..." : "Send Batch"}
          </button>
        </div>
      </div>

      {batchResult && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">
          Batch complete — Sent: {batchResult.sent} | QC Failed: {batchResult.qc_failed} | Errors: {batchResult.failed} | Skipped: {batchResult.skipped}
        </div>
      )}

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Sends" value={summary.total_sends} color="blue" />
          <StatCard
            label="Open Rate"
            value={`${((summary.open_rate || 0) * 100).toFixed(1)}%`}
            color="green"
          />
          <StatCard
            label="Avg Benefit Value"
            value={`$${(summary.avg_benefit_value_usd || 0).toFixed(0)}`}
            sub={`${(summary.avg_roi_multiplier || 0).toFixed(1)}x ROI`}
            color="blue"
          />
          <StatCard
            label="Total Value Delivered"
            value={`$${((summary.total_value_delivered_usd || 0) / 1000).toFixed(1)}k`}
            color="green"
          />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-5">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
            Email Status Breakdown
          </h2>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={statusData} margin={{ left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="status" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {statusData.map((entry) => (
                    <Cell key={entry.status} fill={STATUS_COLORS[entry.status] || "#9ca3af"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-400 text-sm text-center py-10">No data for this month</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-sm p-5">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
            QC & Personalization Scores
          </h2>
          {summary ? (
            <div className="space-y-5">
              {[
                { label: "Delivery Rate", val: summary.delivery_rate },
                { label: "Open Rate", val: summary.open_rate },
                { label: "Click Rate", val: summary.click_rate },
                { label: "Avg QC Score", val: summary.avg_qc_score },
                { label: "Avg Personalization", val: summary.avg_personalization_score },
              ].map(({ label, val }) => (
                <div key={label}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{label}</span>
                    <span className="font-medium">{((val || 0) * 100).toFixed(1)}%</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-2 bg-[#1B4F8A] rounded-full"
                      style={{ width: `${(val || 0) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm text-center py-10">No data for this month</p>
          )}
        </div>
      </div>
    </div>
  );
}
