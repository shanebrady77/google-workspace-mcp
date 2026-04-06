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
import tools_meet

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

@mcp.tool()
def gmail_send_draft(draft_id: str) -> str:
    """Send an existing Gmail draft."""
    return tools_gmail.gmail_send_draft(draft_id)

@mcp.tool()
def gmail_get_attachment(message_id: str, attachment_id: str) -> str:
    """Download a Gmail attachment and return its base64 data."""
    return tools_gmail.gmail_get_attachment(message_id, attachment_id)

@mcp.tool()
def gmail_trash(message_id: str) -> str:
    """Move a Gmail message to the trash."""
    return tools_gmail.gmail_trash(message_id)

@mcp.tool()
def gmail_untrash(message_id: str) -> str:
    """Remove a Gmail message from the trash."""
    return tools_gmail.gmail_untrash(message_id)

@mcp.tool()
def gmail_create_label(name: str) -> str:
    """Create a new Gmail label."""
    return tools_gmail.gmail_create_label(name)

@mcp.tool()
def gmail_delete_label(label_id: str) -> str:
    """Delete a Gmail label."""
    return tools_gmail.gmail_delete_label(label_id)

@mcp.tool()
def gmail_list_filters() -> str:
    """List all Gmail filters."""
    return tools_gmail.gmail_list_filters()

@mcp.tool()
def gmail_create_filter(criteria: dict, action: dict) -> str:
    """Create a Gmail filter. criteria: {from, to, subject, query, hasAttachment}. action: {addLabelIds, removeLabelIds, forward}."""
    return tools_gmail.gmail_create_filter(criteria, action)

@mcp.tool()
def gmail_delete_filter(filter_id: str) -> str:
    """Delete a Gmail filter."""
    return tools_gmail.gmail_delete_filter(filter_id)

@mcp.tool()
def gmail_get_vacation() -> str:
    """Get current Gmail vacation/auto-reply settings."""
    return tools_gmail.gmail_get_vacation()

@mcp.tool()
def gmail_set_vacation(enable: bool, subject: str = "", body: str = "",
                       html: bool = False, start_time: int = 0, end_time: int = 0,
                       contacts_only: bool = False, domain_only: bool = False) -> str:
    """Set Gmail vacation/auto-reply responder."""
    return tools_gmail.gmail_set_vacation(enable, subject, body, html, start_time, end_time,
                                          contacts_only, domain_only)

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
                          timezone: str = "America/Toronto", add_google_meet: bool = False) -> str:
    """Create a calendar event. Use RFC3339 datetimes for timed events or YYYY-MM-DD for all-day. Set add_google_meet=True to auto-generate a Google Meet link."""
    return tools_calendar.calendar_create_event(summary, start, end, calendar_id, description,
                                                 location, attendees, timezone, add_google_meet)

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

@mcp.tool()
def calendar_freebusy(time_min: str, time_max: str, calendars: list[str] = None,
                      timezone: str = "America/Toronto") -> str:
    """Query free/busy info for calendars. Returns busy time blocks."""
    return tools_calendar.calendar_freebusy(time_min, time_max, calendars, timezone)

@mcp.tool()
def calendar_list_recurring_instances(event_id: str, calendar_id: str = "primary",
                                      time_min: str = "", time_max: str = "",
                                      max_results: int = 25) -> str:
    """List instances of a recurring event."""
    return tools_calendar.calendar_list_recurring_instances(event_id, calendar_id, time_min, time_max, max_results)

@mcp.tool()
def calendar_quick_add(text: str, calendar_id: str = "primary") -> str:
    """Create an event from natural language (e.g. 'Lunch with John tomorrow at noon')."""
    return tools_calendar.calendar_quick_add(text, calendar_id)

# ── Meet ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def meet_create_space() -> str:
    """Create a new Google Meet meeting space. Returns meeting URI and code."""
    return tools_meet.meet_create_space()

@mcp.tool()
def meet_get_space(space_name: str) -> str:
    """Get details about a Google Meet meeting space by its resource name (e.g. 'spaces/abc-defg-hij')."""
    return tools_meet.meet_get_space(space_name)

@mcp.tool()
def meet_list_participants(conference_record_name: str) -> str:
    """List participants and their sessions for a conference record (e.g. 'conferenceRecords/abc-defg-hij')."""
    return tools_meet.meet_list_participants(conference_record_name)

@mcp.tool()
def meet_get_artifacts(conference_record_name: str) -> str:
    """Get recordings, transcripts, and transcript entries for a conference record."""
    return tools_meet.meet_get_artifacts(conference_record_name)

@mcp.tool()
def meet_end_conference(space_name: str) -> str:
    """End an active conference in a meeting space."""
    return tools_meet.meet_end_conference(space_name)

@mcp.tool()
def meet_list_conference_records(max_results: int = 25) -> str:
    """List past conference records (meeting history)."""
    return tools_meet.meet_list_conference_records(max_results)

@mcp.tool()
def meet_list_participant_sessions(conference_record_name: str, participant_name: str) -> str:
    """List sessions for a specific participant in a conference."""
    return tools_meet.meet_list_participant_sessions(conference_record_name, participant_name)

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

@mcp.tool()
def drive_copy_file(file_id: str, name: str = "", folder_id: str = "") -> str:
    """Copy a file in Google Drive."""
    return tools_drive.drive_copy_file(file_id, name, folder_id)

@mcp.tool()
def drive_export(file_id: str, mime_type: str) -> str:
    """Export a Google Workspace file to a format (PDF, DOCX, CSV, XLSX, PPTX, PNG, etc)."""
    return tools_drive.drive_export(file_id, mime_type)

@mcp.tool()
def drive_add_comment(file_id: str, content: str) -> str:
    """Add a comment to a Drive file."""
    return tools_drive.drive_add_comment(file_id, content)

@mcp.tool()
def drive_list_comments(file_id: str, max_results: int = 20) -> str:
    """List comments on a Drive file."""
    return tools_drive.drive_list_comments(file_id, max_results)

@mcp.tool()
def drive_list_revisions(file_id: str) -> str:
    """List file revisions (version history)."""
    return tools_drive.drive_list_revisions(file_id)

@mcp.tool()
def drive_list_permissions(file_id: str) -> str:
    """List sharing permissions on a file."""
    return tools_drive.drive_list_permissions(file_id)

@mcp.tool()
def drive_delete_permission(file_id: str, permission_id: str) -> str:
    """Remove a sharing permission from a file."""
    return tools_drive.drive_delete_permission(file_id, permission_id)

@mcp.tool()
def drive_trash(file_id: str) -> str:
    """Move a file to the trash."""
    return tools_drive.drive_trash(file_id)

@mcp.tool()
def drive_untrash(file_id: str) -> str:
    """Restore a file from the trash."""
    return tools_drive.drive_untrash(file_id)

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

@mcp.tool()
def docs_insert_table(document_id: str, rows: int, columns: int, index: int = 1) -> str:
    """Insert a table into a Google Doc."""
    return tools_docs.docs_insert_table(document_id, rows, columns, index)

@mcp.tool()
def docs_insert_image(document_id: str, image_uri: str, index: int = 1,
                      width_pt: float = 300, height_pt: float = 200) -> str:
    """Insert an image into a Google Doc from a URL."""
    return tools_docs.docs_insert_image(document_id, image_uri, index, width_pt, height_pt)

@mcp.tool()
def docs_format_text(document_id: str, start_index: int, end_index: int,
                     bold: bool = None, italic: bool = None, underline: bool = None,
                     strikethrough: bool = None, font_size: float = None,
                     foreground_color: str = "") -> str:
    """Apply formatting (bold, italic, underline, font size, color) to a text range in a Google Doc."""
    return tools_docs.docs_format_text(document_id, start_index, end_index, bold, italic,
                                        underline, strikethrough, font_size, foreground_color)

@mcp.tool()
def docs_insert_bullets(document_id: str, start_index: int, end_index: int,
                        bullet_type: str = "BULLET_DISC_CIRCLE_SQUARE") -> str:
    """Apply bullet or numbered list formatting to paragraphs in a Google Doc."""
    return tools_docs.docs_insert_bullets(document_id, start_index, end_index, bullet_type)

@mcp.tool()
def docs_insert_page_break(document_id: str, index: int) -> str:
    """Insert a page break in a Google Doc."""
    return tools_docs.docs_insert_page_break(document_id, index)

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

@mcp.tool()
def sheets_batch_update(spreadsheet_id: str, data: list[dict]) -> str:
    """Write to multiple ranges in one request. data: [{"range": "A1", "values": [[...]]}]."""
    return tools_sheets.sheets_batch_update(spreadsheet_id, data)

@mcp.tool()
def sheets_add_sheet(spreadsheet_id: str, title: str) -> str:
    """Add a new sheet/tab to a spreadsheet."""
    return tools_sheets.sheets_add_sheet(spreadsheet_id, title)

@mcp.tool()
def sheets_delete_sheet(spreadsheet_id: str, sheet_id: int) -> str:
    """Delete a sheet/tab (by numeric sheet ID, not name)."""
    return tools_sheets.sheets_delete_sheet(spreadsheet_id, sheet_id)

@mcp.tool()
def sheets_merge_cells(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                       start_col: int, end_col: int, merge_type: str = "MERGE_ALL") -> str:
    """Merge cells in a sheet. Indices are 0-based, end is exclusive."""
    return tools_sheets.sheets_merge_cells(spreadsheet_id, sheet_id, start_row, end_row,
                                            start_col, end_col, merge_type)

@mcp.tool()
def sheets_add_chart(spreadsheet_id: str, sheet_id: int, chart_type: str,
                     data_range: str, title: str = "") -> str:
    """Add a chart. Types: BAR, LINE, AREA, COLUMN, SCATTER, COMBO, STEPPED_AREA."""
    return tools_sheets.sheets_add_chart(spreadsheet_id, sheet_id, chart_type, data_range, title)

@mcp.tool()
def sheets_add_conditional_format(spreadsheet_id: str, sheet_id: int,
                                  start_row: int, end_row: int,
                                  start_col: int, end_col: int,
                                  rule_type: str, values: list[str],
                                  bg_color: str = "#FF0000") -> str:
    """Add conditional formatting. rule_type: NUMBER_GREATER, TEXT_CONTAINS, CUSTOM_FORMULA, BLANK, etc."""
    return tools_sheets.sheets_add_conditional_format(spreadsheet_id, sheet_id, start_row, end_row,
                                                      start_col, end_col, rule_type, values, bg_color)

@mcp.tool()
def sheets_add_named_range(spreadsheet_id: str, name: str, sheet_id: int,
                           start_row: int, end_row: int,
                           start_col: int, end_col: int) -> str:
    """Create a named range in a spreadsheet."""
    return tools_sheets.sheets_add_named_range(spreadsheet_id, name, sheet_id, start_row, end_row,
                                                start_col, end_col)

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

@mcp.tool()
def tasks_move(task_id: str, tasklist_id: str = "@default",
               parent: str = "", previous: str = "") -> str:
    """Move/reorder a task. Set parent to make it a subtask, previous to position after another task."""
    return tools_tasks.tasks_move(task_id, tasklist_id, parent, previous)

@mcp.tool()
def tasks_clear_completed(tasklist_id: str = "@default") -> str:
    """Clear all completed tasks from a task list."""
    return tools_tasks.tasks_clear_completed(tasklist_id)

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

@mcp.tool()
def contacts_list_groups(max_results: int = 50) -> str:
    """List all contact groups (labels)."""
    return tools_contacts.contacts_list_groups(max_results)

@mcp.tool()
def contacts_create_group(name: str) -> str:
    """Create a new contact group."""
    return tools_contacts.contacts_create_group(name)

@mcp.tool()
def contacts_modify_group_members(group_resource_name: str,
                                  add_contacts: list[str] = None,
                                  remove_contacts: list[str] = None) -> str:
    """Add or remove contacts from a contact group."""
    return tools_contacts.contacts_modify_group_members(group_resource_name, add_contacts, remove_contacts)

@mcp.tool()
def contacts_batch_create(contacts: list[dict]) -> str:
    """Create multiple contacts at once. Each dict: {givenName, familyName, email, phone, organization, title}."""
    return tools_contacts.contacts_batch_create(contacts)

@mcp.tool()
def contacts_batch_delete(resource_names: list[str]) -> str:
    """Delete multiple contacts at once."""
    return tools_contacts.contacts_batch_delete(resource_names)

@mcp.tool()
def contacts_get_photo(resource_name: str) -> str:
    """Get the photo URL for a contact."""
    return tools_contacts.contacts_get_photo(resource_name)

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

@mcp.tool()
def slides_insert_shape(presentation_id: str, slide_id: str, shape_type: str = "RECTANGLE",
                        x_pt: float = 100, y_pt: float = 100,
                        width_pt: float = 200, height_pt: float = 100) -> str:
    """Insert a shape (RECTANGLE, ELLIPSE, TRIANGLE, STAR, ARROW_EAST, etc) onto a slide."""
    return tools_slides.slides_insert_shape(presentation_id, slide_id, shape_type, x_pt, y_pt, width_pt, height_pt)

@mcp.tool()
def slides_insert_image(presentation_id: str, slide_id: str, image_url: str,
                        x_pt: float = 100, y_pt: float = 100,
                        width_pt: float = 300, height_pt: float = 200) -> str:
    """Insert an image onto a slide from a URL."""
    return tools_slides.slides_insert_image(presentation_id, slide_id, image_url, x_pt, y_pt, width_pt, height_pt)

@mcp.tool()
def slides_insert_table(presentation_id: str, slide_id: str, rows: int, columns: int,
                        x_pt: float = 50, y_pt: float = 100,
                        width_pt: float = 600, height_pt: float = 300) -> str:
    """Insert a table onto a slide."""
    return tools_slides.slides_insert_table(presentation_id, slide_id, rows, columns, x_pt, y_pt, width_pt, height_pt)

@mcp.tool()
def slides_insert_video(presentation_id: str, slide_id: str, video_id: str,
                        x_pt: float = 100, y_pt: float = 100,
                        width_pt: float = 400, height_pt: float = 225) -> str:
    """Insert a YouTube video onto a slide. video_id is the YouTube video ID."""
    return tools_slides.slides_insert_video(presentation_id, slide_id, video_id, x_pt, y_pt, width_pt, height_pt)

@mcp.tool()
def slides_format_text(presentation_id: str, shape_id: str, start_index: int, end_index: int,
                       bold: bool = None, italic: bool = None, underline: bool = None,
                       font_size: float = None, foreground_color: str = "") -> str:
    """Format text within a shape on a slide (bold, italic, size, color)."""
    return tools_slides.slides_format_text(presentation_id, shape_id, start_index, end_index,
                                            bold, italic, underline, font_size, foreground_color)

@mcp.tool()
def slides_get_thumbnail(presentation_id: str, slide_id: str) -> str:
    """Get a thumbnail image URL for a slide."""
    return tools_slides.slides_get_thumbnail(presentation_id, slide_id)

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

@mcp.tool()
def forms_add_question(form_id: str, title: str, question_type: str = "TEXT",
                       required: bool = False, options: list[str] = None,
                       paragraph: bool = False, index: int = -1) -> str:
    """Add a question to a form. Types: TEXT, PARAGRAPH, RADIO, CHECKBOX, DROP_DOWN, SCALE."""
    return tools_forms.forms_add_question(form_id, title, question_type, required, options, paragraph, index)

@mcp.tool()
def forms_update_question(form_id: str, item_index: int, title: str = "",
                          required: bool = None) -> str:
    """Update an existing question in a form."""
    return tools_forms.forms_update_question(form_id, item_index, title, required)

@mcp.tool()
def forms_delete_question(form_id: str, item_index: int) -> str:
    """Delete a question from a form by its 0-based index."""
    return tools_forms.forms_delete_question(form_id, item_index)

@mcp.tool()
def forms_move_question(form_id: str, from_index: int, to_index: int) -> str:
    """Move/reorder a question in a form."""
    return tools_forms.forms_move_question(form_id, from_index, to_index)

@mcp.tool()
def forms_update_settings(form_id: str, is_quiz: bool = None, description: str = "") -> str:
    """Update form settings (make it a quiz, change description)."""
    return tools_forms.forms_update_settings(form_id, is_quiz, description)


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    mcp.run()

if __name__ == "__main__":
    main()
