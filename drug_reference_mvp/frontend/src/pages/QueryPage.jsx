import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Header from "../components/Header";
import { queries, subs } from "../lib/api";

export default function QueryPage() {
  const [question, setQuestion] = useState("");
  const [category, setCategory] = useState("");
  const [busy, setBusy] = useState(false);
  const [response, setResponse] = useState(null);
  const [subStatus, setSubStatus] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    subs.me().then(setSubStatus).catch(() => {});
  }, [response]);

  const submit = async (e) => {
    e?.preventDefault();
    if (!question.trim()) return;
    setBusy(true);
    setError("");
    setResponse(null);
    try {
      const r = await queries.ask(question, category || undefined);
      setResponse(r);
    } catch (err) {
      setError(err.response?.data?.detail?.error || err.response?.data?.detail || "Query failed.");
    } finally { setBusy(false); }
  };

  const feedback = async (thumbs_up) => {
    if (!response) return;
    try {
      await queries.feedback(response.query_id, thumbs_up);
      setResponse({ ...response, _feedback: thumbs_up ? "up" : "down" });
    } catch {}
  };

  const examples = [
    "What is the renal dosing for metformin?",
    "Drug interactions between warfarin and amoxicillin?",
    "Counseling points for a new sertraline prescription",
    "When should atorvastatin be held perioperatively?",
  ];

  return (
    <div className="min-h-screen">
      <Header />
      <div className="max-w-4xl mx-auto px-6 py-8">
        {subStatus && (
          <div className="card mb-4 text-sm flex items-center justify-between">
            <div>
              <span className="font-semibold text-apha">{subStatus.plan}</span> plan ·
              {" "}{subStatus.queries_used_this_month} / {subStatus.queries_limit_per_month} queries used this month
            </div>
            {subStatus.queries_used_this_month >= subStatus.queries_limit_per_month && (
              <a className="btn-primary" href="/pricing">Upgrade</a>
            )}
          </div>
        )}

        <div className="card">
          <h1 className="text-xl font-bold text-apha-700 mb-3">Ask a clinical question</h1>
          <form onSubmit={submit}>
            <textarea
              className="input min-h-[100px]"
              placeholder="e.g., What is the recommended starting dose of lisinopril in CKD stage 3?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <div className="flex flex-wrap gap-2 mt-2">
              <select className="input max-w-xs" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="">All categories</option>
                <option value="drug_monograph">Drug monographs</option>
                <option value="clinical_guideline">Clinical guidelines</option>
                <option value="pharmacy_practice">Pharmacy practice</option>
              </select>
              <button className="btn-primary" disabled={busy || !question.trim()}>
                {busy ? "Searching…" : "Ask"}
              </button>
            </div>
          </form>
          {!response && !busy && (
            <div className="mt-4">
              <p className="text-xs text-slate-500 mb-2">Try an example:</p>
              <div className="flex flex-wrap gap-2">
                {examples.map((ex, i) => (
                  <button key={i} onClick={() => setQuestion(ex)} className="text-xs px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700">{ex}</button>
                ))}
              </div>
            </div>
          )}
        </div>

        {error && <div className="card mt-4 text-red-700 bg-red-50 border border-red-200">{error}</div>}

        {response && (
          <div className="card mt-6">
            <div className="flex justify-between items-start mb-3">
              <div className="text-xs text-slate-500">
                {response.latency_ms}ms · {response.chunks_used} sources · type: {response.query_type}
                {response.used_fallback && " · deterministic fallback"}
              </div>
              <div className="flex gap-1">
                <button onClick={() => feedback(true)} className={`text-sm px-2 py-1 rounded ${response._feedback === "up" ? "bg-green-100 text-green-700" : "hover:bg-slate-100"}`}>👍</button>
                <button onClick={() => feedback(false)} className={`text-sm px-2 py-1 rounded ${response._feedback === "down" ? "bg-red-100 text-red-700" : "hover:bg-slate-100"}`}>👎</button>
              </div>
            </div>
            <div className="markdown-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{response.answer}</ReactMarkdown>
            </div>
            {response.citations?.length > 0 && (
              <div className="border-t border-slate-200 mt-4 pt-4">
                <h3 className="font-semibold text-sm text-slate-700 mb-2">Sources</h3>
                <ul className="text-sm text-slate-600 space-y-1">
                  {response.citations.map((c, i) => (
                    <li key={i}>
                      <span className="font-medium">{c.title}</span>
                      <span className="text-slate-400"> · {c.category} · relevance {c.max_score.toFixed(2)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
