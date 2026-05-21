import { Link, useNavigate } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();
  const token = localStorage.getItem("apha_token");

  const logout = () => {
    localStorage.removeItem("apha_token");
    navigate("/");
  };

  return (
    <header className="bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-apha flex items-center justify-center text-white font-bold">A</div>
          <div>
            <div className="text-lg font-bold text-apha-700">APhA Clinical Assistant</div>
            <div className="text-xs text-slate-500 -mt-0.5">Drug Reference for Pharmacists</div>
          </div>
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link to="/pricing" className="text-slate-600 hover:text-apha">Pricing</Link>
          {token ? (
            <>
              <Link to="/query" className="text-slate-600 hover:text-apha">Ask</Link>
              <Link to="/dashboard" className="text-slate-600 hover:text-apha">Dashboard</Link>
              <button onClick={logout} className="btn-secondary">Log out</button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-slate-600 hover:text-apha">Log in</Link>
              <Link to="/signup" className="btn-primary">Start free trial</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
