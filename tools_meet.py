"""Google Meet tools — create spaces, get space info, list participants, get artifacts."""

import json
from auth import get_service


def _meet():
    return get_service("meet", "v2")


def meet_create_space() -> str:
    """Create a new Google Meet meeting space. Returns the space name, meeting URI, and meeting code."""
    svc = _meet()
    result = svc.spaces().create(body={}).execute()
    return json.dumps({
        "status": "created",
        "name": result.get("name", ""),
        "meetingUri": result.get("meetingUri", ""),
        "meetingCode": result.get("meetingCode", ""),
        "config": result.get("config", {}),
    }, indent=2)


def meet_get_space(space_name: str) -> str:
    """Get details about a Google Meet meeting space.

    Args:
        space_name: The resource name of the space (e.g. 'spaces/abc-defg-hij').
    """
    svc = _meet()
    result = svc.spaces().get(name=space_name).execute()
    return json.dumps({
        "name": result.get("name", ""),
        "meetingUri": result.get("meetingUri", ""),
        "meetingCode": result.get("meetingCode", ""),
        "config": result.get("config", {}),
        "activeConference": result.get("activeConference", {}),
    }, indent=2)


def meet_list_participants(conference_record_name: str) -> str:
    """List participants and their sessions for a conference record.

    Args:
        conference_record_name: The conference record resource name
            (e.g. 'conferenceRecords/abc-defg-hij'). Get this from meet_get_space's activeConference field
            or from the Meet API conference records.
    """
    svc = _meet()
    result = svc.conferenceRecords().participants().list(
        parent=conference_record_name
    ).execute()

    participants = []
    for p in result.get("participants", []):
        participant = {
            "name": p.get("name", ""),
            "earliestStartTime": p.get("earliestStartTime", ""),
            "latestEndTime": p.get("latestEndTime", ""),
        }
        # Get signer info if available
        if "signedinUser" in p:
            participant["user"] = p["signedinUser"].get("displayName", p["signedinUser"].get("user", ""))
        elif "anonymousUser" in p:
            participant["user"] = p["anonymousUser"].get("displayName", "Anonymous")
        elif "phoneUser" in p:
            participant["user"] = p["phoneUser"].get("displayName", "Phone user")
        participants.append(participant)

    return json.dumps({"total": len(participants), "participants": participants}, indent=2)


def meet_get_artifacts(conference_record_name: str) -> str:
    """Get recordings, transcripts, and transcript entries for a conference record.

    Args:
        conference_record_name: The conference record resource name
            (e.g. 'conferenceRecords/abc-defg-hij').
    """
    svc = _meet()
    output = {"conferenceRecord": conference_record_name, "recordings": [], "transcripts": []}

    # Get recordings
    try:
        rec_result = svc.conferenceRecords().recordings().list(
            parent=conference_record_name
        ).execute()
        for r in rec_result.get("recordings", []):
            output["recordings"].append({
                "name": r.get("name", ""),
                "state": r.get("state", ""),
                "startTime": r.get("startTime", ""),
                "endTime": r.get("endTime", ""),
                "driveDestination": r.get("driveDestination", {}),
            })
    except Exception as e:
        output["recordings_error"] = str(e)

    # Get transcripts
    try:
        trans_result = svc.conferenceRecords().transcripts().list(
            parent=conference_record_name
        ).execute()
        for t in trans_result.get("transcripts", []):
            transcript = {
                "name": t.get("name", ""),
                "state": t.get("state", ""),
                "startTime": t.get("startTime", ""),
                "endTime": t.get("endTime", ""),
                "docsDestination": t.get("docsDestination", {}),
            }
            # Get transcript entries
            try:
                entries_result = svc.conferenceRecords().transcripts().entries().list(
                    parent=t["name"]
                ).execute()
                transcript["entries"] = [
                    {
                        "participant": e.get("participantName", ""),
                        "text": e.get("text", ""),
                        "startTime": e.get("startTime", ""),
                        "endTime": e.get("endTime", ""),
                        "languageCode": e.get("languageCode", ""),
                    }
                    for e in entries_result.get("transcriptEntries", [])
                ]
            except Exception:
                transcript["entries"] = []
            output["transcripts"].append(transcript)
    except Exception as e:
        output["transcripts_error"] = str(e)

    return json.dumps(output, indent=2)


def meet_end_conference(space_name: str) -> str:
    """End an active conference in a meeting space.

    Args:
        space_name: The space resource name (e.g. 'spaces/abc-defg-hij').
    """
    svc = _meet()
    result = svc.spaces().endActiveConference(name=space_name, body={}).execute()
    return json.dumps({"status": "conference_ended", "space": space_name})


def meet_list_conference_records(max_results: int = 25) -> str:
    """List past conference records (meeting history).

    Args:
        max_results: Maximum records to return.
    """
    svc = _meet()
    result = svc.conferenceRecords().list(pageSize=max_results).execute()
    records = []
    for r in result.get("conferenceRecords", []):
        records.append({
            "name": r.get("name", ""),
            "startTime": r.get("startTime", ""),
            "endTime": r.get("endTime", ""),
            "space": r.get("space", ""),
            "expireTime": r.get("expireTime", ""),
        })
    return json.dumps(records, indent=2)


def meet_list_participant_sessions(conference_record_name: str, participant_name: str) -> str:
    """List sessions for a specific participant in a conference.

    Args:
        conference_record_name: The conference record resource name (e.g. 'conferenceRecords/abc').
        participant_name: The participant resource name (e.g. 'conferenceRecords/abc/participants/xyz').
    """
    svc = _meet()
    result = svc.conferenceRecords().participants().participantSessions().list(
        parent=participant_name
    ).execute()
    sessions = []
    for s in result.get("participantSessions", []):
        sessions.append({
            "name": s.get("name", ""),
            "startTime": s.get("startTime", ""),
            "endTime": s.get("endTime", ""),
        })
    return json.dumps(sessions, indent=2)
