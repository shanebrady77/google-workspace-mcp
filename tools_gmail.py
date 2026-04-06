"""Gmail tools — search, read, send, draft, labels, modify messages."""

import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from auth import get_service


def _gmail():
    return get_service("gmail", "v1")


def gmail_search(query: str = "", max_results: int = 20) -> str:
    """Search Gmail messages using Gmail query syntax.

    Args:
        query: Gmail search query (e.g. 'is:unread', 'from:boss@company.com', 'subject:meeting has:attachment').
               Empty string returns recent messages.
        max_results: Maximum number of messages to return (1-500).
    """
    svc = _gmail()
    results = svc.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = results.get("messages", [])
    if not messages:
        return "No messages found."

    output = []
    for msg_stub in messages:
        msg = svc.users().messages().get(userId="me", id=msg_stub["id"], format="metadata",
                                          metadataHeaders=["From", "To", "Subject", "Date"]).execute()
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        snippet = msg.get("snippet", "")
        output.append({
            "id": msg["id"],
            "threadId": msg["threadId"],
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "snippet": snippet,
            "labels": msg.get("labelIds", []),
        })
    return json.dumps(output, indent=2)


def gmail_read_message(message_id: str) -> str:
    """Read the full content of a specific Gmail message.

    Args:
        message_id: The message ID (from gmail_search results).
    """
    svc = _gmail()
    msg = svc.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

    # Extract body
    body = _extract_body(msg.get("payload", {}))

    return json.dumps({
        "id": msg["id"],
        "threadId": msg["threadId"],
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "cc": headers.get("Cc", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "body": body,
        "labels": msg.get("labelIds", []),
    }, indent=2)


def gmail_read_thread(thread_id: str) -> str:
    """Read all messages in a Gmail thread.

    Args:
        thread_id: The thread ID (from gmail_search results).
    """
    svc = _gmail()
    thread = svc.users().threads().get(userId="me", id=thread_id, format="full").execute()
    messages = []
    for msg in thread.get("messages", []):
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        body = _extract_body(msg.get("payload", {}))
        messages.append({
            "id": msg["id"],
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "date": headers.get("Date", ""),
            "subject": headers.get("Subject", ""),
            "body": body,
        })
    return json.dumps(messages, indent=2)


def gmail_send(to: str, subject: str, body: str, cc: str = "", bcc: str = "",
               html: bool = False, thread_id: str = "", in_reply_to: str = "") -> str:
    """Send an email via Gmail.

    Args:
        to: Recipient email address(es), comma-separated for multiple.
        subject: Email subject line.
        body: Email body content (plain text or HTML).
        cc: CC recipients, comma-separated.
        bcc: BCC recipients, comma-separated.
        html: If True, body is treated as HTML content.
        thread_id: Thread ID to reply to (for threading).
        in_reply_to: Message-ID header for threading.
    """
    svc = _gmail()

    if html:
        message = MIMEMultipart("alternative")
        message.attach(MIMEText(body, "html"))
    else:
        message = MIMEText(body)

    message["to"] = to
    message["subject"] = subject
    if cc:
        message["cc"] = cc
    if bcc:
        message["bcc"] = bcc
    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
        message["References"] = in_reply_to

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_body = {"raw": raw}
    if thread_id:
        send_body["threadId"] = thread_id

    result = svc.users().messages().send(userId="me", body=send_body).execute()
    return json.dumps({"status": "sent", "messageId": result["id"], "threadId": result.get("threadId", "")})


def gmail_draft(to: str = "", subject: str = "", body: str = "", cc: str = "",
                bcc: str = "", html: bool = False, thread_id: str = "") -> str:
    """Create a Gmail draft.

    Args:
        to: Recipient email address(es). Can be empty for drafts.
        subject: Email subject line.
        body: Email body content.
        cc: CC recipients.
        bcc: BCC recipients.
        html: If True, body is treated as HTML.
        thread_id: Thread ID for reply drafts.
    """
    svc = _gmail()

    if html:
        message = MIMEMultipart("alternative")
        message.attach(MIMEText(body, "html"))
    else:
        message = MIMEText(body)

    if to:
        message["to"] = to
    if subject:
        message["subject"] = subject
    if cc:
        message["cc"] = cc
    if bcc:
        message["bcc"] = bcc

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_body = {"message": {"raw": raw}}
    if thread_id:
        draft_body["message"]["threadId"] = thread_id

    result = svc.users().drafts().create(userId="me", body=draft_body).execute()
    return json.dumps({"status": "draft_created", "draftId": result["id"]})


def gmail_list_labels() -> str:
    """List all Gmail labels (system and user-created)."""
    svc = _gmail()
    results = svc.users().labels().list(userId="me").execute()
    labels = [{"id": l["id"], "name": l["name"], "type": l.get("type", "")}
              for l in results.get("labels", [])]
    return json.dumps(labels, indent=2)


def gmail_modify_labels(message_id: str, add_labels: list[str] = None,
                        remove_labels: list[str] = None) -> str:
    """Modify labels on a Gmail message (archive, mark read/unread, star, etc).

    Args:
        message_id: The message ID to modify.
        add_labels: List of label IDs to add (e.g. ['STARRED', 'IMPORTANT']).
        remove_labels: List of label IDs to remove (e.g. ['INBOX', 'UNREAD']).
    """
    svc = _gmail()
    body = {}
    if add_labels:
        body["addLabelIds"] = add_labels
    if remove_labels:
        body["removeLabelIds"] = remove_labels
    result = svc.users().messages().modify(userId="me", id=message_id, body=body).execute()
    return json.dumps({"status": "modified", "id": result["id"], "labels": result.get("labelIds", [])})


def gmail_send_draft(draft_id: str) -> str:
    """Send an existing Gmail draft.

    Args:
        draft_id: The draft ID (from gmail_draft results).
    """
    svc = _gmail()
    result = svc.users().drafts().send(userId="me", body={"id": draft_id}).execute()
    return json.dumps({"status": "sent", "messageId": result["id"], "threadId": result.get("threadId", "")})


def gmail_get_attachment(message_id: str, attachment_id: str) -> str:
    """Download a Gmail attachment and return its base64 data.

    Args:
        message_id: The message ID containing the attachment.
        attachment_id: The attachment ID (from gmail_read_message payload parts).
    """
    svc = _gmail()
    att = svc.users().messages().attachments().get(
        userId="me", messageId=message_id, id=attachment_id
    ).execute()
    return json.dumps({"size": att.get("size", 0), "data": att.get("data", "")})


def gmail_trash(message_id: str) -> str:
    """Move a Gmail message to the trash.

    Args:
        message_id: The message ID to trash.
    """
    svc = _gmail()
    svc.users().messages().trash(userId="me", id=message_id).execute()
    return json.dumps({"status": "trashed", "id": message_id})


def gmail_untrash(message_id: str) -> str:
    """Remove a Gmail message from the trash.

    Args:
        message_id: The message ID to untrash.
    """
    svc = _gmail()
    svc.users().messages().untrash(userId="me", id=message_id).execute()
    return json.dumps({"status": "untrashed", "id": message_id})


def gmail_create_label(name: str) -> str:
    """Create a new Gmail label.

    Args:
        name: Name for the new label.
    """
    svc = _gmail()
    result = svc.users().labels().create(userId="me", body={
        "name": name, "labelListVisibility": "labelShow",
        "messageListVisibility": "show"
    }).execute()
    return json.dumps({"status": "created", "id": result["id"], "name": result["name"]})


def gmail_delete_label(label_id: str) -> str:
    """Delete a Gmail label.

    Args:
        label_id: The label ID to delete (from gmail_list_labels).
    """
    svc = _gmail()
    svc.users().labels().delete(userId="me", id=label_id).execute()
    return json.dumps({"status": "deleted", "id": label_id})


def gmail_list_filters() -> str:
    """List all Gmail filters."""
    svc = _gmail()
    result = svc.users().settings().filters().list(userId="me").execute()
    filters = []
    for f in result.get("filter", []):
        filters.append({
            "id": f["id"],
            "criteria": f.get("criteria", {}),
            "action": f.get("action", {}),
        })
    return json.dumps(filters, indent=2) if filters else "No filters found."


def gmail_create_filter(criteria: dict, action: dict) -> str:
    """Create a Gmail filter.

    Args:
        criteria: Filter criteria dict. Keys: from, to, subject, query, negatedQuery, hasAttachment, excludeChats, size, sizeComparison.
        action: Filter action dict. Keys: addLabelIds, removeLabelIds, forward, archive (removeLabelIds=['INBOX']), markRead (removeLabelIds=['UNREAD']), star (addLabelIds=['STARRED']).
    """
    svc = _gmail()
    body = {"criteria": criteria, "action": action}
    result = svc.users().settings().filters().create(userId="me", body=body).execute()
    return json.dumps({"status": "created", "id": result["id"], "criteria": result.get("criteria", {}),
                       "action": result.get("action", {})})


def gmail_delete_filter(filter_id: str) -> str:
    """Delete a Gmail filter.

    Args:
        filter_id: The filter ID to delete.
    """
    svc = _gmail()
    svc.users().settings().filters().delete(userId="me", id=filter_id).execute()
    return json.dumps({"status": "deleted", "id": filter_id})


def gmail_get_vacation(account: str = "me") -> str:
    """Get the current Gmail vacation/auto-reply settings."""
    svc = _gmail()
    result = svc.users().settings().getVacation(userId=account).execute()
    return json.dumps(result, indent=2)


def gmail_set_vacation(enable: bool, subject: str = "", body: str = "",
                       html: bool = False, start_time: int = 0, end_time: int = 0,
                       contacts_only: bool = False, domain_only: bool = False) -> str:
    """Set Gmail vacation/auto-reply responder.

    Args:
        enable: True to enable, False to disable.
        subject: Auto-reply subject line.
        body: Auto-reply body text.
        html: If True, body is treated as HTML.
        start_time: Start time in milliseconds since epoch (0 = immediate).
        end_time: End time in milliseconds since epoch (0 = no end).
        contacts_only: Only auto-reply to contacts.
        domain_only: Only auto-reply to same domain.
    """
    svc = _gmail()
    settings = {"enableAutoReply": enable}
    if subject:
        settings["responseSubject"] = subject
    if body:
        if html:
            settings["responseBodyHtml"] = body
        else:
            settings["responseBodyPlainText"] = body
    if start_time:
        settings["startTime"] = start_time
    if end_time:
        settings["endTime"] = end_time
    settings["restrictToContacts"] = contacts_only
    settings["restrictToDomain"] = domain_only

    result = svc.users().settings().updateVacation(userId="me", body=settings).execute()
    return json.dumps({"status": "updated", "enableAutoReply": result.get("enableAutoReply", False)})


def _extract_body(payload: dict) -> str:
    """Recursively extract text body from a Gmail message payload."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    if payload.get("mimeType") == "text/html" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        result = _extract_body(part)
        if result:
            return result
    return ""
