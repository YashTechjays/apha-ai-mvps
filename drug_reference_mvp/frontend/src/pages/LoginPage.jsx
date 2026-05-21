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
      localStorage.setItem("apha_token", r.access_token);
      navigate("/query");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed.");
    } finally { setBusy(false); }
  };

  return (
    <div className="min-h-screen">
      <Header />
      <div className="max-w-md mx-auto px-6 py-16">
        <h1 className="text-2xl font-bold text-apha-700 mb-2">Welcome back</h1>
        <p className="text-sm text-slate-500 mb-6">Sign in to your APhA Clinical Assistant account.</p>
        <form onSubmit={submit} className="card space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 p-2 rounded">{error}</div>}
          <div>
            <label className="text-sm font-medium text-slate-700">Email</label>
            <input className="input mt-1" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Password</label>
            <input className="input mt-1" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button className="btn-primary w-full" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
        </form>
        <p className="text-sm text-slate-500 mt-4 text-center">
          New here? <Link to="/signup" className="text-apha underline">Start your free trial</Link>
        </p>
      </div>
    </div>
  );
}
