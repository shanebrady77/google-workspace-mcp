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
                          timezone: str = "America/Toronto", add_google_meet: bool = False) -> str:
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
        add_google_meet: If True, automatically creates a Google Meet video conference link.
    """
    import uuid

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
    if add_google_meet:
        event["conferenceData"] = {
            "createRequest": {
                "requestId": uuid.uuid4().hex,
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        }

    result = svc.events().insert(
        calendarId=calendar_id, body=event,
        conferenceDataVersion=1 if add_google_meet else 0
    ).execute()

    out = {"status": "created", "id": result["id"], "htmlLink": result.get("htmlLink", "")}
    # Include Meet link if generated
    conf = result.get("conferenceData", {})
    if conf:
        for ep in conf.get("entryPoints", []):
            if ep.get("entryPointType") == "video":
                out["meetLink"] = ep.get("uri", "")
                break
    return json.dumps(out)


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


def calendar_freebusy(time_min: str, time_max: str, calendars: list[str] = None,
                      timezone: str = "America/Toronto") -> str:
    """Query free/busy information for calendars.

    Args:
        time_min: Start of range in RFC3339 format (e.g. '2026-04-06T09:00:00').
        time_max: End of range in RFC3339 format.
        calendars: List of calendar IDs to check (default ['primary']).
        timezone: Timezone for the query.
    """
    svc = _cal()
    cal_ids = calendars or ["primary"]
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "timeZone": timezone,
        "items": [{"id": c} for c in cal_ids],
    }
    result = svc.freebusy().query(body=body).execute()
    output = {}
    for cal_id, data in result.get("calendars", {}).items():
        output[cal_id] = {
            "busy": data.get("busy", []),
            "errors": data.get("errors", []),
        }
    return json.dumps(output, indent=2)


def calendar_list_recurring_instances(event_id: str, calendar_id: str = "primary",
                                      time_min: str = "", time_max: str = "",
                                      max_results: int = 25) -> str:
    """List instances of a recurring event.

    Args:
        event_id: The recurring event ID.
        calendar_id: Calendar ID (default 'primary').
        time_min: Start of range in RFC3339 format (optional).
        time_max: End of range in RFC3339 format (optional).
        max_results: Maximum instances to return.
    """
    svc = _cal()
    kwargs = {"calendarId": calendar_id, "eventId": event_id, "maxResults": max_results}
    if time_min:
        kwargs["timeMin"] = time_min
    if time_max:
        kwargs["timeMax"] = time_max

    result = svc.events().instances(**kwargs).execute()
    instances = []
    for e in result.get("items", []):
        instances.append({
            "id": e["id"],
            "summary": e.get("summary", ""),
            "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date", "")),
            "end": e.get("end", {}).get("dateTime", e.get("end", {}).get("date", "")),
            "status": e.get("status", ""),
        })
    return json.dumps(instances, indent=2)


def calendar_quick_add(text: str, calendar_id: str = "primary") -> str:
    """Create an event from natural language text (like Google Calendar's Quick Add).

    Args:
        text: Natural language event description (e.g. 'Lunch with John tomorrow at noon').
        calendar_id: Calendar ID (default 'primary').
    """
    svc = _cal()
    result = svc.events().quickAdd(calendarId=calendar_id, text=text).execute()
    return json.dumps({
        "status": "created",
        "id": result["id"],
        "summary": result.get("summary", ""),
        "start": result.get("start", {}).get("dateTime", result.get("start", {}).get("date", "")),
        "htmlLink": result.get("htmlLink", ""),
    })
