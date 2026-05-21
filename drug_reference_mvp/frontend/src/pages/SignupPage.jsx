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
      localStorage.setItem("apha_token", r.access_token);
      navigate("/query");
    } catch (err) {
      setError(err.response?.data?.detail || "Signup failed.");
    } finally { setBusy(false); }
  };

  return (
    <div className="min-h-screen">
      <Header />
      <div className="max-w-md mx-auto px-6 py-16">
        <h1 className="text-2xl font-bold text-apha-700 mb-2">Start your free trial</h1>
        <p className="text-sm text-slate-500 mb-6">10 clinical queries to evaluate. No credit card required.</p>
        <form onSubmit={submit} className="card space-y-4">
          {error && <div className="text-sm text-red-600 bg-red-50 p-2 rounded">{error}</div>}
          <div>
            <label className="text-sm font-medium text-slate-700">Full name</label>
            <input className="input mt-1" value={form.full_name} onChange={update("full_name")} placeholder="Jane Patel, PharmD" />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Work email</label>
            <input className="input mt-1" type="email" value={form.email} onChange={update("email")} required />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Password</label>
            <input className="input mt-1" type="password" value={form.password} onChange={update("password")} required minLength={8} />
            <p className="text-xs text-slate-400 mt-1">8+ characters.</p>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Organization (optional)</label>
            <input className="input mt-1" value={form.organization_name} onChange={update("organization_name")} placeholder="Riverside Pharmacy" />
          </div>
          <button className="btn-primary w-full" disabled={busy}>{busy ? "Creating account…" : "Create account"}</button>
        </form>
        <p className="text-sm text-slate-500 mt-4 text-center">
          Already have an account? <Link to="/login" className="text-apha underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}
