import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import { auth } from "../lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r = await auth.login({ email, password });
      localStorage.setItem('drugref_token', r.access_token);
      navigate('/drug-ref/query');
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed.");
    } finally { setBusy(false); }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Header />
      <div className="max-w-md mx-auto px-6 py-16">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-[#1B4F8A]/10 rounded-2xl mb-4">
            <span className="text-2xl">💊</span>
          </div>
          <h1 className="text-2xl font-bold text-[#1B4F8A]">Welcome back</h1>
          <p className="text-sm text-slate-500 mt-2">Sign in to your APhA Clinical Assistant account.</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-8">
          <form onSubmit={submit} className="space-y-5">
            {error && (
              <div className="text-sm text-red-700 bg-red-50 border border-red-200 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Email</label>
              <input
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#1B4F8A]/30 focus:border-[#1B4F8A] transition"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jane@pharmacy.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Password</label>
              <input
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#1B4F8A]/30 focus:border-[#1B4F8A] transition"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              disabled={busy}
              className="w-full bg-[#1B4F8A] text-white font-semibold py-3 rounded-lg hover:bg-[#163f6e] active:bg-[#12355c] disabled:opacity-50 disabled:cursor-not-allowed transition shadow-md shadow-[#1B4F8A]/20"
            >
              {busy ? "Signing in..." : "Sign in"}
            </button>
          </form>
        </div>

        <p className="text-sm text-slate-500 mt-6 text-center">
          New here?{" "}
          <Link to="/drug-ref/signup" className="text-[#1B4F8A] font-semibold hover:underline">
            Start your free trial
          </Link>
        </p>
      </div>
    </div>
  );
}
