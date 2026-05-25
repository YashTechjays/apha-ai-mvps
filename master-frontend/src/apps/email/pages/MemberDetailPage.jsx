import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getMember, getBenefitSummary, getMemberEmails, previewEmail, sendSingleEmail } from "../utils/api";
import StatusBadge from "../components/StatusBadge";

export default function MemberDetailPage() {
  const { id } = useParams();
  const [member, setMember] = useState(null);
  const [summary, setSummary] = useState(null);
  const [emails, setEmails] = useState([]);
  const [preview, setPreview] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [sending, setSending] = useState(false);
  const month = new Date().toISOString().slice(0, 7);

  useEffect(() => {
    getMember(id).then((r) => setMember(r.data));
    getBenefitSummary(id, month).then((r) => setSummary(r.data));
    getMemberEmails(id).then((r) => setEmails(r.data));
  }, [id]);

  const handlePreview = async () => {
    setLoadingPreview(true);
    try {
      const r = await previewEmail(id, month);
      setPreview(r.data);
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleSend = async () => {
    setSending(true);
    try {
      await sendSingleEmail(id, month);
      const r = await getMemberEmails(id);
      setEmails(r.data);
      setPreview(null);
    } finally {
      setSending(false);
    }
  };

  if (!member) return <p className="text-gray-400">Loading...</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {member.first_name} {member.last_name}
          </h1>
          <p className="text-gray-500 text-sm">{member.email}</p>
        </div>
        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold capitalize">
          {member.tier}
        </span>
      </div>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Total Benefit Value", value: `$${summary.total_value_usd?.toFixed(0)}` },
            { label: "ROI Multiplier", value: `${summary.roi_multiplier}x` },
            { label: "Engagement Level", value: summary.engagement_level },
            { label: "Top Benefit", value: summary.top_benefit },
          ].map(({ label, value }) => (
            <div key={label} className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
              <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
              <p className="text-xl font-bold text-[#1B4F8A] mt-1 capitalize">{value}</p>
            </div>
          ))}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-800">Email Preview — {month}</h2>
          <div className="flex gap-2">
            <button
              onClick={handlePreview}
              disabled={loadingPreview}
              className="px-3 py-1.5 text-sm border border-[#1B4F8A] text-[#1B4F8A] rounded hover:bg-blue-50"
            >
              {loadingPreview ? "Generating..." : "Generate Preview"}
            </button>
            {preview && (
              <button
                onClick={handleSend}
                disabled={sending}
                className="px-3 py-1.5 text-sm bg-[#1B4F8A] text-white rounded hover:bg-blue-800"
              >
                {sending ? "Sending..." : "Send Email"}
              </button>
            )}
          </div>
        </div>
        {preview ? (
          <div>
            <p className="text-xs text-gray-500 mb-1">Subject</p>
            <p className="font-semibold mb-3">{preview.subject}</p>
            <div
              className="border rounded overflow-auto max-h-[500px]"
              dangerouslySetInnerHTML={{ __html: preview.html_body }}
            />
          </div>
        ) : (
          <p className="text-gray-400 text-sm text-center py-8">
            Click "Generate Preview" to see the AI-personalized email for this member.
          </p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-sm p-5">
        <h2 className="font-semibold text-gray-800 mb-4">Email History</h2>
        {emails.length === 0 ? (
          <p className="text-gray-400 text-sm">No emails sent yet.</p>
        ) : (
          <table className="min-w-full text-sm">
            <thead className="text-gray-500 uppercase text-xs">
              <tr>
                {["Month", "Status", "Value", "QC Score", "Opened", "Clicked", "Sent At"].map((h) => (
                  <th key={h} className="pb-2 text-left font-medium pr-4">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {emails.map((e) => (
                <tr key={e.id}>
                  <td className="py-2 pr-4">{e.send_month}</td>
                  <td className="py-2 pr-4"><StatusBadge status={e.status} /></td>
                  <td className="py-2 pr-4">${e.total_value_usd?.toFixed(0)}</td>
                  <td className="py-2 pr-4">{e.qc_score != null ? (e.qc_score * 100).toFixed(0) + "%" : "—"}</td>
                  <td className="py-2 pr-4">{e.opened ? "✓" : "—"}</td>
                  <td className="py-2 pr-4">{e.clicked ? "✓" : "—"}</td>
                  <td className="py-2 pr-4 text-gray-400">{e.sent_at ? new Date(e.sent_at).toLocaleDateString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
