"""
Google Workspace MCP Server
Full access to Gmail, Drive, Calendar, Docs, Sheets, Slides, Forms, Tasks, Contacts.
Built with FastMCP. Uses your own Google Cloud OAuth credentials.
"""

from mcp.server.fastmcp import FastMCP

# Import all tool modules
import tools_gmail
import tools_calendar
import tools_drive
import tools_docs
import tools_sheets
import tools_tasks
import tools_contacts
import tools_slides
import tools_forms

mcp = FastMCP("google_workspace_mcp")

# ── Gmail ────────────────────────────────────────────────────────────────────

@mcp.tool()
def gmail_search(query: str = "", max_results: int = 20) -> str:
    """Search Gmail messages. Uses Gmail query syntax: 'is:unread', 'from:user@example.com', 'subject:meeting has:attachment', 'after:2026/01/01', etc. Empty query returns recent messages."""
    return tools_gmail.gmail_search(query, max_results)

@mcp.tool()
def gmail_read_message(message_id: str) -> str:
    """Read the full content of a Gmail message by its ID."""
    return tools_gmail.gmail_read_message(message_id)

@mcp.tool()
def gmail_read_thread(thread_id: str) -> str:
    """Read all messages in a Gmail thread by its thread ID."""
    return tools_gmail.gmail_read_thread(thread_id)

@mcp.tool()
def gmail_send(to: str, subject: str, body: str, cc: str = "", bcc: str = "",
               html: bool = False, thread_id: str = "", in_reply_to: str = "") -> str:
    """Send an email. Supports plain text and HTML, CC/BCC, and threading for replies."""
    return tools_gmail.gmail_send(to, subject, body, cc, bcc, html, thread_id, in_reply_to)

@mcp.tool()
def gmail_draft(to: str = "", subject: str = "", body: str = "", cc: str = "",
                bcc: str = "", html: bool = False, thread_id: str = "") -> str:
    """Create a Gmail draft. All fields are optional for work-in-progress drafts."""
    return tools_gmail.gmail_draft(to, subject, body, cc, bcc, html, thread_id)

@mcp.tool()
def gmail_list_labels() -> str:
    """List all Gmail labels (system and user-created)."""
    return tools_gmail.gmail_list_labels()

@mcp.tool()
def gmail_modify_labels(message_id: str, add_labels: list[str] = None,
                        remove_labels: list[str] = None) -> str:
    """Modify labels on a message. Use to archive (remove INBOX), mark read (remove UNREAD), star (add STARRED), etc."""
    return tools_gmail.gmail_modify_labels(message_id, add_labels, remove_labels)

# ── Calendar ─────────────────────────────────────────────────────────────────

@mcp.tool()
def calendar_list_calendars() -> str:
    """List all calendars the user has access to."""
    return tools_calendar.calendar_list_calendars()

@mcp.tool()
def calendar_get_events(calendar_id: str = "primary", time_min: str = "",
                        time_max: str = "", max_results: int = 25, query: str = "") -> str:
    """Get calendar events. Filter by time range (RFC3339 format) and/or text search."""
    return tools_calendar.calendar_get_events(calendar_id, time_min, time_max, max_results, query)

@mcp.tool()
def calendar_create_event(summary: str, start: str, end: str, calendar_id: str = "primary",
                          description: str = "", location: str = "", attendees: list[str] = None,
                          timezone: str = "America/Toronto") -> str:
    """Create a calendar event. Use RFC3339 datetimes for timed events or YYYY-MM-DD for all-day."""
    return tools_calendar.calendar_create_event(summary, start, end, calendar_id, description,
                                                 location, attendees, timezone)

@mcp.tool()
def calendar_update_event(event_id: str, calendar_id: str = "primary", summary: str = "",
                          start: str = "", end: str = "", description: str = "",
                          location: str = "", timezone: str = "America/Toronto") -> str:
    """Update an existing calendar event. Only provided fields are changed."""
    return tools_calendar.calendar_update_event(event_id, calendar_id, summary, start, end,
                                                 description, location, timezone)

@mcp.tool()
def calendar_delete_event(event_id: str, calendar_id: str = "primary") -> str:
    """Delete a calendar event."""
    return tools_calendar.calendar_delete_event(event_id, calendar_id)

# ── Drive ────────────────────────────────────────────────────────────────────

@mcp.tool()
def drive_search(query: str = "", max_results: int = 20) -> str:
    """Search Google Drive files. Uses Drive query syntax: 'name contains \"report\"', 'mimeType=\"application/pdf\"', etc."""
    return tools_drive.drive_search(query, max_results)

@mcp.tool()
def drive_read_file(file_id: str) -> str:
    """Read the text content of a Drive file (Google Docs/Sheets/Slides exported, or raw text files)."""
    return tools_drive.drive_read_file(file_id)

@mcp.tool()
def drive_create_file(name: str, content: str = "", mime_type: str = "text/plain",
                      folder_id: str = "", as_google_doc: bool = False) -> str:
    """Create a new file in Drive. Set as_google_doc=True to create a Google Doc."""
    return tools_drive.drive_create_file(name, content, mime_type, folder_id, as_google_doc)

@mcp.tool()
def drive_list_folder(folder_id: str = "root", max_results: int = 50) -> str:
    """List contents of a Drive folder."""
    return tools_drive.drive_list_folder(folder_id, max_results)

@mcp.tool()
def drive_share_file(file_id: str, email: str, role: str = "reader",
                     send_notification: bool = True) -> str:
    """Share a Drive file. Roles: 'reader', 'writer', 'commenter'."""
    return tools_drive.drive_share_file(file_id, email, role, send_notification)

@mcp.tool()
def drive_create_folder(name: str, parent_id: str = "") -> str:
    """Create a folder in Google Drive."""
    return tools_drive.drive_create_folder(name, parent_id)

# ── Docs ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def docs_create(title: str, body_text: str = "") -> str:
    """Create a new Google Doc with optional initial text content."""
    return tools_docs.docs_create(title, body_text)

@mcp.tool()
def docs_read(document_id: str) -> str:
    """Read the full text content of a Google Doc."""
    return tools_docs.docs_read(document_id)

@mcp.tool()
def docs_insert_text(document_id: str, text: str, index: int = 1) -> str:
    """Insert text at a specific position in a Google Doc. Index 1 = beginning."""
    return tools_docs.docs_insert_text(document_id, text, index)

@mcp.tool()
def docs_find_replace(document_id: str, find_text: str, replace_text: str,
                      match_case: bool = False) -> str:
    """Find and replace text in a Google Doc."""
    return tools_docs.docs_find_replace(document_id, find_text, replace_text, match_case)

@mcp.tool()
def docs_append_text(document_id: str, text: str) -> str:
    """Append text to the end of a Google Doc."""
    return tools_docs.docs_append_text(document_id, text)

# ── Sheets ───────────────────────────────────────────────────────────────────

@mcp.tool()
def sheets_read(spreadsheet_id: str, range: str = "Sheet1") -> str:
    """Read values from a Google Sheet. Use A1 notation for ranges (e.g. 'Sheet1!A1:D10')."""
    return tools_sheets.sheets_read(spreadsheet_id, range)

@mcp.tool()
def sheets_write(spreadsheet_id: str, range: str, values: list[list]) -> str:
    """Write values to a Google Sheet. Values is a 2D array like [['Name','Age'],['Alice',30]]."""
    return tools_sheets.sheets_write(spreadsheet_id, range, values)

@mcp.tool()
def sheets_append(spreadsheet_id: str, range: str, values: list[list]) -> str:
    """Append rows to a Google Sheet after existing data."""
    return tools_sheets.sheets_append(spreadsheet_id, range, values)

@mcp.tool()
def sheets_create(title: str, sheet_names: list[str] = None) -> str:
    """Create a new Google Spreadsheet with optional custom sheet/tab names."""
    return tools_sheets.sheets_create(title, sheet_names)

@mcp.tool()
def sheets_clear(spreadsheet_id: str, range: str) -> str:
    """Clear values from a range in a Google Sheet."""
    return tools_sheets.sheets_clear(spreadsheet_id, range)

@mcp.tool()
def sheets_get_info(spreadsheet_id: str) -> str:
    """Get spreadsheet metadata — title, sheets/tabs, row and column counts."""
    return tools_sheets.sheets_get_info(spreadsheet_id)

# ── Tasks ────────────────────────────────────────────────────────────────────

@mcp.tool()
def tasks_list_tasklists() -> str:
    """List all Google Tasks task lists."""
    return tools_tasks.tasks_list_tasklists()

@mcp.tool()
def tasks_list(tasklist_id: str = "@default", show_completed: bool = False,
               max_results: int = 50) -> str:
    """List tasks in a task list. Use '@default' for the primary list."""
    return tools_tasks.tasks_list(tasklist_id, show_completed, max_results)

@mcp.tool()
def tasks_create(title: str, tasklist_id: str = "@default", notes: str = "",
                 due: str = "", parent: str = "") -> str:
    """Create a new task. Set parent for subtasks. Due date in RFC3339 format."""
    return tools_tasks.tasks_create(title, tasklist_id, notes, due, parent)

@mcp.tool()
def tasks_update(task_id: str, tasklist_id: str = "@default", title: str = "",
                 notes: str = "", status: str = "", due: str = "") -> str:
    """Update a task. Status can be 'needsAction' or 'completed'."""
    return tools_tasks.tasks_update(task_id, tasklist_id, title, notes, status, due)

@mcp.tool()
def tasks_delete(task_id: str, tasklist_id: str = "@default") -> str:
    """Delete a task."""
    return tools_tasks.tasks_delete(task_id, tasklist_id)

@mcp.tool()
def tasks_create_tasklist(title: str) -> str:
    """Create a new task list."""
    return tools_tasks.tasks_create_tasklist(title)

# ── Contacts ─────────────────────────────────────────────────────────────────

@mcp.tool()
def contacts_search(query: str, max_results: int = 20) -> str:
    """Search contacts by name, email, or phone number."""
    return tools_contacts.contacts_search(query, max_results)

@mcp.tool()
def contacts_list(max_results: int = 50) -> str:
    """List all contacts sorted by last name."""
    return tools_contacts.contacts_list(max_results)

@mcp.tool()
def contacts_create(given_name: str, family_name: str = "", email: str = "",
                    phone: str = "", organization: str = "", title: str = "") -> str:
    """Create a new contact with name, email, phone, organization, and title."""
    return tools_contacts.contacts_create(given_name, family_name, email, phone, organization, title)

@mcp.tool()
def contacts_update(resource_name: str, given_name: str = "", family_name: str = "",
                    email: str = "", phone: str = "", organization: str = "",
                    title: str = "") -> str:
    """Update a contact. Resource name from contacts_search/contacts_list (e.g. 'people/c123')."""
    return tools_contacts.contacts_update(resource_name, given_name, family_name, email, phone,
                                           organization, title)

@mcp.tool()
def contacts_delete(resource_name: str) -> str:
    """Delete a contact by resource name."""
    return tools_contacts.contacts_delete(resource_name)

# ── Slides ───────────────────────────────────────────────────────────────────

@mcp.tool()
def slides_create(title: str) -> str:
    """Create a new Google Slides presentation."""
    return tools_slides.slides_create(title)

@mcp.tool()
def slides_read(presentation_id: str) -> str:
    """Read a presentation's metadata and text content from all slides."""
    return tools_slides.slides_read(presentation_id)

@mcp.tool()
def slides_add_slide(presentation_id: str, layout: str = "BLANK",
                     insertion_index: int = -1) -> str:
    """Add a slide. Layouts: BLANK, CAPTION_ONLY, TITLE, TITLE_AND_BODY, TITLE_AND_TWO_COLUMNS."""
    return tools_slides.slides_add_slide(presentation_id, layout, insertion_index)

@mcp.tool()
def slides_add_text(presentation_id: str, slide_id: str, text: str,
                    shape_id: str = "") -> str:
    """Add text to a slide. Creates a new text box if shape_id is empty."""
    return tools_slides.slides_add_text_to_slide(presentation_id, slide_id, text, shape_id)

# ── Forms ────────────────────────────────────────────────────────────────────

@mcp.tool()
def forms_create(title: str, description: str = "") -> str:
    """Create a new Google Form."""
    return tools_forms.forms_create(title, description)

@mcp.tool()
def forms_read(form_id: str) -> str:
    """Read a form's structure, questions, and settings."""
    return tools_forms.forms_read(form_id)

@mcp.tool()
def forms_list_responses(form_id: str, max_results: int = 50) -> str:
    """List all responses submitted to a Google Form."""
    return tools_forms.forms_list_responses(form_id, max_results)


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    mcp.run()

if __name__ == "__main__":
    main()
