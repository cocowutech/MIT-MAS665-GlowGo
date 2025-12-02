"""
Google Calendar Tool for GlowGo
Allows checking user's calendar for availability with smart time suggestions
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import pytz
from crewai.tools import BaseTool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

from models.database import SessionLocal
from models.user import User

logger = logging.getLogger(__name__)

# Service duration estimates in minutes
SERVICE_DURATIONS = {
    "haircut": 60,
    "nails": 45,
    "manicure": 30,
    "pedicure": 45,
    "massage": 90,
    "facial": 60,
    "waxing": 30,
    "makeup": 45,
    "spa": 120,
    "default": 60
}

# Keywords indicating important events where looking good matters
IMPORTANT_EVENT_KEYWORDS = [
    # Professional
    "meeting", "interview", "presentation", "conference", "pitch",
    "client", "networking", "board meeting", "review", "demo",
    # Social - high visibility
    "wedding", "baby shower", "bridal shower", "birthday party",
    "engagement", "anniversary", "graduation", "gala", "fundraiser",
    "date", "date night", "dinner party", "reception",
    # Competitive/Performance
    "competition", "recital", "performance", "photoshoot", "photo",
    "video", "recording", "audition", "show",
    # Family/Important gatherings
    "family dinner", "reunion", "holiday", "thanksgiving", "christmas",
    "easter", "passover", "new year", "party"
]


class GoogleCalendarTool(BaseTool):
    """
    Tool for checking user's Google Calendar availability
    """

    name: str = "google_calendar_check"
    description: str = """
    Check user's Google Calendar for availability on a specific date/time.
    Input should be a JSON with:
    - user_id: The ID of the user
    - date: ISO format date string (YYYY-MM-DD)
    - time: Optional time string (HH:MM)
    
    Returns free/busy slots around the requested time.
    """

    def _run(self, input_data: Dict[str, Any]) -> str:
        """Check calendar availability"""
        db = SessionLocal()
        try:
            # Parse input
            user_id = input_data.get("user_id")
            date_str = input_data.get("date")
            time_str = input_data.get("time")
            
            if not user_id:
                return "Error: User ID is required"
                
            # Get user and token
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.google_access_token:
                return "Error: User has not connected their Google Calendar"
                
            # Create credentials
            creds = Credentials(token=user.google_access_token)
            service = build('calendar', 'v3', credentials=creds)
            
            # Calculate time range
            target_date = datetime.fromisoformat(date_str)
            
            # If specific time provided, check +/- 2 hours
            # If no time, check whole day (9am-9pm)
            if time_str:
                target_time = datetime.strptime(time_str, "%H:%M").time()
                start_dt = datetime.combine(target_date.date(), target_time) - timedelta(hours=2)
                end_dt = datetime.combine(target_date.date(), target_time) + timedelta(hours=2)
            else:
                start_dt = datetime.combine(target_date.date(), datetime.strptime("09:00", "%H:%M").time())
                end_dt = datetime.combine(target_date.date(), datetime.strptime("21:00", "%H:%M").time())
            
            # Convert to UTC isoformat for API
            # Assuming EST for now, in production should store user's timezone
            tz = pytz.timezone('America/New_York')
            start_iso = tz.localize(start_dt).isoformat()
            end_iso = tz.localize(end_dt).isoformat()
            
            # Query free/busy
            body = {
                "timeMin": start_iso,
                "timeMax": end_iso,
                "timeZone": "America/New_York",
                "items": [{"id": "primary"}]
            }
            
            events_result = service.freebusy().query(body=body).execute()
            calendars = events_result.get('calendars', {})
            primary = calendars.get('primary', {})
            busy_slots = primary.get('busy', [])
            
            if not busy_slots:
                return f"Great news! Your calendar is completely free on {date_str} between {start_dt.strftime('%I:%M %p')} and {end_dt.strftime('%I:%M %p')}."
                
            # Format busy slots for the agent
            busy_text = []
            for slot in busy_slots:
                start = datetime.fromisoformat(slot['start']).strftime('%I:%M %p')
                end = datetime.fromisoformat(slot['end']).strftime('%I:%M %p')
                busy_text.append(f"{start} - {end}")
                
            return f"You have the following events on your calendar:\n" + "\n".join(busy_text)

        except Exception as e:
            logger.error(f"Calendar check error: {e}")
            return f"Error checking calendar: {str(e)}"
        finally:
            db.close()

google_calendar_tool = GoogleCalendarTool()


async def analyze_calendar_for_smart_suggestions(
    user_id: str,
    service_type: str,
    target_date: Optional[str] = None,
    llm = None
) -> Dict[str, Any]:
    """
    Analyze user's calendar to provide smart time suggestions for appointments.

    Features:
    1. Finds gaps between events with buffer time
    2. Detects important upcoming events and suggests day-before appointments
    3. Prioritizes daytime slots (9am-6pm)
    4. Considers service duration + travel buffer

    Args:
        user_id: User's ID to fetch calendar
        service_type: Type of service to estimate duration
        target_date: Optional specific date (YYYY-MM-DD), defaults to next 7 days
        llm: Optional LLM for advanced event importance detection

    Returns:
        Dict with suggested_slots, important_events, and reasoning
    """
    db = SessionLocal()
    result = {
        "has_calendar": False,
        "suggested_slots": [],
        "important_events": [],
        "day_before_suggestions": [],
        "events_on_date": [],
        "reasoning": "",
        "smart_suggestion": ""
    }

    try:
        # Get user and token
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.google_access_token:
            result["reasoning"] = "User has not connected their Google Calendar"
            return result

        result["has_calendar"] = True

        # Create credentials
        creds = Credentials(token=user.google_access_token)
        service = build('calendar', 'v3', credentials=creds)

        # Get service duration
        service_duration = SERVICE_DURATIONS.get(service_type.lower(), SERVICE_DURATIONS["default"])
        buffer_time = 30  # 30 minutes before and after
        total_time_needed = service_duration + (buffer_time * 2)  # service + buffer before + after

        # Timezone
        tz = pytz.timezone('America/New_York')
        now = datetime.now(tz)

        # Determine date range
        if target_date:
            start_date = datetime.fromisoformat(target_date)
            start_date = tz.localize(start_date.replace(hour=0, minute=0, second=0))
            end_date = start_date + timedelta(days=1)
        else:
            # Look at next 7 days
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)

        # Fetch actual events (not just free/busy) to get event names
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat(),
            timeMax=end_date.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # Process events - ONLY include future events
        processed_events = []
        important_events = []

        print(f"[CalendarAnalysis] Current time: {now.strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"[CalendarAnalysis] Found {len(events)} total events, filtering for future events...")

        for event in events:
            event_start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
            event_end = event.get('end', {}).get('dateTime') or event.get('end', {}).get('date')
            event_name = event.get('summary', 'Busy')

            if not event_start:
                continue

            # Parse datetime
            try:
                if 'T' in event_start:
                    start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                    # Ensure timezone awareness
                    if start_dt.tzinfo is None:
                        start_dt = tz.localize(start_dt)
                else:
                    # All-day event
                    start_dt = tz.localize(datetime.fromisoformat(event_start))

                if 'T' in event_end:
                    end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
                    if end_dt.tzinfo is None:
                        end_dt = tz.localize(end_dt)
                else:
                    end_dt = tz.localize(datetime.fromisoformat(event_end))
            except Exception as e:
                print(f"[CalendarAnalysis] Error parsing event '{event_name}': {e}")
                continue

            # SKIP events that have already ended
            if end_dt < now:
                print(f"[CalendarAnalysis] Skipping past event: {event_name} (ended {end_dt.strftime('%Y-%m-%d %H:%M')})")
                continue

            print(f"[CalendarAnalysis] Future event: {event_name} at {start_dt.strftime('%Y-%m-%d %H:%M')}")

            processed_events.append({
                "name": event_name,
                "start": start_dt,
                "end": end_dt,
                "location": event.get('location', '')
            })

            # Check if this is an important event (only for future events)
            event_name_lower = event_name.lower()
            is_important = any(kw in event_name_lower for kw in IMPORTANT_EVENT_KEYWORDS)

            if is_important:
                important_events.append({
                    "name": event_name,
                    "date": start_dt.strftime("%A, %B %d"),
                    "time": start_dt.strftime("%I:%M %p"),
                    "start_dt": start_dt,  # Keep datetime for comparison
                    "why_important": _get_importance_reason(event_name_lower)
                })
                print(f"[CalendarAnalysis] Important event detected: {event_name} on {start_dt.strftime('%A, %B %d')}")

        result["important_events"] = important_events

        # If we have a target date, find events on that date
        if target_date:
            result["events_on_date"] = [
                {
                    "name": e["name"],
                    "start_time": e["start"].strftime("%I:%M %p"),
                    "end_time": e["end"].strftime("%I:%M %p"),
                    "location": e.get("location", "")
                }
                for e in processed_events
            ]

        # Find available slots
        available_slots = _find_available_slots(
            processed_events,
            target_date,
            total_time_needed,
            buffer_time,
            tz
        )

        result["suggested_slots"] = available_slots

        # Generate day-before suggestions for important events (only future ones)
        for important_event in important_events:
            # Use the actual datetime we stored, not the formatted string
            event_start = important_event.get("start_dt")
            if not event_start:
                continue

            # Only suggest day-before if event is at least 1 day away
            if event_start - now < timedelta(hours=24):
                print(f"[CalendarAnalysis] Skipping day-before suggestion for {important_event['name']} - event is less than 24 hours away")
                continue

            day_before = event_start - timedelta(days=1)

            # Find events on the day before to suggest a good time slot
            day_before_events = [e for e in processed_events if e["start"].date() == day_before.date()]
            day_before_events.sort(key=lambda x: x["start"])

            # Find the best available slot on the day before
            suggested_time = _find_best_slot_for_day(
                day_before,
                day_before_events,
                total_time_needed,
                buffer_time,
                tz,
                now
            )

            result["day_before_suggestions"].append({
                "event_name": important_event["name"],
                "event_date": important_event["date"],
                "suggested_day": day_before.strftime("%A, %B %d"),
                "suggested_time": suggested_time,
                "reason": f"Get your {service_type} done before {important_event['name']} so you look your best!"
            })
            print(f"[CalendarAnalysis] Day-before suggestion: {service_type} on {day_before.strftime('%A, %B %d')} at {suggested_time} before {important_event['name']}")

        # Build smart suggestion text
        result["smart_suggestion"] = _build_smart_suggestion(
            result,
            service_type,
            service_duration,
            target_date
        )

        return result

    except Exception as e:
        logger.error(f"Calendar analysis error: {e}", exc_info=True)
        result["reasoning"] = f"Error analyzing calendar: {str(e)}"
        return result
    finally:
        db.close()


def _find_best_slot_for_day(
    target_day: datetime,
    events_on_day: List[Dict],
    total_time_needed: int,
    buffer_time: int,
    tz,
    now: datetime
) -> str:
    """
    Find the best available time slot on a specific day, considering existing events.

    Prioritizes:
    1. Morning/early afternoon (10am-2pm) - ideal for beauty before big events
    2. Gaps between events that fit the service + buffer time
    3. Falls back to any available slot

    Returns a formatted time string like "11:00 AM" or "2:30 PM"
    """
    # Business hours
    day_start_hour = 9
    day_end_hour = 19

    # Preferred hours for beauty services before big events (gives time to get ready after)
    preferred_hours = [10, 11, 12, 13, 14]  # 10am - 2pm

    day_start = tz.localize(target_day.replace(hour=day_start_hour, minute=0, second=0, microsecond=0, tzinfo=None))
    day_end = tz.localize(target_day.replace(hour=day_end_hour, minute=0, second=0, microsecond=0, tzinfo=None))

    # If the day is today, start from now + 1 hour minimum
    if target_day.date() == now.date():
        earliest_start = now + timedelta(hours=1)
        if earliest_start > day_start:
            day_start = earliest_start

    if not events_on_day:
        # No events - pick preferred time (11 AM is ideal)
        return "11:00 AM"

    # Build list of busy periods (with buffer)
    busy_periods = []
    for event in events_on_day:
        event_start = event["start"] - timedelta(minutes=buffer_time)
        event_end = event["end"] + timedelta(minutes=buffer_time)
        busy_periods.append((event_start, event_end))

    # Sort by start time
    busy_periods.sort(key=lambda x: x[0])

    # Find available slots
    available_slots = []

    # Check before first event
    if busy_periods[0][0] > day_start:
        gap_minutes = (busy_periods[0][0] - day_start).total_seconds() / 60
        if gap_minutes >= total_time_needed:
            available_slots.append({
                "start": day_start,
                "end": busy_periods[0][0],
                "minutes": gap_minutes
            })

    # Check between events
    for i in range(len(busy_periods) - 1):
        gap_start = busy_periods[i][1]
        gap_end = busy_periods[i + 1][0]
        gap_minutes = (gap_end - gap_start).total_seconds() / 60

        if gap_minutes >= total_time_needed:
            available_slots.append({
                "start": gap_start,
                "end": gap_end,
                "minutes": gap_minutes
            })

    # Check after last event
    if busy_periods[-1][1] < day_end:
        gap_minutes = (day_end - busy_periods[-1][1]).total_seconds() / 60
        if gap_minutes >= total_time_needed:
            available_slots.append({
                "start": busy_periods[-1][1],
                "end": day_end,
                "minutes": gap_minutes
            })

    if not available_slots:
        # No slots available - return None or a fallback
        print(f"[CalendarAnalysis] No available slots found on {target_day.strftime('%A, %B %d')}")
        return "No available time"

    # Find slot that contains preferred hours
    for slot in available_slots:
        slot_start_hour = slot["start"].hour
        slot_end_hour = slot["end"].hour

        for preferred_hour in preferred_hours:
            if slot_start_hour <= preferred_hour < slot_end_hour:
                # This slot contains a preferred hour
                suggested_dt = slot["start"].replace(hour=preferred_hour, minute=0)
                # Make sure it's actually within the slot
                if suggested_dt >= slot["start"] and suggested_dt < slot["end"]:
                    return suggested_dt.strftime("%I:%M %p").lstrip("0")

    # No preferred hours available - use the start of the first available slot
    first_slot = available_slots[0]
    # Round up to nearest 30 minutes
    suggested_minute = 0 if first_slot["start"].minute < 30 else 30
    if first_slot["start"].minute > 30:
        suggested_dt = first_slot["start"].replace(minute=0) + timedelta(hours=1)
    else:
        suggested_dt = first_slot["start"].replace(minute=suggested_minute)

    return suggested_dt.strftime("%I:%M %p").lstrip("0")


def _get_importance_reason(event_name_lower: str) -> str:
    """Determine why an event is important based on keywords"""
    if any(kw in event_name_lower for kw in ["wedding", "bridal", "engagement"]):
        return "Special celebration where you'll want to look your absolute best"
    elif any(kw in event_name_lower for kw in ["interview", "pitch", "client", "board"]):
        return "Professional event where first impressions matter"
    elif any(kw in event_name_lower for kw in ["date", "anniversary"]):
        return "Romantic occasion where looking great is a must"
    elif any(kw in event_name_lower for kw in ["photo", "video", "performance"]):
        return "You'll be photographed or on camera"
    elif any(kw in event_name_lower for kw in ["party", "gala", "dinner"]):
        return "Social event with many people"
    elif any(kw in event_name_lower for kw in ["meeting", "conference", "presentation"]):
        return "Professional gathering where you'll meet important people"
    else:
        return "Important event where looking polished matters"


def _find_available_slots(
    events: List[Dict],
    target_date: Optional[str],
    total_time_needed: int,
    buffer_time: int,
    tz
) -> List[Dict[str, Any]]:
    """Find available time slots between events"""
    slots = []
    now = datetime.now(tz)

    # Define business hours (9am - 7pm)
    business_start = 9
    business_end = 19

    # If target_date specified, only look at that day
    if target_date:
        target = datetime.fromisoformat(target_date)
        target = tz.localize(target.replace(hour=0, minute=0, second=0))

        # Filter events for target date
        day_events = [e for e in events if e["start"].date() == target.date()]

        # Sort by start time
        day_events.sort(key=lambda x: x["start"])

        # Check slot before first event
        day_start = target.replace(hour=business_start, minute=0)
        if now.date() == target.date() and now.hour >= business_start:
            day_start = now + timedelta(minutes=30)  # At least 30 min from now

        if day_events:
            first_event_start = day_events[0]["start"] - timedelta(minutes=buffer_time)
            gap = (first_event_start - day_start).total_seconds() / 60

            if gap >= total_time_needed:
                slots.append({
                    "start_time": day_start.strftime("%I:%M %p"),
                    "end_time": first_event_start.strftime("%I:%M %p"),
                    "date": target.strftime("%A, %B %d"),
                    "type": "before_first_event",
                    "note": f"Before your {day_events[0]['name']}"
                })

            # Check gaps between events
            for i in range(len(day_events) - 1):
                current_end = day_events[i]["end"] + timedelta(minutes=buffer_time)
                next_start = day_events[i + 1]["start"] - timedelta(minutes=buffer_time)

                gap = (next_start - current_end).total_seconds() / 60

                if gap >= total_time_needed:
                    slots.append({
                        "start_time": current_end.strftime("%I:%M %p"),
                        "end_time": next_start.strftime("%I:%M %p"),
                        "date": target.strftime("%A, %B %d"),
                        "type": "between_events",
                        "note": f"Between {day_events[i]['name']} and {day_events[i + 1]['name']}"
                    })

            # Check slot after last event
            last_event_end = day_events[-1]["end"] + timedelta(minutes=buffer_time)
            day_end = target.replace(hour=business_end, minute=0)

            gap = (day_end - last_event_end).total_seconds() / 60

            if gap >= total_time_needed:
                slots.append({
                    "start_time": last_event_end.strftime("%I:%M %p"),
                    "end_time": day_end.strftime("%I:%M %p"),
                    "date": target.strftime("%A, %B %d"),
                    "type": "after_last_event",
                    "note": f"After your {day_events[-1]['name']}"
                })
        else:
            # No events - whole day available
            slots.append({
                "start_time": day_start.strftime("%I:%M %p"),
                "end_time": target.replace(hour=business_end, minute=0).strftime("%I:%M %p"),
                "date": target.strftime("%A, %B %d"),
                "type": "free_day",
                "note": "Your calendar is free this day!"
            })

    return slots


async def detect_important_events_with_llm(
    events: List[Dict[str, Any]],
    llm
) -> List[Dict[str, Any]]:
    """
    Use LLM to intelligently detect which events are important for looking good.

    The LLM considers:
    - Events where you'll meet important people
    - Events where you'll be photographed
    - Professional events with clients/bosses
    - Social events where appearance matters
    """
    if not events or not llm:
        return []

    # Prepare event list for LLM
    event_list = "\n".join([
        f"- {e['name']} on {e.get('date', 'unknown date')} at {e.get('time', 'unknown time')}"
        for e in events[:10]  # Limit to 10 events
    ])

    prompt = f"""Analyze these upcoming calendar events and identify which ones are "important appearance events"
where the person would want to look their best (get a haircut, nails done, etc. beforehand).

Events:
{event_list}

For each important event, return a JSON array with objects containing:
- "name": the event name
- "importance_score": 1-10 (10 = most important to look good)
- "reason": why this event matters for appearance

Consider events like:
- Weddings, parties, galas (9-10)
- Client meetings, interviews, presentations (8-9)
- Dates, romantic dinners (8-9)
- Photo shoots, videos, performances (9-10)
- Family gatherings, reunions (7-8)
- Regular work meetings (5-6)

Return ONLY the JSON array, no other text. If no important events, return [].
Example: [{{"name": "Wedding", "importance_score": 10, "reason": "Special celebration where looking your best matters"}}]"""

    try:
        response = await llm.ainvoke(prompt)
        result_text = response.content.strip()

        # Parse JSON response
        import json
        # Handle potential markdown code blocks
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()

        important_events = json.loads(result_text)
        return important_events

    except Exception as e:
        logger.error(f"LLM event detection error: {e}")
        return []


def _build_smart_suggestion(
    analysis: Dict[str, Any],
    service_type: str,
    service_duration: int,
    target_date: Optional[str]
) -> str:
    """Build a natural language smart suggestion based on calendar analysis"""

    if not analysis.get("has_calendar"):
        return ""

    suggestion_parts = []

    # If there are events on the target date
    if target_date and analysis.get("events_on_date"):
        events = analysis["events_on_date"]
        if len(events) == 1:
            e = events[0]
            suggestion_parts.append(
                f"I see you have {e['name']} at {e['start_time']}."
            )
        elif len(events) == 2:
            e1, e2 = events[0], events[1]
            suggestion_parts.append(
                f"I see from your calendar you have {e1['name']} at {e1['start_time']}, "
                f"and {e2['name']} at {e2['start_time']}."
            )
        else:
            first = events[0]
            suggestion_parts.append(
                f"I see you have {len(events)} events that day, starting with {first['name']} at {first['start_time']}."
            )

    # Suggest available slots
    if analysis.get("suggested_slots"):
        slots = analysis["suggested_slots"]
        if slots[0]["type"] == "between_events":
            slot = slots[0]
            suggestion_parts.append(
                f"How about between your appointments? {slot['start_time']} to {slot['end_time']} "
                f"would give you enough time for your {service_type} with buffer time to spare!"
            )
        elif slots[0]["type"] == "free_day":
            suggestion_parts.append(
                f"Your calendar is free that day! I'd suggest late morning or early afternoon "
                f"when you have plenty of time to enjoy your {service_type}."
            )
        elif len(slots) > 0:
            slot = slots[0]
            suggestion_parts.append(
                f"I'd suggest around {slot['start_time']} - {slot['note'].lower()}."
            )

    # Mention important upcoming events - suggest DAY BEFORE with concrete time
    if analysis.get("day_before_suggestions"):
        important = analysis["day_before_suggestions"][0]

        # Get suggested time from the day_before_suggestion if available, otherwise use smart default
        suggested_time = important.get("suggested_time", "11:00 AM")

        suggestion_parts.append(
            f"\n\n💡 I noticed you have {important['event_name']} on {important['event_date']}! "
            f"How about getting your {service_type} done the day before on {important['suggested_day']} around {suggested_time}? "
            f"That way you'll look fresh and have plenty of time to get ready for your big event!"
        )

    return " ".join(suggestion_parts)


