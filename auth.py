"""
Google OAuth2 authentication and service builder.
Handles OAuth flow, token storage, token refresh, and building Google API service objects.
"""

import json
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Where tokens get stored
TOKEN_DIR = Path.home() / ".gw-mcp"
TOKEN_FILE = TOKEN_DIR / "token.json"
CREDS_FILE = TOKEN_DIR / "credentials.json"

# All scopes needed for full workspace access
SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/contacts",
    "https://www.googleapis.com/auth/meetings.space.created",
    "https://www.googleapis.com/auth/meetings.space.readonly",
]

# Service cache so we don't rebuild on every call
_service_cache: dict = {}


def _get_credentials() -> Credentials:
    """Get valid OAuth2 credentials, refreshing or re-authenticating as needed."""
    creds = None

    # Try loading existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # If no valid creds, do the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Build credentials.json from env vars if it doesn't exist
            if not CREDS_FILE.exists():
                client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
                client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
                if not client_id or not client_secret:
                    raise RuntimeError(
                        "No credentials found. Either place credentials.json in ~/.gw-mcp/ "
                        "or set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET env vars."
                    )
                TOKEN_DIR.mkdir(parents=True, exist_ok=True)
                creds_data = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
                    }
                }
                CREDS_FILE.write_text(json.dumps(creds_data))

            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for next time
        TOKEN_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())

    return creds


def get_service(service_name: str, version: str):
    """Build and cache a Google API service object."""
    cache_key = f"{service_name}:{version}"
    if cache_key not in _service_cache:
        creds = _get_credentials()
        _service_cache[cache_key] = build(service_name, version, credentials=creds)
    return _service_cache[cache_key]


def clear_cache():
    """Clear the service cache (useful after re-auth)."""
    _service_cache.clear()
