import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import { subs } from "../lib/api";

export default function PricingPage() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    subs.plans().then((p) => { setPlans(p); setLoading(false); }).catch(() => {
      // Fallback static plans
      setPlans(staticPlans);
      setLoading(false);
    });
  }, []);

  const start = async (code) => {
    const token = localStorage.getItem('drugref_token');
    if (!token) { navigate("/signup"); return; }
    if (code === "trial") { navigate('/drug-ref/query'); return; }
    setBusy(code);
    try {
      const { checkout_url } = await subs.checkout(code);
      window.location.href = checkout_url;
    } catch (e) {
      alert("Checkout failed — please try again.");
    } finally { setBusy(null); }
  };

  return (
    <div className="min-h-screen">
      <Header />
      <div className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold text-apha-700 text-center">Simple, predictable pricing</h1>
        <p className="text-center text-slate-600 mt-2 max-w-2xl mx-auto">
          Choose the plan that fits how you use clinical drug references. Cancel any time.
        </p>

        {loading ? (
          <p className="text-center mt-12 text-slate-500">Loading plans…</p>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
            {plans.map((p) => (
              <div
                key={p.code}
                className={`card flex flex-col ${p.code === "team" ? "ring-2 ring-apha" : ""}`}
              >
                {p.code === "team" && (
                  <div className="text-xs font-semibold text-apha bg-apha-100 px-2 py-1 rounded inline-block self-start mb-2">
                    Most popular
                  </div>
                )}
                <h3 className="text-xl font-bold text-apha-700">{p.name}</h3>
                <div className="mt-3 mb-4">
                  {p.code === "enterprise" ? (
                    <div className="text-2xl font-bold text-slate-800">Custom</div>
                  ) : (
                    <>
                      <span className="text-4xl font-bold text-slate-800">${p.monthly_price_usd}</span>
                      <span className="text-slate-500 text-sm">/month</span>
                    </>
                  )}
                </div>
                <ul className="text-sm text-slate-700 space-y-2 mb-6 flex-1">
                  {p.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-apha font-bold">✓</span> {f}
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => start(p.code)}
                  disabled={busy === p.code}
                  className={p.code === "team" ? "btn-primary" : "btn-secondary"}
                >
                  {busy === p.code
                    ? "Loading…"
                    : p.code === "trial"
                    ? "Start trial"
                    : p.code === "enterprise"
                    ? "Contact sales"
                    : "Subscribe"}
                </button>
              </div>
            ))}
          </div>
        )}

        <p className="text-center text-xs text-slate-500 mt-12">
          Need a quote or compliance review? <Link className="text-apha underline" to="/drug-ref/signup">Sign up</Link> and we'll be in touch.
        </p>
      </div>
    </div>
  );
}

const staticPlans = [
  { code: "trial", name: "Free Trial", monthly_price_usd: 0, features: ["10 queries / month", "Single user", "Web interface only"] },
  { code: "individual", name: "Individual", monthly_price_usd: 99, features: ["500 queries / month", "Full APhA library", "Citation tracking"] },
  { code: "team", name: "Pharmacy Team", monthly_price_usd: 299, features: ["2,500 queries / month", "Up to 10 seats", "API access"] },
  { code: "institution", name: "Institution", monthly_price_usd: 799, features: ["15,000 queries / month", "Up to 50 seats", "Dedicated success manager"] },
  { code: "enterprise", name: "Enterprise", monthly_price_usd: 0, features: ["Custom volume", "Unlimited seats", "Custom SLA"] },
];
