"""Google Slides tools — create presentations, read content, add/update slides."""

import json
from auth import get_service


def _slides():
    return get_service("slides", "v1")


def slides_create(title: str) -> str:
    """Create a new Google Slides presentation.

    Args:
        title: Presentation title.
    """
    svc = _slides()
    result = svc.presentations().create(body={"title": title}).execute()
    return json.dumps({
        "status": "created",
        "presentationId": result["presentationId"],
        "title": result["title"],
        "url": f"https://docs.google.com/presentation/d/{result['presentationId']}/edit"
    })


def slides_read(presentation_id: str) -> str:
    """Read a Google Slides presentation (metadata and text content).

    Args:
        presentation_id: The presentation ID.
    """
    svc = _slides()
    pres = svc.presentations().get(presentationId=presentation_id).execute()

    slides = []
    for slide in pres.get("slides", []):
        slide_text = []
        for element in slide.get("pageElements", []):
            shape = element.get("shape", {})
            for tf in [shape.get("text", {})]:
                for te in tf.get("textElements", []):
                    if "textRun" in te:
                        slide_text.append(te["textRun"]["content"])
        slides.append({
            "objectId": slide["objectId"],
            "text": "".join(slide_text).strip()
        })

    return json.dumps({
        "presentationId": pres["presentationId"],
        "title": pres["title"],
        "slideCount": len(slides),
        "slides": slides,
        "url": f"https://docs.google.com/presentation/d/{presentation_id}/edit"
    }, indent=2)


def slides_add_slide(presentation_id: str, layout: str = "BLANK",
                     insertion_index: int = -1) -> str:
    """Add a new slide to a presentation.

    Args:
        presentation_id: The presentation ID.
        layout: Slide layout — 'BLANK', 'CAPTION_ONLY', 'TITLE', 'TITLE_AND_BODY', 'TITLE_AND_TWO_COLUMNS', etc.
        insertion_index: Position to insert at (-1 = end).
    """
    svc = _slides()
    request = {"createSlide": {"slideLayoutReference": {"predefinedLayout": layout}}}
    if insertion_index >= 0:
        request["createSlide"]["insertionIndex"] = insertion_index

    result = svc.presentations().batchUpdate(
        presentationId=presentation_id, body={"requests": [request]}
    ).execute()
    slide_id = result["replies"][0]["createSlide"]["objectId"]
    return json.dumps({"status": "slide_added", "slideId": slide_id})


def slides_add_text_to_slide(presentation_id: str, slide_id: str, text: str,
                              shape_id: str = "") -> str:
    """Insert text into a shape on a slide.

    Args:
        presentation_id: The presentation ID.
        slide_id: The slide object ID (not used if shape_id is provided).
        text: Text to insert.
        shape_id: Shape/placeholder object ID to insert text into. If empty, creates a new text box.
    """
    svc = _slides()
    requests = []

    if not shape_id:
        # Create a text box on the slide
        import uuid
        shape_id = f"textbox_{uuid.uuid4().hex[:8]}"
        requests.append({
            "createShape": {
                "objectId": shape_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 500, "unit": "PT"},
                        "height": {"magnitude": 300, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1, "scaleY": 1,
                        "translateX": 50, "translateY": 100,
                        "unit": "PT"
                    }
                }
            }
        })

    requests.append({
        "insertText": {"objectId": shape_id, "text": text, "insertionIndex": 0}
    })

    svc.presentations().batchUpdate(
        presentationId=presentation_id, body={"requests": requests}
    ).execute()
    return json.dumps({"status": "text_added", "shapeId": shape_id})
