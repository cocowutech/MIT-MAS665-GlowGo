'use client'

import { ChatMessage as ChatMessageType } from '@/types/chat'

interface ChatMessageProps {
  message: ChatMessageType
  isLoading?: boolean
}

export default function ChatMessage({ message, isLoading = false }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 animate-fade-in`}>
      <div className={`flex items-end gap-3 max-w-[80%] ${isUser ? 'flex-row-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`w-10 h-10 rounded-2xl flex-shrink-0 flex items-center justify-center shadow-md ${
          isUser
            ? 'bg-gradient-to-br from-slate-100 to-slate-200 ring-1 ring-slate-200'
            : 'bg-gradient-to-br from-rose-400 via-pink-500 to-fuchsia-500 ring-1 ring-pink-300'
        }`}>
          {isUser ? (
            <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          ) : (
            <span className="text-white text-lg">✦</span>
          )}
        </div>

        {/* Message Bubble */}
        <div
          className={`px-5 py-4 shadow-sm ${
            isUser
              ? 'bg-gradient-to-br from-rose-400 to-pink-500 text-white rounded-3xl rounded-br-lg'
              : 'bg-white border border-slate-100 text-slate-800 rounded-3xl rounded-bl-lg'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2 px-3 py-2">
              <div className="w-2.5 h-2.5 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2.5 h-2.5 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2.5 h-2.5 bg-slate-300 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          ) : (
            <p className={`text-[17px] leading-relaxed whitespace-pre-wrap break-words font-medium ${
              isUser ? 'text-white' : 'text-slate-700'
            }`}>
              {message.content}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
