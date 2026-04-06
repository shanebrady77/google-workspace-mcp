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

## Tools (51 total)

### Gmail (7)
- `gmail_search` — search with Gmail query syntax
- `gmail_read_message` — read full message content
- `gmail_read_thread` — read all messages in a thread
- `gmail_send` — **send emails** (plain text or HTML, CC/BCC, threading)
- `gmail_draft` — create drafts
- `gmail_list_labels` — list all labels
- `gmail_modify_labels` — archive, mark read/unread, star, etc

### Calendar (5)
- `calendar_list_calendars` — list all calendars
- `calendar_get_events` — get events with time range and search
- `calendar_create_event` — create events with attendees + Google Meet links
- `calendar_update_event` — update existing events
- `calendar_delete_event` — delete events

### Meet (4)
- `meet_create_space` — create a meeting space
- `meet_get_space` — get meeting space by name
- `meet_list_participants` — list participants and sessions
- `meet_get_artifacts` — get recordings, transcripts, and transcript entries

### Drive (6)
- `drive_search` — search files
- `drive_read_file` — read file content (Docs, Sheets, text files)
- `drive_create_file` — create files (plain text or Google Docs)
- `drive_list_folder` — list folder contents
- `drive_share_file` — share files with users
- `drive_create_folder` — create folders

### Docs (5)
- `docs_create` — create new docs
- `docs_read` — read doc content
- `docs_insert_text` — insert text at position
- `docs_find_replace` — find and replace
- `docs_append_text` — append to end

### Sheets (6)
- `sheets_read` — read cell ranges
- `sheets_write` — write values
- `sheets_append` — append rows
- `sheets_create` — create spreadsheets
- `sheets_clear` — clear ranges
- `sheets_get_info` — get spreadsheet metadata

### Tasks (6)
- `tasks_list_tasklists` — list task lists
- `tasks_list` — list tasks
- `tasks_create` — create tasks (with subtask support)
- `tasks_update` — update tasks
- `tasks_delete` — delete tasks
- `tasks_create_tasklist` — create task lists

### Contacts (5)
- `contacts_search` — search by name/email/phone
- `contacts_list` — list all contacts
- `contacts_create` — create contacts
- `contacts_update` — update contacts
- `contacts_delete` — delete contacts

### Slides (4)
- `slides_create` — create presentations
- `slides_read` — read slide content
- `slides_add_slide` — add slides with layouts
- `slides_add_text` — add text to slides

### Forms (3)
- `forms_create` — create forms
- `forms_read` — read form structure
- `forms_list_responses` — list form responses

---

## Build It Yourself Prompt

Want to rebuild this from scratch using Claude? Paste this into Claude Code Desktop:

> Build me a Python MCP server using FastMCP at ~/Desktop/google-workspace-mcp/. It should give me full access to Google Workspace with these tools:
>
> Gmail (7): search, read message, read thread, send (with CC/BCC, HTML, threading for replies), create draft, list labels, modify labels (archive, star, mark read/unread)
>
> Calendar (5): list calendars, get events (with time range + search), create event (with attendees, timezone, Google Meet link generation), update event, delete event
>
> Meet (4): create meeting space, get meeting space by name, list participants/sessions, get meeting artifacts (recordings, transcripts)
>
> Drive (6): search files, read file content (export Google Docs/Sheets/Slides to text), create file (plain text or Google Doc), list folder, share file, create folder
>
> Docs (5): create, read, insert text at position, find and replace, append text
>
> Sheets (6): read ranges, write values, append rows, create spreadsheet, clear ranges, get spreadsheet metadata
>
> Tasks (6): list task lists, list tasks, create task (with subtask support), update task, delete task, create task list
>
> Contacts (5): search by name/email/phone, list all, create, update, delete
>
> Slides (4): create presentation, read slide content, add slide with layout, add text to slide
>
> Forms (3): create form, read form structure, list responses
>
> Requirements:
> - Separate file per service (tools_gmail.py, tools_calendar.py, tools_meet.py, etc) plus auth.py and server.py
> - auth.py handles Google OAuth2: reads GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET from env vars, opens browser on first use, saves token to ~/.gw-mcp/token.json, auto-refreshes
> - Use google-api-python-client and google-auth-oauthlib
> - pyproject.toml with uv, entry point gw-mcp = "server:main"
> - .gitignore for .venv, __pycache__, .env, token.json, credentials.json
> - README with setup instructions for Google Cloud Console, running with uv, and adding to Claude Desktop + Claude Code configs
