'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'

interface CalendarEvent {
  id: string
  summary: string
  start: string
  end: string
  description?: string
  location?: string
}

interface CalendarResponse {
  events: CalendarEvent[]
  connected: boolean
}

export default function CalendarWidget() {
  const { isAuthenticated, token } = useAuth()
  const [events, setEvents] = useState<CalendarEvent[]>([])
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(true)

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    if (!isAuthenticated || !token) {
      setLoading(false)
      return
    }

    const fetchCalendar = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/calendar/events`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const data: CalendarResponse = await response.json()
          setConnected(data.connected)
          setEvents(data.events)
        }
      } catch (error) {
        console.error('Error fetching calendar:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchCalendar()
  }, [isAuthenticated, token])

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
        <div className="animate-pulse">
          <div className="h-7 bg-slate-100 rounded-lg w-2/3 mb-5"></div>
          <div className="space-y-4">
            <div className="h-20 bg-slate-50 rounded-xl"></div>
            <div className="h-20 bg-slate-50 rounded-xl"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!connected) {
    return null
  }

  // Format time for display
  const formatEventTime = (startDate: Date, endDate: Date) => {
    const timeOptions: Intl.DateTimeFormatOptions = { hour: '2-digit', minute: '2-digit' }
    const startTime = startDate.toLocaleTimeString([], timeOptions)
    const endTime = endDate.toLocaleTimeString([], timeOptions)
    return `${startTime} - ${endTime}`
  }

  // Format date for display
  const formatEventDate = (date: Date) => {
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)

    if (date.toDateString() === today.toDateString()) {
      return 'Today'
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow'
    } else {
      return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
    }
  }

  // Group events by date
  const groupedEvents = events.reduce((groups: { [key: string]: CalendarEvent[] }, event) => {
    const date = new Date(event.start).toDateString()
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(event)
    return groups
  }, {})

  return (
    <div className="bg-white rounded-2xl border border-slate-100 overflow-hidden shadow-sm">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-50 via-pink-50/50 to-slate-50 px-6 py-5 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-violet-400 to-purple-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-200">
            <span className="text-white text-lg">📅</span>
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-lg tracking-tight">My Calendar</h3>
            <p className="text-xs text-slate-400 font-light">Your upcoming schedule</p>
          </div>
        </div>
      </div>

      {/* Events List */}
      <div className="p-5 max-h-96 overflow-y-auto">
        {events.length === 0 ? (
          <div className="text-center py-10">
            <div className="w-16 h-16 bg-gradient-to-br from-slate-100 to-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl opacity-40">📭</span>
            </div>
            <p className="text-base text-slate-400 font-medium">No upcoming events</p>
            <p className="text-sm text-slate-300 mt-1">Your calendar is clear!</p>
          </div>
        ) : (
          <div className="space-y-5">
            {Object.entries(groupedEvents).map(([dateStr, dateEvents]) => {
              const date = new Date(dateStr)
              return (
                <div key={dateStr}>
                  {/* Date Header */}
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-[0.15em]">
                      {formatEventDate(date)}
                    </span>
                    <div className="flex-1 h-px bg-gradient-to-r from-slate-200 to-transparent"></div>
                  </div>

                  {/* Events for this date */}
                  <div className="space-y-3">
                    {dateEvents.map(event => {
                      const startDate = new Date(event.start)
                      const endDate = new Date(event.end)

                      return (
                        <div
                          key={event.id}
                          className="group bg-gradient-to-r from-slate-50 to-white hover:from-pink-50 hover:to-white rounded-xl p-4 border-l-4 border-l-pink-400 transition-all duration-300 hover:shadow-md hover:shadow-pink-50"
                        >
                          <div className="font-semibold text-slate-800 text-base truncate group-hover:text-pink-700 transition-colors">
                            {event.summary}
                          </div>
                          <div className="flex items-center gap-2 mt-2">
                            <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span className="text-sm text-slate-500 font-medium">
                              {formatEventTime(startDate, endDate)}
                            </span>
                          </div>
                          {event.location && (
                            <div className="flex items-center gap-2 mt-1.5">
                              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                              </svg>
                              <span className="text-sm text-slate-400 truncate">{event.location}</span>
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      {events.length > 0 && (
        <div className="bg-gradient-to-r from-slate-50 to-white px-5 py-3 border-t border-slate-100">
          <p className="text-sm text-slate-400 text-center font-medium">
            Showing next {events.length} event{events.length > 1 ? 's' : ''}
          </p>
        </div>
      )}
    </div>
  )
}
