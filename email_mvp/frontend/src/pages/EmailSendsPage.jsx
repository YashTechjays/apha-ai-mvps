import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getEmailSends } from "../utils/api";
import StatusBadge from "../components/StatusBadge";

const STATUSES = ["", "sent", "qc_failed", "failed", "pending"];

export default function EmailSendsPage() {
  const [sends, setSends] = useState([]);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [status, setStatus] = useState("");

  useEffect(() => {
    getEmailSends({ send_month: month, status: status || undefined, limit: 200 }).then((r) =>
      setSends(r.data)
    );
  }, [month, status]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Email Sends</h1>
        <div className="flex gap-3">
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm"
          />
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm"
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>{s || "All statuses"}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 uppercase text-xs tracking-wide">
            <tr>
              {["Member", "Month", "Subject", "Status", "Value", "QC", "Personalization", "Opened", "Clicked"].map(
                (h) => (
                  <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
                )
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {sends.map((s) => (
              <tr key={s.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link to={`/members/${s.member_id}`} className="text-[#1B4F8A] hover:underline">
                    {s.member_id.slice(0, 8)}…
                  </Link>
                </td>
                <td className="px-4 py-3">{s.send_month}</td>
                <td className="px-4 py-3 max-w-xs truncate text-gray-700">{s.subject_line || "—"}</td>
                <td className="px-4 py-3"><StatusBadge status={s.status} /></td>
                <td className="px-4 py-3">${s.total_value_usd?.toFixed(0)}</td>
                <td className="px-4 py-3">
                  {s.qc_score != null ? (
                    <span className={s.qc_score >= 0.7 ? "text-green-700" : "text-amber-600"}>
                      {(s.qc_score * 100).toFixed(0)}%
                    </span>
                  ) : "—"}
                </td>
                <td className="px-4 py-3">
                  {s.personalization_score != null
                    ? (s.personalization_score * 100).toFixed(0) + "%"
                    : "—"}
                </td>
                <td className="px-4 py-3">{s.opened ? "✓" : "—"}</td>
                <td className="px-4 py-3">{s.clicked ? "✓" : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {sends.length === 0 && (
          <p className="text-center text-gray-400 text-sm py-10">
            No emails for this filter. Run a batch from the Dashboard.
          </p>
        )}
      </div>
    </div>
  );
}
