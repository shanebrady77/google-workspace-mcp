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


def docs_insert_table(document_id: str, rows: int, columns: int, index: int = 1) -> str:
    """Insert a table into a Google Doc.

    Args:
        document_id: The Google Doc ID.
        rows: Number of rows.
        columns: Number of columns.
        index: Character index to insert at (1 = beginning).
    """
    svc = _docs()
    svc.documents().batchUpdate(documentId=document_id, body={
        "requests": [{
            "insertTable": {
                "rows": rows, "columns": columns,
                "location": {"index": index}
            }
        }]
    }).execute()
    return json.dumps({"status": "table_inserted", "documentId": document_id,
                       "rows": rows, "columns": columns})


def docs_insert_image(document_id: str, image_uri: str, index: int = 1,
                      width_pt: float = 300, height_pt: float = 200) -> str:
    """Insert an image into a Google Doc from a URL.

    Args:
        document_id: The Google Doc ID.
        image_uri: Public URL of the image to insert.
        index: Character index to insert at.
        width_pt: Image width in points.
        height_pt: Image height in points.
    """
    svc = _docs()
    svc.documents().batchUpdate(documentId=document_id, body={
        "requests": [{
            "insertInlineImage": {
                "uri": image_uri,
                "location": {"index": index},
                "objectSize": {
                    "width": {"magnitude": width_pt, "unit": "PT"},
                    "height": {"magnitude": height_pt, "unit": "PT"},
                }
            }
        }]
    }).execute()
    return json.dumps({"status": "image_inserted", "documentId": document_id})


def docs_format_text(document_id: str, start_index: int, end_index: int,
                     bold: bool = None, italic: bool = None, underline: bool = None,
                     strikethrough: bool = None, font_size: float = None,
                     foreground_color: str = "") -> str:
    """Apply formatting to a range of text in a Google Doc.

    Args:
        document_id: The Google Doc ID.
        start_index: Start character index of the range.
        end_index: End character index of the range.
        bold: Set bold (True/False/None for no change).
        italic: Set italic.
        underline: Set underline.
        strikethrough: Set strikethrough.
        font_size: Font size in points (e.g. 12, 14, 18).
        foreground_color: Hex color string (e.g. '#FF0000' for red). Empty = no change.
    """
    svc = _docs()
    style = {}
    fields = []

    if bold is not None:
        style["bold"] = bold
        fields.append("bold")
    if italic is not None:
        style["italic"] = italic
        fields.append("italic")
    if underline is not None:
        style["underline"] = underline
        fields.append("underline")
    if strikethrough is not None:
        style["strikethrough"] = strikethrough
        fields.append("strikethrough")
    if font_size is not None:
        style["fontSize"] = {"magnitude": font_size, "unit": "PT"}
        fields.append("fontSize")
    if foreground_color:
        r = int(foreground_color[1:3], 16) / 255
        g = int(foreground_color[3:5], 16) / 255
        b = int(foreground_color[5:7], 16) / 255
        style["foregroundColor"] = {"color": {"rgbColor": {"red": r, "green": g, "blue": b}}}
        fields.append("foregroundColor")

    svc.documents().batchUpdate(documentId=document_id, body={
        "requests": [{
            "updateTextStyle": {
                "range": {"startIndex": start_index, "endIndex": end_index},
                "textStyle": style,
                "fields": ",".join(fields),
            }
        }]
    }).execute()
    return json.dumps({"status": "formatted", "documentId": document_id, "fields": fields})


def docs_insert_bullets(document_id: str, start_index: int, end_index: int,
                        bullet_type: str = "BULLET_DISC_CIRCLE_SQUARE") -> str:
    """Apply bullet or numbered list formatting to paragraphs in a Google Doc.

    Args:
        document_id: The Google Doc ID.
        start_index: Start character index of the range.
        end_index: End character index of the range.
        bullet_type: Bullet preset — 'BULLET_DISC_CIRCLE_SQUARE', 'BULLET_DIAMONDX_ARROW3D_SQUARE',
            'BULLET_CHECKBOX', 'NUMBERED_DECIMAL_ALPHA_ROMAN', 'NUMBERED_DECIMAL_NESTED',
            'NUMBERED_UPPERALPHA_ALPHA_ROMAN', 'NUMBERED_UPPERROMAN_UPPERALPHA_DECIMAL'.
    """
    svc = _docs()
    svc.documents().batchUpdate(documentId=document_id, body={
        "requests": [{
            "createParagraphBullets": {
                "range": {"startIndex": start_index, "endIndex": end_index},
                "bulletPreset": bullet_type,
            }
        }]
    }).execute()
    return json.dumps({"status": "bullets_applied", "documentId": document_id})


def docs_insert_page_break(document_id: str, index: int) -> str:
    """Insert a page break in a Google Doc.

    Args:
        document_id: The Google Doc ID.
        index: Character index to insert the page break at.
    """
    svc = _docs()
    svc.documents().batchUpdate(documentId=document_id, body={
        "requests": [{
            "insertPageBreak": {"location": {"index": index}}
        }]
    }).execute()
    return json.dumps({"status": "page_break_inserted", "documentId": document_id})
