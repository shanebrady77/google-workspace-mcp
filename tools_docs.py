"""Google Docs tools — create, read, edit text, find and replace."""

import json
from auth import get_service


def _docs():
    return get_service("docs", "v1")


def docs_create(title: str, body_text: str = "") -> str:
    """Create a new Google Doc.

    Args:
        title: Document title.
        body_text: Initial text content to insert (optional).
    """
    svc = _docs()
    doc = svc.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    if body_text:
        svc.documents().batchUpdate(documentId=doc_id, body={
            "requests": [{"insertText": {"location": {"index": 1}, "text": body_text}}]
        }).execute()

    return json.dumps({
        "status": "created",
        "documentId": doc_id,
        "title": doc["title"],
        "url": f"https://docs.google.com/document/d/{doc_id}/edit"
    })


def docs_read(document_id: str) -> str:
    """Read the full text content of a Google Doc.

    Args:
        document_id: The Google Doc ID.
    """
    svc = _docs()
    doc = svc.documents().get(documentId=document_id).execute()

    # Extract all text content
    text_parts = []
    for element in doc.get("body", {}).get("content", []):
        if "paragraph" in element:
            for run in element["paragraph"].get("elements", []):
                if "textRun" in run:
                    text_parts.append(run["textRun"]["content"])

    return json.dumps({
        "documentId": doc["documentId"],
        "title": doc["title"],
        "text": "".join(text_parts),
        "url": f"https://docs.google.com/document/d/{document_id}/edit"
    })


def docs_insert_text(document_id: str, text: str, index: int = 1) -> str:
    """Insert text into a Google Doc at a specific position.

    Args:
        document_id: The Google Doc ID.
        text: Text to insert.
        index: Character index to insert at (1 = beginning of doc).
    """
    svc = _docs()
    svc.documents().batchUpdate(documentId=document_id, body={
        "requests": [{"insertText": {"location": {"index": index}, "text": text}}]
    }).execute()
    return json.dumps({"status": "text_inserted", "documentId": document_id})


def docs_find_replace(document_id: str, find_text: str, replace_text: str,
                      match_case: bool = False) -> str:
    """Find and replace text in a Google Doc.

    Args:
        document_id: The Google Doc ID.
        find_text: Text to find.
        replace_text: Replacement text.
        match_case: Whether the search is case-sensitive.
    """
    svc = _docs()
    result = svc.documents().batchUpdate(documentId=document_id, body={
        "requests": [{
            "replaceAllText": {
                "containsText": {"text": find_text, "matchCase": match_case},
                "replaceText": replace_text
            }
        }]
    }).execute()
    count = result.get("replies", [{}])[0].get("replaceAllText", {}).get("occurrencesChanged", 0)
    return json.dumps({"status": "replaced", "occurrencesChanged": count})


def docs_append_text(document_id: str, text: str) -> str:
    """Append text to the end of a Google Doc.

    Args:
        document_id: The Google Doc ID.
        text: Text to append.
    """
    svc = _docs()
    doc = svc.documents().get(documentId=document_id).execute()
    # Find the end index of the body content
    body_content = doc.get("body", {}).get("content", [])
    end_index = body_content[-1]["endIndex"] - 1 if body_content else 1

    svc.documents().batchUpdate(documentId=document_id, body={
        "requests": [{"insertText": {"location": {"index": end_index}, "text": text}}]
    }).execute()
    return json.dumps({"status": "text_appended", "documentId": document_id})
