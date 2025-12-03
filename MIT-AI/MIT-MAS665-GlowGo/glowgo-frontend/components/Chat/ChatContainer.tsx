'use client'

import { useEffect, useRef } from 'react'
import { ChatMessage as ChatMessageType } from '@/types/chat'
import { Preference } from '@/types/chat'
import ChatMessage from './ChatMessage'
import PreferenceSummaryMessage from './PreferenceSummaryMessage'

interface ChatContainerProps {
  messages: ChatMessageType[]
  isLoading: boolean
  preferences: Preference
  readyToMatch: boolean
  onSeeMatches: () => void
  matchesLoading: boolean
}

export default function ChatContainer({
  messages,
  isLoading,
  preferences,
  readyToMatch,
  onSeeMatches,
  matchesLoading
}: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading, readyToMatch])

  // Empty state - Fashionista/Tech aesthetic
  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-10 bg-gradient-to-b from-slate-50/50 to-white">
        <div className="text-center max-w-xl">
          {/* Geometric accent */}
          <div className="relative mx-auto mb-10 w-32 h-32">
            <div className="absolute inset-0 bg-gradient-to-br from-rose-200 to-pink-300 rounded-[2rem] rotate-6 opacity-60"></div>
            <div className="absolute inset-0 bg-gradient-to-br from-rose-400 via-pink-500 to-fuchsia-500 rounded-[2rem] flex items-center justify-center shadow-2xl shadow-pink-200">
              <span className="text-5xl text-white">✦</span>
            </div>
          </div>

          <h2 className="text-4xl font-poppins font-bold text-slate-900 mb-5 tracking-tight">
            What brings you here today?
          </h2>
          <p className="text-slate-500 text-xl mb-10 leading-relaxed font-light">
            Your personal beauty concierge is ready to curate the perfect experience for you.
          </p>

          <div className="space-y-5">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-[0.2em]">Popular requests</p>
            <div className="flex flex-wrap gap-4 justify-center">
              <span className="px-6 py-3 bg-white border border-slate-200 rounded-2xl text-slate-700 text-lg font-medium shadow-sm hover:shadow-lg hover:border-pink-300 hover:scale-105 transition-all duration-300 cursor-default">
                ✂️ Fresh haircut
              </span>
              <span className="px-6 py-3 bg-white border border-slate-200 rounded-2xl text-slate-700 text-lg font-medium shadow-sm hover:shadow-lg hover:border-pink-300 hover:scale-105 transition-all duration-300 cursor-default">
                💆 Relaxing massage
              </span>
              <span className="px-6 py-3 bg-white border border-slate-200 rounded-2xl text-slate-700 text-lg font-medium shadow-sm hover:shadow-lg hover:border-pink-300 hover:scale-105 transition-all duration-300 cursor-default">
                💅 Nail artistry
              </span>
            </div>
          </div>

          {/* Decorative line */}
          <div className="mt-12 flex items-center justify-center gap-3">
            <div className="w-12 h-px bg-gradient-to-r from-transparent to-slate-200"></div>
            <div className="w-2 h-2 rounded-full bg-pink-300"></div>
            <div className="w-12 h-px bg-gradient-to-l from-transparent to-slate-200"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 md:p-8 bg-gradient-to-b from-slate-50/30 to-white">
      <div className="max-w-3xl mx-auto">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <ChatMessage
            message={{ role: 'assistant', content: '' }}
            isLoading={true}
          />
        )}

        {/* Preference Summary with See Matches button (shown when ready) */}
        {readyToMatch && !isLoading && (
          <PreferenceSummaryMessage
            preferences={preferences}
            onSeeMatches={onSeeMatches}
            matchesLoading={matchesLoading}
          />
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}
