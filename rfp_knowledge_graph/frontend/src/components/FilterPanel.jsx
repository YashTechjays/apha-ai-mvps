export default function FilterPanel({ filters, onChange }) {
  const update = (key, val) => onChange({ ...filters, [key]: val })

  return (
    <div className="flex flex-wrap gap-3 items-center">
      <input
        className="border rounded-lg px-3 py-2 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Search RFPs..."
        value={filters.q || ''}
        onChange={e => update('q', e.target.value)}
      />
      <select className="border rounded-lg px-3 py-2 text-sm"
        value={filters.status || ''}
        onChange={e => update('status', e.target.value)}>
        <option value="">All Statuses</option>
        <option value="open">Open</option>
        <option value="closed">Closed</option>
      </select>
      <select className="border rounded-lg px-3 py-2 text-sm"
        value={filters.state || ''}
        onChange={e => update('state', e.target.value)}>
        <option value="">All States</option>
        <option value="California">California</option>
        <option value="Texas">Texas</option>
        <option value="New York">New York</option>
        <option value="Ohio">Ohio</option>
        <option value="Georgia">Georgia</option>
        <option value="Michigan">Michigan</option>
        <option value="Montana">Montana</option>
        <option value="Virginia">Virginia</option>
        <option value="New Jersey">New Jersey</option>
        <option value="Kentucky">Kentucky</option>
        <option value="Illinois">Illinois</option>
        <option value="North Carolina">North Carolina</option>
        <option value="Massachusetts">Massachusetts</option>
        <option value="District of Columbia">DC</option>
      </select>
      <select className="border rounded-lg px-3 py-2 text-sm"
        value={filters.category || ''}
        onChange={e => update('category', e.target.value)}>
        <option value="">All Categories</option>
        <option value="pharmacy-services">Pharmacy Services</option>
        <option value="clinical-pharmacy">Clinical Pharmacy</option>
        <option value="consulting">Consulting</option>
        <option value="technology">Technology</option>
        <option value="public-health">Public Health</option>
        <option value="specialty-pharmacy">Specialty Pharmacy</option>
        <option value="hospital-pharmacy">Hospital Pharmacy</option>
        <option value="community-pharmacy">Community Pharmacy</option>
        <option value="compliance">Compliance</option>
        <option value="education">Education</option>
      </select>
    </div>
  )
}
