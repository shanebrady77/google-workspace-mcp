"""Google Drive tools — search, read content, create, list, share files."""

import json
import io
from typing import Optional
from auth import get_service
from googleapiclient.http import MediaIoBaseUpload


def _drive():
    return get_service("drive", "v3")


def drive_search(query: str = "", max_results: int = 20) -> str:
    """Search Google Drive files.

    Args:
        query: Drive search query (e.g. 'name contains \"report\"', 'mimeType=\"application/pdf\"',
               'modifiedTime > \"2026-01-01\"'). Empty returns recent files.
        max_results: Maximum number of files to return.
    """
    svc = _drive()
    kwargs = {
        "pageSize": max_results,
        "fields": "files(id, name, mimeType, modifiedTime, size, webViewLink, parents, shared)",
    }
    if query:
        kwargs["q"] = query

    result = svc.files().list(**kwargs).execute()
    files = result.get("files", [])
    return json.dumps(files, indent=2) if files else "No files found."


def drive_read_file(file_id: str) -> str:
    """Read the text content of a Google Drive file (Docs, Sheets, or text files).

    Args:
        file_id: The Drive file ID.
    """
    svc = _drive()
    meta = svc.files().get(fileId=file_id, fields="mimeType, name").execute()
    mime = meta.get("mimeType", "")

    # Google Docs → export as plain text
    if mime == "application/vnd.google-apps.document":
        content = svc.files().export(fileId=file_id, mimeType="text/plain").execute()
        return content.decode("utf-8") if isinstance(content, bytes) else content

    # Google Sheets → export as CSV
    if mime == "application/vnd.google-apps.spreadsheet":
        content = svc.files().export(fileId=file_id, mimeType="text/csv").execute()
        return content.decode("utf-8") if isinstance(content, bytes) else content

    # Google Slides → export as plain text
    if mime == "application/vnd.google-apps.presentation":
        content = svc.files().export(fileId=file_id, mimeType="text/plain").execute()
        return content.decode("utf-8") if isinstance(content, bytes) else content

    # Regular files → download
    content = svc.files().get_media(fileId=file_id).execute()
    if isinstance(content, bytes):
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return f"[Binary file: {meta.get('name', 'unknown')} ({len(content)} bytes)]"
    return content


def drive_create_file(name: str, content: str = "", mime_type: str = "text/plain",
                      folder_id: str = "", as_google_doc: bool = False) -> str:
    """Create a new file in Google Drive.

    Args:
        name: File name.
        content: File content (text).
        mime_type: MIME type of the content being uploaded.
        folder_id: Parent folder ID (empty = root).
        as_google_doc: If True, convert to Google Docs format.
    """
    svc = _drive()
    file_metadata = {"name": name}
    if folder_id:
        file_metadata["parents"] = [folder_id]
    if as_google_doc:
        file_metadata["mimeType"] = "application/vnd.google-apps.document"

    if content:
        media = MediaIoBaseUpload(io.BytesIO(content.encode("utf-8")), mimetype=mime_type)
        result = svc.files().create(body=file_metadata, media_body=media, fields="id, name, webViewLink").execute()
    else:
        result = svc.files().create(body=file_metadata, fields="id, name, webViewLink").execute()

    return json.dumps({"status": "created", "id": result["id"], "name": result["name"],
                       "webViewLink": result.get("webViewLink", "")})


def drive_list_folder(folder_id: str = "root", max_results: int = 50) -> str:
    """List contents of a Drive folder.

    Args:
        folder_id: Folder ID to list (default 'root').
        max_results: Maximum items to return.
    """
    svc = _drive()
    result = svc.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        pageSize=max_results,
        fields="files(id, name, mimeType, modifiedTime, size)",
        orderBy="folder, name"
    ).execute()
    files = result.get("files", [])
    return json.dumps(files, indent=2) if files else "Folder is empty."


def drive_share_file(file_id: str, email: str, role: str = "reader",
                     send_notification: bool = True) -> str:
    """Share a Drive file with a user.

    Args:
        file_id: The file ID to share.
        email: Email address to share with.
        role: Permission role — 'reader', 'writer', or 'commenter'.
        send_notification: Whether to send a notification email.
    """
    svc = _drive()
    permission = {"type": "user", "role": role, "emailAddress": email}
    result = svc.permissions().create(
        fileId=file_id, body=permission, sendNotificationEmail=send_notification,
        fields="id, role, emailAddress"
    ).execute()
    return json.dumps({"status": "shared", "permission": result})


def drive_create_folder(name: str, parent_id: str = "") -> str:
    """Create a folder in Google Drive.

    Args:
        name: Folder name.
        parent_id: Parent folder ID (empty = root).
    """
    svc = _drive()
    metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]
    result = svc.files().create(body=metadata, fields="id, name, webViewLink").execute()
    return json.dumps({"status": "created", "id": result["id"], "name": result["name"],
                       "webViewLink": result.get("webViewLink", "")})
