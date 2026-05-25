import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import { auth } from "../lib/api";

export default function SignupPage() {
  const [form, setForm] = useState({ email: "", password: "", full_name: "", organization_name: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r = await auth.signup({
        email: form.email,
        password: form.password,
        full_name: form.full_name || undefined,
        organization_name: form.organization_name || undefined,
      });
      localStorage.setItem('drugref_token', r.access_token);
      navigate('/drug-ref/query');
    } catch (err) {
      setError(err.response?.data?.detail || "Signup failed.");
    } finally { setBusy(false); }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Header />
      <div className="max-w-md mx-auto px-6 py-16">
        {/* Header section */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-[#1B4F8A]/10 rounded-2xl mb-4">
            <span className="text-2xl">💊</span>
          </div>
          <h1 className="text-2xl font-bold text-[#1B4F8A]">Start your free trial</h1>
          <p className="text-sm text-slate-500 mt-2">10 clinical queries to evaluate. No credit card required.</p>
        </div>

        {/* Form card */}
        <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-8">
          <form onSubmit={submit} className="space-y-5">
            {error && (
              <div className="text-sm text-red-700 bg-red-50 border border-red-200 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Full name</label>
              <input
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#1B4F8A]/30 focus:border-[#1B4F8A] transition"
                value={form.full_name}
                onChange={update("full_name")}
                placeholder="Jane Patel, PharmD"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Work email</label>
              <input
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#1B4F8A]/30 focus:border-[#1B4F8A] transition"
                type="email"
                value={form.email}
                onChange={update("email")}
                placeholder="jane@pharmacy.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Password</label>
              <input
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#1B4F8A]/30 focus:border-[#1B4F8A] transition"
                type="password"
                value={form.password}
                onChange={update("password")}
                placeholder="••••••••"
                required
                minLength={8}
              />
              <p className="text-xs text-slate-400 mt-1.5">8+ characters.</p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                Organization <span className="font-normal text-slate-400">(optional)</span>
              </label>
              <input
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#1B4F8A]/30 focus:border-[#1B4F8A] transition"
                value={form.organization_name}
                onChange={update("organization_name")}
                placeholder="Riverside Pharmacy"
              />
            </div>

            <button
              type="submit"
              disabled={busy}
              className="w-full bg-[#1B4F8A] text-white font-semibold py-3 rounded-lg hover:bg-[#163f6e] active:bg-[#12355c] disabled:opacity-50 disabled:cursor-not-allowed transition shadow-md shadow-[#1B4F8A]/20"
            >
              {busy ? "Creating account..." : "Create account"}
            </button>
          </form>
        </div>

        <p className="text-sm text-slate-500 mt-6 text-center">
          Already have an account?{" "}
          <Link to="/drug-ref/login" className="text-[#1B4F8A] font-semibold hover:underline">
            Log in
          </Link>
        </p>

        {/* Trust badges */}
        <div className="mt-8 flex items-center justify-center gap-6 text-xs text-slate-400">
          <div className="flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
            HIPAA-ready
          </div>
          <div className="flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
            Encrypted
          </div>
          <div className="flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg>
            No credit card
          </div>
        </div>
      </div>
    </div>
  );
}
