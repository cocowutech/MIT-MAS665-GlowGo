'use client'

import { useRouter } from 'next/navigation'
import { Preference } from '@/types/chat'
import CalendarWidget from './CalendarWidget'

interface PreferenceSummaryProps {
  preferences: Preference
  readyToMatch: boolean
}

export default function PreferenceSummary({ preferences, readyToMatch }: PreferenceSummaryProps) {
  const router = useRouter()

  const handleSeeMatches = () => {
    router.push('/matches')
  }

  return (
    <div className="bg-gradient-to-b from-slate-50 to-white border-l border-slate-100 h-full overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white/90 backdrop-blur-md border-b border-slate-100 px-6 py-5 z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-rose-400 to-pink-500 rounded-xl flex items-center justify-center shadow-lg shadow-pink-200">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div>
            <h3 className="text-xl font-poppins font-bold text-slate-900 tracking-tight">
              Your Preferences
            </h3>
            <p className="text-sm text-slate-400 font-light">Curating your experience</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-5">
        {/* Preference Cards */}
        <div className="grid gap-4">
          {/* Service Type Card */}
          <div className="group bg-white rounded-2xl border border-slate-100 p-5 hover:border-pink-200 hover:shadow-lg hover:shadow-pink-50 transition-all duration-300">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-violet-100 to-purple-100 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <span className="text-2xl">✨</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-[0.15em] mb-1">Service</p>
                <p className="text-slate-900 font-bold text-xl truncate">
                  {preferences.service_type || (
                    <span className="text-slate-300 italic font-normal text-lg">Not specified</span>
                  )}
                </p>
              </div>
            </div>
          </div>

          {/* Budget Card */}
          <div className="group bg-white rounded-2xl border border-slate-100 p-5 hover:border-pink-200 hover:shadow-lg hover:shadow-pink-50 transition-all duration-300">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <span className="text-2xl">💰</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-[0.15em] mb-1">Budget</p>
                <p className="text-slate-900 font-bold text-xl">
                  {preferences.budget_min && preferences.budget_max ? (
                    `$${preferences.budget_min} - $${preferences.budget_max}`
                  ) : preferences.budget_max ? (
                    `Up to $${preferences.budget_max}`
                  ) : preferences.budget_min ? (
                    `From $${preferences.budget_min}`
                  ) : (
                    <span className="text-slate-300 italic font-normal text-lg">Not specified</span>
                  )}
                </p>
              </div>
            </div>
          </div>

          {/* Time Preferences Card */}
          <div className="group bg-white rounded-2xl border border-slate-100 p-5 hover:border-pink-200 hover:shadow-lg hover:shadow-pink-50 transition-all duration-300">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-sky-100 to-blue-100 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <span className="text-2xl">🕐</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-[0.15em] mb-1">When</p>
                <p className="text-slate-900 font-bold text-xl">
                  {(() => {
                    if (preferences.preferred_date) {
                      const [year, month, day] = preferences.preferred_date.split('-').map(Number)
                      const date = new Date(year, month - 1, day)
                      const dateStr = date.toLocaleDateString('en-US', {
                        weekday: 'short',
                        month: 'short',
                        day: 'numeric'
                      })

                      let timeDisplay = dateStr

                      if (preferences.preferred_time) {
                        const [hours, minutes] = preferences.preferred_time.split(':')
                        const hour = parseInt(hours)
                        const ampm = hour >= 12 ? 'PM' : 'AM'
                        const hour12 = hour % 12 || 12
                        timeDisplay += ` at ${hour12}:${minutes} ${ampm}`
                      }

                      if (preferences.time_constraint) {
                        if (preferences.time_constraint === 'before') {
                          timeDisplay = `Before ${timeDisplay}`
                        } else if (preferences.time_constraint === 'by') {
                          timeDisplay = `By ${timeDisplay}`
                        } else if (preferences.time_constraint === 'after') {
                          timeDisplay = `After ${timeDisplay}`
                        }
                      }

                      return timeDisplay
                    }

                    if (preferences.time_urgency) {
                      return <span className="capitalize">{preferences.time_urgency}</span>
                    }

                    return <span className="text-slate-300 italic font-normal text-lg">Not specified</span>
                  })()}
                </p>
              </div>
            </div>
          </div>

          {/* Location Card */}
          <div className="group bg-white rounded-2xl border border-slate-100 p-5 hover:border-pink-200 hover:shadow-lg hover:shadow-pink-50 transition-all duration-300">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-rose-100 to-pink-100 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <span className="text-2xl">📍</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-[0.15em] mb-1">Location</p>
                <p className="text-slate-900 font-bold text-xl truncate">
                  {preferences.location || (
                    <span className="text-slate-300 italic font-normal text-lg">Not specified</span>
                  )}
                </p>
              </div>
            </div>
          </div>

          {/* Provider Preference Card - Only show if specified */}
          {preferences.artisan_preference && (
            <div className="group bg-white rounded-2xl border border-slate-100 p-5 hover:border-pink-200 hover:shadow-lg hover:shadow-pink-50 transition-all duration-300">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-amber-100 to-orange-100 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                  <span className="text-2xl">👤</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-[0.15em] mb-1">Provider</p>
                  <p className="text-slate-900 font-bold text-xl truncate">
                    {preferences.artisan_preference}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Special Notes Card - Only show if specified */}
          {preferences.special_notes && (
            <div className="group bg-white rounded-2xl border border-slate-100 p-5 hover:border-pink-200 hover:shadow-lg hover:shadow-pink-50 transition-all duration-300">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-yellow-100 to-amber-100 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                  <span className="text-2xl">📝</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-[0.15em] mb-1">Notes</p>
                  <p className="text-slate-600 text-base leading-relaxed">
                    {preferences.special_notes}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Calendar Section */}
        <div className="pt-2">
          <CalendarWidget />
        </div>

        {/* Status & Action Section */}
        <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${readyToMatch ? 'bg-emerald-500' : 'bg-amber-400'} animate-pulse shadow-lg ${readyToMatch ? 'shadow-emerald-200' : 'shadow-amber-200'}`}></div>
              <span className="text-base font-semibold text-slate-600">Status</span>
            </div>
            <span className={`px-4 py-2 rounded-full text-sm font-bold ${
              readyToMatch
                ? 'bg-gradient-to-r from-emerald-50 to-teal-50 text-emerald-700 border border-emerald-200'
                : 'bg-gradient-to-r from-amber-50 to-yellow-50 text-amber-700 border border-amber-200'
            }`}>
              {readyToMatch ? '✓ Ready to Match' : 'Gathering info...'}
            </span>
          </div>

          {readyToMatch && (
            <button
              onClick={handleSeeMatches}
              className="w-full py-4 px-6 bg-gradient-to-r from-rose-500 via-pink-500 to-fuchsia-500 text-white text-lg font-bold rounded-2xl shadow-xl shadow-pink-200 hover:shadow-2xl hover:shadow-pink-300 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300"
            >
              <span className="flex items-center justify-center gap-3">
                <span>See Your Matches</span>
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
