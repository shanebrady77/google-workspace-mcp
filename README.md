# Google Workspace MCP Server

Your own MCP server for full Google Workspace access from Claude Desktop or Claude Code.

**Gmail (send + read) · Drive · Calendar · Docs · Sheets · Slides · Forms · Tasks · Contacts**

Built with FastMCP. Uses your own Google Cloud OAuth credentials. You own everything.

---

## Setup

### 1. Google Cloud Console (you do this in your browser)

1. Go to https://console.cloud.google.com → Create a new project
2. Enable these APIs (APIs & Services → Library):
   - Gmail, Calendar, Drive, Docs, Sheets, Slides, Forms, Tasks, People, Google Meet
3. Set up OAuth consent screen (APIs & Services → OAuth consent screen):
   - Choose External, add your email as test user
   - Add all workspace scopes
4. Create OAuth credentials (APIs & Services → Credentials → Create → OAuth Client ID → Desktop Application)
5. Copy the **Client ID** and **Client Secret**

### 2. Install & Run

```bash
# Set your credentials
export GOOGLE_OAUTH_CLIENT_ID="your-client-id-here"
export GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret-here"

# Run with uv (no install needed)
cd google-workspace-mcp
uv run server.py
```

### 3. Connect to Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google_workspace": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/google-workspace-mcp", "server.py"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "your-client-id",
        "GOOGLE_OAUTH_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### 4. Connect to Claude Code

```bash
claude mcp add google_workspace -- uv run --directory /path/to/google-workspace-mcp server.py
```

### 5. First authentication

First time you use any tool, a browser window opens for Google OAuth. Sign in, approve the permissions, done. Token is saved to `~/.gw-mcp/token.json` and auto-refreshes.

---

## Tools (108 total)

### Gmail (18)
- `gmail_search` — search with Gmail query syntax
- `gmail_read_message` — read full message content
- `gmail_read_thread` — read all messages in a thread
- `gmail_send` — **send emails** (plain text or HTML, CC/BCC, threading)
- `gmail_draft` — create drafts
- `gmail_send_draft` — send an existing draft
- `gmail_list_labels` — list all labels
- `gmail_create_label` — create new labels
- `gmail_delete_label` — delete labels
- `gmail_modify_labels` — archive, mark read/unread, star, etc
- `gmail_get_attachment` — download attachments
- `gmail_trash` — move to trash
- `gmail_untrash` — restore from trash
- `gmail_list_filters` — list email filters
- `gmail_create_filter` — create filter rules
- `gmail_delete_filter` — delete filters
- `gmail_get_vacation` — get vacation responder settings
- `gmail_set_vacation` — set vacation responder

### Calendar (8)
- `calendar_list_calendars` — list all calendars
- `calendar_get_events` — get events with time range and search
- `calendar_create_event` — create events with attendees + Google Meet links
- `calendar_update_event` — update existing events
- `calendar_delete_event` — delete events
- `calendar_freebusy` — query free/busy availability
- `calendar_list_recurring_instances` — list instances of recurring events
- `calendar_quick_add` — create event from text string

### Meet (7)
- `meet_create_space` — create a meeting space
- `meet_get_space` — get meeting space by name
- `meet_list_participants` — list participants
- `meet_get_artifacts` — get recordings, transcripts, and transcript entries
- `meet_end_conference` — end an active conference
- `meet_list_conference_records` — list past meetings
- `meet_list_participant_sessions` — list participant sessions

### Drive (15)
- `drive_search` — search files
- `drive_read_file` — read file content (Docs, Sheets, text files)
- `drive_create_file` — create files (plain text or Google Docs)
- `drive_list_folder` — list folder contents
- `drive_share_file` — share files with users
- `drive_create_folder` — create folders
- `drive_copy_file` — copy files
- `drive_export` — export to format (PDF, CSV, etc)
- `drive_add_comment` — add comments to files
- `drive_list_comments` — list file comments
- `drive_list_revisions` — list file version history
- `drive_list_permissions` — list file permissions
- `drive_delete_permission` — revoke file access
- `drive_trash` — move to trash
- `drive_untrash` — restore from trash

### Docs (9)
- `docs_create` — create new docs
- `docs_read` — read doc content
- `docs_insert_text` — insert text at position
- `docs_find_replace` — find and replace
- `docs_append_text` — append to end
- `docs_insert_table` — insert tables
- `docs_insert_image` — insert images
- `docs_format_text` — format text (bold, italic, color, font)
- `docs_insert_bullets` — insert bullet lists
- `docs_insert_page_break` — insert page breaks

### Sheets (12)
- `sheets_read` — read cell ranges
- `sheets_write` — write values
- `sheets_append` — append rows
- `sheets_create` — create spreadsheets
- `sheets_clear` — clear ranges
- `sheets_get_info` — get spreadsheet metadata
- `sheets_batch_update` — batch update cells
- `sheets_add_sheet` — add new sheet/tab
- `sheets_delete_sheet` — delete sheet/tab
- `sheets_merge_cells` — merge cells
- `sheets_add_chart` — add charts
- `sheets_add_conditional_format` — add conditional formatting
- `sheets_add_named_range` — add named ranges

### Tasks (8)
- `tasks_list_tasklists` — list task lists
- `tasks_list` — list tasks
- `tasks_create` — create tasks (with subtask support)
- `tasks_update` — update tasks
- `tasks_delete` — delete tasks
- `tasks_create_tasklist` — create task lists
- `tasks_move` — move/reorder tasks
- `tasks_clear_completed` — clear completed tasks

### Contacts (11)
- `contacts_search` — search by name/email/phone
- `contacts_list` — list all contacts
- `contacts_create` — create contacts
- `contacts_update` — update contacts
- `contacts_delete` — delete contacts
- `contacts_list_groups` — list contact groups
- `contacts_create_group` — create contact group
- `contacts_modify_group_members` — add/remove group members
- `contacts_batch_create` — batch create contacts
- `contacts_batch_delete` — batch delete contacts
- `contacts_get_photo` — get contact photo

### Slides (10)
- `slides_create` — create presentations
- `slides_read` — read slide content
- `slides_add_slide` — add slides with layouts
- `slides_add_text` — add text to slides
- `slides_insert_shape` — insert shapes
- `slides_insert_image` — insert images
- `slides_insert_table` — insert tables
- `slides_insert_video` — insert videos
- `slides_format_text` — format text
- `slides_get_thumbnail` — get slide thumbnail

### Forms (8)
- `forms_create` — create forms
- `forms_read` — read form structure
- `forms_list_responses` — list form responses
- `forms_add_question` — add questions
- `forms_update_question` — update questions
- `forms_delete_question` — delete questions
- `forms_move_question` — reorder questions
- `forms_update_settings` — update form settings

---

## Build It Yourself Prompt

Want to rebuild this from scratch using Claude? Paste this into Claude Code Desktop:

> Build me a Python MCP server using FastMCP at ~/Desktop/google-workspace-mcp/. It should give me full access to Google Workspace with these tools:
>
> Gmail (18): search, read message, read thread, send (with CC/BCC, HTML, threading for replies), create draft, send draft, list labels, create label, delete label, modify labels (archive, star, mark read/unread), get attachment, trash, untrash, list filters, create filter, delete filter, get vacation responder, set vacation responder
>
> Calendar (8): list calendars, get events (with time range + search), create event (with attendees, timezone, Google Meet link generation), update event, delete event, query free/busy, list recurring event instances, quick add from text string
>
> Meet (7): create meeting space, get meeting space, list participants, get artifacts (recordings + transcripts), end active conference, list conference records, list participant sessions
>
> Drive (15): search files, read file content (export Google Docs/Sheets/Slides to text), create file (plain text or Google Doc), list folder, share file, create folder, copy file, export to format, add comment, list comments, list revisions, list permissions, delete permission, trash, untrash
>
> Docs (9): create, read, insert text at position, find and replace, append text, insert table, insert image, format text (bold/italic/color/font), insert bullet list, insert page break
>
> Sheets (12): read ranges, write values, append rows, create spreadsheet, clear ranges, get spreadsheet metadata, batch update cells, add sheet/tab, delete sheet/tab, merge cells, add chart, add conditional formatting, add named range
>
> Tasks (8): list task lists, list tasks, create task (with subtask support), update task, delete task, create task list, move/reorder task, clear completed tasks
>
> Contacts (11): search by name/email/phone, list all, create, update, delete, list contact groups, create group, modify group members, batch create, batch delete, get contact photo
>
> Slides (10): create presentation, read slide content, add slide with layout, add text to slide, insert shape, insert image, insert table, insert video, format text, get slide thumbnail
>
> Forms (8): create form, read form structure, list responses, add question, update question, delete question, move/reorder question, update form settings
>
> Requirements:
> - Separate file per service (tools_gmail.py, tools_calendar.py, tools_meet.py, tools_drive.py, tools_docs.py, tools_sheets.py, tools_tasks.py, tools_contacts.py, tools_slides.py, tools_forms.py) plus auth.py and server.py
> - auth.py handles Google OAuth2: reads GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET from env vars, opens browser on first use, saves token to ~/.gw-mcp/token.json, auto-refreshes
> - Use google-api-python-client and google-auth-oauthlib
> - pyproject.toml with uv, entry point gw-mcp = "server:main"
> - .gitignore for .venv, __pycache__, .env, token.json, credentials.json
> - README with setup instructions for Google Cloud Console, running with uv, and adding to Claude Desktop + Claude Code configs
