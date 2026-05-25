import { useEffect, useState } from "react";
import Header from "../components/Header";
import { analytics, auth, queries, subs } from "../lib/api";

export default function DashboardPage() {
  const [usage, setUsage] = useState(null);
  const [subStatus, setSubStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [apiKeys, setApiKeys] = useState([]);
  const [newKeyLabel, setNewKeyLabel] = useState("");
  const [createdKey, setCreatedKey] = useState(null);

  const loadAll = () => {
    analytics.usage().then(setUsage).catch(() => {});
    subs.me().then(setSubStatus).catch(() => {});
    queries.history(10).then(setHistory).catch(() => {});
    auth.apiKeys.list().then(setApiKeys).catch(() => {});
  };

  useEffect(loadAll, []);

  const createKey = async (e) => {
    e.preventDefault();
    const r = await auth.apiKeys.create(newKeyLabel || "Untitled");
    setCreatedKey(r);
    setNewKeyLabel("");
    loadAll();
  };
  const revokeKey = async (id) => {
    if (!confirm("Revoke this API key?")) return;
    await auth.apiKeys.revoke(id);
    loadAll();
  };

  return (
    <div className="min-h-screen">
      <Header />
      <div className="max-w-6xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold text-apha-700 mb-6">Dashboard</h1>

        <div className="grid md:grid-cols-3 gap-4 mb-8">
          <Stat title="Plan" value={subStatus?.plan || "—"} />
          <Stat title="Queries this month" value={`${subStatus?.queries_used_this_month ?? 0} / ${subStatus?.queries_limit_per_month ?? 0}`} />
          <Stat title="Avg latency (30d)" value={usage ? `${usage.avg_latency_ms?.toFixed?.(0)}ms` : "—"} />
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="font-bold text-apha-700 mb-3">Recent queries</h2>
            {history.length === 0 ? (
              <p className="text-sm text-slate-500">No queries yet.</p>
            ) : (
              <ul className="space-y-3 text-sm">
                {history.map((h) => (
                  <li key={h.id} className="border-b border-slate-100 pb-2">
                    <div className="text-slate-800 line-clamp-2">{h.query_text}</div>
                    <div className="text-xs text-slate-400 mt-1">
                      {h.query_type} · {h.sources_cited} sources · {h.latency_ms}ms
                      {h.thumbs_up !== null && (h.thumbs_up ? " · 👍" : " · 👎")}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="card">
            <h2 className="font-bold text-apha-700 mb-3">API Keys</h2>
            {createdKey && (
              <div className="bg-amber-50 border border-amber-300 p-3 rounded mb-3 text-sm">
                <div className="font-semibold text-amber-800 mb-1">Save this key — it won't be shown again:</div>
                <code className="text-xs break-all">{createdKey.raw_key}</code>
              </div>
            )}
            <form onSubmit={createKey} className="flex gap-2 mb-4">
              <input className="input flex-1" placeholder="Label (e.g. 'pharmacy app')" value={newKeyLabel} onChange={(e) => setNewKeyLabel(e.target.value)} />
              <button className="btn-primary">Create</button>
            </form>
            {apiKeys.length === 0 ? (
              <p className="text-sm text-slate-500">No API keys yet.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {apiKeys.map((k) => (
                  <li key={k.id} className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{k.label || "Untitled"}</div>
                      <div className="text-xs text-slate-400">{k.key_prefix}… · {k.is_active ? "active" : "revoked"}</div>
                    </div>
                    {k.is_active && (
                      <button onClick={() => revokeKey(k.id)} className="text-xs text-red-600 hover:underline">Revoke</button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {usage && (
          <div className="card mt-6">
            <h2 className="font-bold text-apha-700 mb-3">Usage (last 30 days)</h2>
            <div className="grid md:grid-cols-4 gap-4 text-sm">
              <KV label="Total queries" value={usage.total_queries} />
              <KV label="Safety flagged" value={usage.safety_flagged} />
              <KV label="Thumbs up" value={usage.thumbs_up} />
              <KV label="Thumbs down" value={usage.thumbs_down} />
            </div>
            {usage.by_query_type?.length > 0 && (
              <div className="mt-4">
                <h3 className="text-sm font-semibold text-slate-700 mb-2">By query type</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                  {usage.by_query_type.map((t) => (
                    <div key={t.query_type} className="bg-slate-100 rounded px-2 py-1 flex justify-between">
                      <span>{t.query_type}</span>
                      <span className="font-semibold">{t.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function Stat({ title, value }) {
  return (
    <div className="card">
      <div className="text-xs text-slate-500">{title}</div>
      <div className="text-2xl font-bold text-apha-700 mt-1">{value}</div>
    </div>
  );
}
function KV({ label, value }) {
  return (
    <div>
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-lg font-semibold text-slate-800">{value}</div>
    </div>
  );
}
