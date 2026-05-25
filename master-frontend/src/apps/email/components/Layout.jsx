import { NavLink } from "react-router-dom";

const NAV = [
  { to: "/email", label: "Dashboard" },
  { to: "/email/members", label: "Members" },
  { to: "/email/emails", label: "Email Sends" },
  { to: "/email/analytics", label: "Analytics" },
];

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-[#1B4F8A] text-white px-6 py-3 flex items-center gap-8 shadow">
        <span className="font-bold text-lg tracking-wide">APhA Email MVP</span>
        <div className="flex gap-6">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === "/email"}
              className={({ isActive }) =>
                isActive
                  ? "text-white font-semibold border-b-2 border-white pb-0.5"
                  : "text-blue-200 hover:text-white transition-colors"
              }
            >
              {n.label}
            </NavLink>
          ))}
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}
