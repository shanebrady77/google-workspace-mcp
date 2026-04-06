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


def drive_copy_file(file_id: str, name: str = "", folder_id: str = "") -> str:
    """Copy a file in Google Drive.

    Args:
        file_id: The file ID to copy.
        name: Name for the copy (empty = 'Copy of <original>').
        folder_id: Destination folder ID (empty = same folder).
    """
    svc = _drive()
    body = {}
    if name:
        body["name"] = name
    if folder_id:
        body["parents"] = [folder_id]
    result = svc.files().copy(fileId=file_id, body=body, fields="id, name, webViewLink").execute()
    return json.dumps({"status": "copied", "id": result["id"], "name": result["name"],
                       "webViewLink": result.get("webViewLink", "")})


def drive_export(file_id: str, mime_type: str) -> str:
    """Export a Google Workspace file to a specific format.

    Args:
        file_id: The file ID to export.
        mime_type: Target MIME type. Common options:
            - 'application/pdf' (Docs, Sheets, Slides)
            - 'text/plain' (Docs)
            - 'text/csv' (Sheets)
            - 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' (Docs → DOCX)
            - 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' (Sheets → XLSX)
            - 'application/vnd.openxmlformats-officedocument.presentationml.presentation' (Slides → PPTX)
            - 'image/png' (Slides → PNG)
    """
    svc = _drive()
    content = svc.files().export(fileId=file_id, mimeType=mime_type).execute()
    if isinstance(content, bytes):
        import base64
        return json.dumps({"size": len(content), "mimeType": mime_type,
                           "data": base64.b64encode(content).decode()})
    return content


def drive_add_comment(file_id: str, content: str) -> str:
    """Add a comment to a Drive file.

    Args:
        file_id: The file ID to comment on.
        content: Comment text.
    """
    svc = _drive()
    result = svc.comments().create(
        fileId=file_id, body={"content": content}, fields="id, content, author, createdTime"
    ).execute()
    return json.dumps({"status": "comment_added", "id": result["id"],
                       "author": result.get("author", {}).get("displayName", ""),
                       "createdTime": result.get("createdTime", "")})


def drive_list_comments(file_id: str, max_results: int = 20) -> str:
    """List comments on a Drive file.

    Args:
        file_id: The file ID.
        max_results: Maximum comments to return.
    """
    svc = _drive()
    result = svc.comments().list(
        fileId=file_id, pageSize=max_results,
        fields="comments(id, content, author, createdTime, resolved, replies)"
    ).execute()
    comments = []
    for c in result.get("comments", []):
        comments.append({
            "id": c["id"],
            "content": c.get("content", ""),
            "author": c.get("author", {}).get("displayName", ""),
            "createdTime": c.get("createdTime", ""),
            "resolved": c.get("resolved", False),
            "replies": [{"content": r.get("content", ""), "author": r.get("author", {}).get("displayName", "")}
                        for r in c.get("replies", [])],
        })
    return json.dumps(comments, indent=2)


def drive_list_revisions(file_id: str) -> str:
    """List file revisions (version history).

    Args:
        file_id: The file ID.
    """
    svc = _drive()
    result = svc.revisions().list(fileId=file_id, fields="revisions(id, modifiedTime, lastModifyingUser, size)").execute()
    revisions = []
    for r in result.get("revisions", []):
        revisions.append({
            "id": r["id"],
            "modifiedTime": r.get("modifiedTime", ""),
            "lastModifyingUser": r.get("lastModifyingUser", {}).get("displayName", ""),
            "size": r.get("size", ""),
        })
    return json.dumps(revisions, indent=2)


def drive_list_permissions(file_id: str) -> str:
    """List sharing permissions on a file.

    Args:
        file_id: The file ID.
    """
    svc = _drive()
    result = svc.permissions().list(
        fileId=file_id, fields="permissions(id, type, role, emailAddress, displayName)"
    ).execute()
    return json.dumps(result.get("permissions", []), indent=2)


def drive_delete_permission(file_id: str, permission_id: str) -> str:
    """Remove a sharing permission from a file.

    Args:
        file_id: The file ID.
        permission_id: The permission ID to remove (from drive_list_permissions).
    """
    svc = _drive()
    svc.permissions().delete(fileId=file_id, permissionId=permission_id).execute()
    return json.dumps({"status": "permission_removed", "fileId": file_id, "permissionId": permission_id})


def drive_trash(file_id: str) -> str:
    """Move a file to the trash.

    Args:
        file_id: The file ID to trash.
    """
    svc = _drive()
    svc.files().update(fileId=file_id, body={"trashed": True}).execute()
    return json.dumps({"status": "trashed", "id": file_id})


def drive_untrash(file_id: str) -> str:
    """Restore a file from the trash.

    Args:
        file_id: The file ID to restore.
    """
    svc = _drive()
    svc.files().update(fileId=file_id, body={"trashed": False}).execute()
    return json.dumps({"status": "untrashed", "id": file_id})
