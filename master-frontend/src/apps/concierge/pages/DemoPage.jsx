import ChatWidget from '../components/ChatWidget'

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-[#EBF5FB]">
      {/* Simulated APhA Header */}
      <header className="bg-[#1B4F8A] text-white py-4 px-8 flex items-center justify-between">
        <div className="font-bold text-xl">pharmacist.com</div>
        <nav className="flex gap-6 text-sm">
          <a href="#" className="hover:underline">Membership</a>
          <a href="#" className="hover:underline">CPE</a>
          <a href="#" className="hover:underline">Publications</a>
          <a href="#" className="hover:underline">Events</a>
        </nav>
      </header>

      <main className="max-w-4xl mx-auto px-8 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-[#1B4F8A] mb-4">
            Join the American Pharmacists Association
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            APhA is the largest association of pharmacists in the US. Join 63,000+ members
            and get access to 300+ CPE hours, peer-reviewed journals, career resources, and more.
          </p>
        </div>

        <div className="grid grid-cols-3 gap-6 mb-12">
          {[
            { tier: 'Student', price: '~$50/yr', desc: 'For enrolled PharmD students' },
            { tier: 'Pharmacist', price: '~$195/yr', desc: 'For licensed practicing pharmacists' },
            { tier: 'Technician', price: '~$75/yr', desc: 'For pharmacy technicians' },
          ].map(t => (
            <div key={t.tier} className="bg-white rounded-2xl shadow-sm p-6 text-center border border-gray-100">
              <div className="font-bold text-lg text-gray-900">{t.tier}</div>
              <div className="text-2xl font-bold text-[#1B4F8A] my-2">{t.price}</div>
              <div className="text-sm text-gray-500">{t.desc}</div>
              <button className="mt-4 w-full border-2 border-[#1B4F8A] text-[#1B4F8A] py-2 rounded-lg font-semibold hover:bg-[#1B4F8A] hover:text-white transition text-sm">
                Join Now
              </button>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-2xl p-8 shadow-sm text-center">
          <div className="text-gray-500 text-sm">
            💬 Not sure which tier is right for you? Click the chat button in the bottom-right corner — our AI concierge can help!
          </div>
        </div>
      </main>

      <ChatWidget />
    </div>
  )
}
