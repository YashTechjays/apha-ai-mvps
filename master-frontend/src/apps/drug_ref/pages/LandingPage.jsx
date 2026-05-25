import { Link } from "react-router-dom";
import Header from "../components/Header";

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <section className="bg-gradient-to-b from-apha-50 to-white">
        <div className="max-w-6xl mx-auto px-6 py-20 text-center">
          <div className="inline-block px-3 py-1 rounded-full bg-apha-100 text-apha-700 text-xs font-semibold mb-6">
            Backed by APhA reference content · Built for pharmacists
          </div>
          <h1 className="text-5xl font-bold text-apha-700 mb-6 leading-tight">
            Trusted clinical drug answers,<br />in under 3 seconds.
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
            APhA Clinical Assistant searches our authoritative drug monographs, clinical guidelines, and pharmacy practice resources to give you cited, decision-ready answers — without the noise.
          </p>
          <div className="flex gap-3 justify-center">
            <Link to="/drug-ref/signup" className="btn-primary text-base px-6 py-3">
              Start free — 10 queries
            </Link>
            <Link to="/drug-ref/pricing" className="btn-secondary text-base px-6 py-3">
              View pricing
            </Link>
          </div>
          <p className="mt-4 text-xs text-slate-500">No credit card required for trial.</p>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <Feature
            title="Cited, evidence-grounded answers"
            body="Every clinically substantive statement is backed by a citation to the APhA reference library — no hallucinated guidelines."
          />
          <Feature
            title="Pharmacist-tuned safety"
            body="Built-in safety guardrails flag patient-specific requests, contraindicated combinations, and red-flag queries."
          />
          <Feature
            title="API access for teams"
            body="Embed clinical decision support in your pharmacy system, EHR, or workflow tool with our REST API."
          />
        </div>
      </section>

      <section className="bg-slate-100 py-16">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-10 text-apha-700">Reference library coverage</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <Stat number="5" label="Drug monographs" />
            <Stat number="4" label="Clinical guidelines" />
            <Stat number="3" label="Pharmacy practice topics" />
          </div>
          <p className="text-center text-sm text-slate-500 mt-6">
            Growing weekly — request topics through your dashboard once subscribed.
          </p>
        </div>
      </section>

      <footer className="bg-apha-700 text-apha-100 py-10 mt-16">
        <div className="max-w-6xl mx-auto px-6 text-sm flex justify-between">
          <div>© {new Date().getFullYear()} APhA Clinical Assistant — Not affiliated with the American Pharmacists Association in this demo build.</div>
          <div className="flex gap-4">
            <Link to="/drug-ref/pricing" className="hover:text-white">Pricing</Link>
            <Link to="/drug-ref/login" className="hover:text-white">Log in</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

function Feature({ title, body }) {
  return (
    <div className="card">
      <h3 className="font-semibold text-lg mb-2 text-apha-700">{title}</h3>
      <p className="text-slate-600 text-sm leading-relaxed">{body}</p>
    </div>
  );
}

function Stat({ number, label }) {
  return (
    <div className="bg-white rounded-xl p-6 text-center shadow-sm">
      <div className="text-4xl font-bold text-apha">{number}</div>
      <div className="text-sm text-slate-600 mt-1">{label}</div>
    </div>
  );
}
