import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMembers } from "../utils/api";

export default function MembersPage() {
  const [members, setMembers] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    getMembers({ limit: 200 }).then((r) => setMembers(r.data));
  }, []);

  const filtered = members.filter(
    (m) =>
      `${m.first_name} ${m.last_name} ${m.email}`.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Members</h1>
        <input
          placeholder="Search name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border rounded px-3 py-1.5 text-sm w-64"
        />
      </div>

      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 uppercase text-xs tracking-wide">
            <tr>
              {["Name", "Email", "Tier", "CPE Credits", "Webinars", "Portal Sessions", "Email Open Rate", ""].map(
                (h) => (
                  <th key={h} className="px-4 py-3 text-left font-medium">
                    {h}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.map((m) => (
              <tr key={m.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">
                  {m.first_name} {m.last_name}
                </td>
                <td className="px-4 py-3 text-gray-500">{m.email}</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs font-medium capitalize">
                    {m.tier}
                  </span>
                </td>
                <td className="px-4 py-3">{m.cpe_credits_ytd}</td>
                <td className="px-4 py-3">{m.webinars_attended_ytd}</td>
                <td className="px-4 py-3">{m.portal_sessions_last_30d}</td>
                <td className="px-4 py-3">{(m.email_open_rate * 100).toFixed(0)}%</td>
                <td className="px-4 py-3">
                  <Link
                    to={`/members/${m.id}`}
                    className="text-[#1B4F8A] hover:underline text-xs font-medium"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
