"""Google Calendar tools — list calendars, get/create/update/delete events."""

import json
from typing import Optional
from auth import get_service


def _cal():
    return get_service("calendar", "v3")


def calendar_list_calendars() -> str:
    """List all calendars the user has access to."""
    svc = _cal()
    result = svc.calendarList().list().execute()
    calendars = [{"id": c["id"], "summary": c.get("summary", ""), "primary": c.get("primary", False)}
                 for c in result.get("items", [])]
    return json.dumps(calendars, indent=2)


def calendar_get_events(calendar_id: str = "primary", time_min: str = "",
                        time_max: str = "", max_results: int = 25, query: str = "") -> str:
    """Get events from a calendar.

    Args:
        calendar_id: Calendar ID (default 'primary').
        time_min: Start of time range in RFC3339 format (e.g. '2026-03-29T00:00:00Z').
        time_max: End of time range in RFC3339 format.
        max_results: Maximum number of events to return.
        query: Free text search query.
    """
    svc = _cal()
    kwargs = {"calendarId": calendar_id, "maxResults": max_results, "singleEvents": True,
              "orderBy": "startTime"}
    if time_min:
        kwargs["timeMin"] = time_min
    if time_max:
        kwargs["timeMax"] = time_max
    if query:
        kwargs["q"] = query

    result = svc.events().list(**kwargs).execute()
    events = []
    for e in result.get("items", []):
        events.append({
            "id": e["id"],
            "summary": e.get("summary", "(no title)"),
            "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date", "")),
            "end": e.get("end", {}).get("dateTime", e.get("end", {}).get("date", "")),
            "location": e.get("location", ""),
            "description": e.get("description", ""),
            "attendees": [a.get("email", "") for a in e.get("attendees", [])],
            "status": e.get("status", ""),
            "htmlLink": e.get("htmlLink", ""),
        })
    return json.dumps(events, indent=2)


def calendar_create_event(summary: str, start: str, end: str, calendar_id: str = "primary",
                          description: str = "", location: str = "", attendees: list[str] = None,
                          timezone: str = "America/Toronto") -> str:
    """Create a new calendar event.

    Args:
        summary: Event title.
        start: Start datetime in RFC3339 format (e.g. '2026-03-30T10:00:00') or date for all-day ('2026-03-30').
        end: End datetime in RFC3339 format or date for all-day events.
        calendar_id: Calendar ID (default 'primary').
        description: Event description.
        location: Event location.
        attendees: List of attendee email addresses.
        timezone: Timezone (default America/Toronto).
    """
    svc = _cal()
    event = {"summary": summary}

    # Detect all-day vs timed event
    if "T" in start:
        event["start"] = {"dateTime": start, "timeZone": timezone}
        event["end"] = {"dateTime": end, "timeZone": timezone}
    else:
        event["start"] = {"date": start}
        event["end"] = {"date": end}

    if description:
        event["description"] = description
    if location:
        event["location"] = location
    if attendees:
        event["attendees"] = [{"email": a} for a in attendees]

    result = svc.events().insert(calendarId=calendar_id, body=event).execute()
    return json.dumps({"status": "created", "id": result["id"], "htmlLink": result.get("htmlLink", "")})


def calendar_update_event(event_id: str, calendar_id: str = "primary",
                          summary: str = "", start: str = "", end: str = "",
                          description: str = "", location: str = "",
                          timezone: str = "America/Toronto") -> str:
    """Update an existing calendar event.

    Args:
        event_id: The event ID to update.
        calendar_id: Calendar ID (default 'primary').
        summary: New event title (empty = no change).
        start: New start datetime (empty = no change).
        end: New end datetime (empty = no change).
        description: New description (empty = no change).
        location: New location (empty = no change).
        timezone: Timezone for the event.
    """
    svc = _cal()
    event = svc.events().get(calendarId=calendar_id, eventId=event_id).execute()

    if summary:
        event["summary"] = summary
    if start:
        if "T" in start:
            event["start"] = {"dateTime": start, "timeZone": timezone}
        else:
            event["start"] = {"date": start}
    if end:
        if "T" in end:
            event["end"] = {"dateTime": end, "timeZone": timezone}
        else:
            event["end"] = {"date": end}
    if description:
        event["description"] = description
    if location:
        event["location"] = location

    result = svc.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
    return json.dumps({"status": "updated", "id": result["id"]})


def calendar_delete_event(event_id: str, calendar_id: str = "primary") -> str:
    """Delete a calendar event.

    Args:
        event_id: The event ID to delete.
        calendar_id: Calendar ID (default 'primary').
    """
    svc = _cal()
    svc.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return json.dumps({"status": "deleted", "id": event_id})
