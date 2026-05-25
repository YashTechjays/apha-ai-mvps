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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Header />
      <div className="max-w-4xl mx-auto px-6 py-8">

        {/* Usage meter */}
        {subStatus && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 px-5 py-3 mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-[#1B4F8A]/10 text-[#1B4F8A] uppercase">
                  {subStatus.plan}
                </span>
                <span className="text-sm text-slate-600">
                  {subStatus.queries_used_this_month} / {subStatus.queries_limit_per_month} queries used
                </span>
              </div>
              {/* Progress bar */}
              <div className="hidden sm:block w-32 h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    subStatus.queries_used_this_month >= subStatus.queries_limit_per_month ? 'bg-red-500' : 'bg-[#1B4F8A]'
                  }`}
                  style={{ width: `${Math.min(100, (subStatus.queries_used_this_month / subStatus.queries_limit_per_month) * 100)}%` }}
                />
              </div>
            </div>
            {subStatus.queries_used_this_month >= subStatus.queries_limit_per_month && (
              <a href="/drug-ref/pricing" className="text-sm font-semibold text-white bg-[#1B4F8A] px-4 py-1.5 rounded-lg hover:bg-[#163f6e] transition">
                Upgrade
              </a>
            )}
          </div>
        )}

        {/* Query card */}
        <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-6 sm:p-8">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 bg-[#1B4F8A]/10 rounded-xl flex items-center justify-center">
              <span className="text-lg">💊</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900">Ask a clinical question</h1>
              <p className="text-xs text-slate-400">AI-powered drug reference backed by clinical sources</p>
            </div>
          </div>

          <form onSubmit={submit}>
            <textarea
              className="w-full px-4 py-3 rounded-xl border border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#1B4F8A]/30 focus:border-[#1B4F8A] transition resize-y min-h-[110px] text-sm leading-relaxed"
              placeholder="e.g., What is the recommended starting dose of lisinopril in CKD stage 3?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <div className="flex flex-wrap items-center gap-3 mt-3">
              <select
                className="px-4 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-700 text-sm focus:outline-none focus:ring-2 focus:ring-[#1B4F8A]/30 focus:border-[#1B4F8A] transition"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              >
                <option value="">All categories</option>
                <option value="drug_monograph">Drug monographs</option>
                <option value="clinical_guideline">Clinical guidelines</option>
                <option value="pharmacy_practice">Pharmacy practice</option>
              </select>
              <button
                type="submit"
                disabled={busy || !question.trim()}
                className="bg-[#1B4F8A] text-white font-semibold px-6 py-2.5 rounded-lg hover:bg-[#163f6e] active:bg-[#12355c] disabled:opacity-40 disabled:cursor-not-allowed transition shadow-sm flex items-center gap-2"
              >
                {busy ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                    Searching...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                    Ask
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Example queries */}
          {!response && !busy && (
            <div className="mt-5 pt-5 border-t border-slate-100">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-3">Try an example</p>
              <div className="flex flex-wrap gap-2">
                {examples.map((ex, i) => (
                  <button
                    key={i}
                    onClick={() => setQuestion(ex)}
                    className="text-xs px-3.5 py-2 rounded-lg bg-slate-50 border border-slate-200 hover:bg-[#1B4F8A]/5 hover:border-[#1B4F8A]/30 hover:text-[#1B4F8A] text-slate-600 transition"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 text-red-700 rounded-xl px-5 py-4 text-sm">
            {error}
          </div>
        )}

        {/* Response */}
        {response && (
          <div className="bg-white rounded-2xl shadow-lg border border-slate-100 mt-6 overflow-hidden">
            {/* Response header */}
            <div className="px-6 py-3 bg-slate-50 border-b border-slate-100 flex justify-between items-center">
              <div className="flex items-center gap-3 text-xs text-slate-500">
                <span className="inline-flex items-center gap-1">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  {response.latency_ms}ms
                </span>
                <span className="inline-flex items-center gap-1">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                  {response.chunks_used} sources
                </span>
                <span className="px-2 py-0.5 rounded-full bg-slate-200/60 text-slate-600 font-medium">
                  {response.query_type}
                </span>
                {response.used_fallback && (
                  <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 font-medium">fallback</span>
                )}
              </div>
              <div className="flex gap-1">
                <button
                  onClick={() => feedback(true)}
                  className={`px-2.5 py-1.5 rounded-lg text-sm transition ${
                    response._feedback === "up"
                      ? "bg-green-100 text-green-700 ring-1 ring-green-300"
                      : "hover:bg-slate-100 text-slate-400 hover:text-slate-600"
                  }`}
                >👍</button>
                <button
                  onClick={() => feedback(false)}
                  className={`px-2.5 py-1.5 rounded-lg text-sm transition ${
                    response._feedback === "down"
                      ? "bg-red-100 text-red-700 ring-1 ring-red-300"
                      : "hover:bg-slate-100 text-slate-400 hover:text-slate-600"
                  }`}
                >👎</button>
              </div>
            </div>

            {/* Answer body */}
            <div className="px-6 py-5">
              <div className="prose prose-slate prose-sm max-w-none prose-headings:text-slate-900 prose-p:text-slate-700 prose-strong:text-slate-800 prose-ul:text-slate-700 prose-li:marker:text-[#1B4F8A]">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{response.answer}</ReactMarkdown>
              </div>
            </div>

            {/* Citations */}
            {response.citations?.length > 0 && (
              <div className="border-t border-slate-100 px-6 py-4 bg-slate-50/50">
                <h3 className="font-semibold text-xs text-slate-500 uppercase tracking-wide mb-3">Sources</h3>
                <div className="space-y-2">
                  {response.citations.map((c, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm">
                      <span className="flex-shrink-0 w-5 h-5 rounded-full bg-[#1B4F8A]/10 text-[#1B4F8A] text-xs font-bold flex items-center justify-center mt-0.5">
                        {i + 1}
                      </span>
                      <div>
                        <span className="font-medium text-slate-800">{c.title}</span>
                        <span className="text-slate-400 ml-2 text-xs">{c.category} · relevance {c.max_score.toFixed(2)}</span>
                      </div>
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
