export default function ChatMessage({ role, content }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-[#1B4F8A] flex items-center justify-center text-white text-xs font-bold mr-2 mt-1 shrink-0">
          A
        </div>
      )}
      <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm whitespace-pre-wrap ${
        isUser
          ? 'bg-[#1B4F8A] text-white rounded-br-none'
          : 'bg-white text-gray-800 rounded-bl-none'
      }`}>
        {content}
      </div>
    </div>
  )
}
