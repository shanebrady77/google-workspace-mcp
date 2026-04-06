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


def slides_insert_shape(presentation_id: str, slide_id: str, shape_type: str = "RECTANGLE",
                        x_pt: float = 100, y_pt: float = 100,
                        width_pt: float = 200, height_pt: float = 100) -> str:
    """Insert a shape onto a slide.

    Args:
        presentation_id: The presentation ID.
        slide_id: The slide object ID.
        shape_type: Shape type — 'RECTANGLE', 'ROUND_RECTANGLE', 'ELLIPSE', 'TRIANGLE',
            'DIAMOND', 'PENTAGON', 'HEXAGON', 'STAR', 'ARROW_EAST', 'ARROW_NORTH', etc.
        x_pt: X position in points.
        y_pt: Y position in points.
        width_pt: Width in points.
        height_pt: Height in points.
    """
    import uuid
    svc = _slides()
    shape_id = f"shape_{uuid.uuid4().hex[:8]}"
    svc.presentations().batchUpdate(presentationId=presentation_id, body={
        "requests": [{
            "createShape": {
                "objectId": shape_id,
                "shapeType": shape_type,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": width_pt, "unit": "PT"},
                             "height": {"magnitude": height_pt, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1,
                                  "translateX": x_pt, "translateY": y_pt, "unit": "PT"}
                }
            }
        }]
    }).execute()
    return json.dumps({"status": "shape_added", "shapeId": shape_id, "shapeType": shape_type})


def slides_insert_image(presentation_id: str, slide_id: str, image_url: str,
                        x_pt: float = 100, y_pt: float = 100,
                        width_pt: float = 300, height_pt: float = 200) -> str:
    """Insert an image onto a slide from a URL.

    Args:
        presentation_id: The presentation ID.
        slide_id: The slide object ID.
        image_url: Public URL of the image.
        x_pt: X position in points.
        y_pt: Y position in points.
        width_pt: Width in points.
        height_pt: Height in points.
    """
    import uuid
    svc = _slides()
    img_id = f"img_{uuid.uuid4().hex[:8]}"
    svc.presentations().batchUpdate(presentationId=presentation_id, body={
        "requests": [{
            "createImage": {
                "objectId": img_id,
                "url": image_url,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": width_pt, "unit": "PT"},
                             "height": {"magnitude": height_pt, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1,
                                  "translateX": x_pt, "translateY": y_pt, "unit": "PT"}
                }
            }
        }]
    }).execute()
    return json.dumps({"status": "image_added", "imageId": img_id})


def slides_insert_table(presentation_id: str, slide_id: str, rows: int, columns: int,
                        x_pt: float = 50, y_pt: float = 100,
                        width_pt: float = 600, height_pt: float = 300) -> str:
    """Insert a table onto a slide.

    Args:
        presentation_id: The presentation ID.
        slide_id: The slide object ID.
        rows: Number of rows.
        columns: Number of columns.
        x_pt: X position in points.
        y_pt: Y position in points.
        width_pt: Width in points.
        height_pt: Height in points.
    """
    import uuid
    svc = _slides()
    table_id = f"table_{uuid.uuid4().hex[:8]}"
    svc.presentations().batchUpdate(presentationId=presentation_id, body={
        "requests": [{
            "createTable": {
                "objectId": table_id,
                "rows": rows,
                "columns": columns,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": width_pt, "unit": "PT"},
                             "height": {"magnitude": height_pt, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1,
                                  "translateX": x_pt, "translateY": y_pt, "unit": "PT"}
                }
            }
        }]
    }).execute()
    return json.dumps({"status": "table_added", "tableId": table_id, "rows": rows, "columns": columns})


def slides_insert_video(presentation_id: str, slide_id: str, video_id: str,
                        x_pt: float = 100, y_pt: float = 100,
                        width_pt: float = 400, height_pt: float = 225) -> str:
    """Insert a YouTube video onto a slide.

    Args:
        presentation_id: The presentation ID.
        slide_id: The slide object ID.
        video_id: YouTube video ID (e.g. 'dQw4w9WgXcQ' from the URL).
        x_pt: X position in points.
        y_pt: Y position in points.
        width_pt: Width in points.
        height_pt: Height in points.
    """
    import uuid
    svc = _slides()
    vid_id = f"video_{uuid.uuid4().hex[:8]}"
    svc.presentations().batchUpdate(presentationId=presentation_id, body={
        "requests": [{
            "createVideo": {
                "objectId": vid_id,
                "source": "YOUTUBE",
                "id": video_id,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {"width": {"magnitude": width_pt, "unit": "PT"},
                             "height": {"magnitude": height_pt, "unit": "PT"}},
                    "transform": {"scaleX": 1, "scaleY": 1,
                                  "translateX": x_pt, "translateY": y_pt, "unit": "PT"}
                }
            }
        }]
    }).execute()
    return json.dumps({"status": "video_added", "videoId": vid_id})


def slides_format_text(presentation_id: str, shape_id: str, start_index: int, end_index: int,
                       bold: bool = None, italic: bool = None, underline: bool = None,
                       font_size: float = None, foreground_color: str = "") -> str:
    """Format text within a shape on a slide.

    Args:
        presentation_id: The presentation ID.
        shape_id: The shape/textbox object ID containing the text.
        start_index: Start character index in the shape's text.
        end_index: End character index in the shape's text.
        bold: Set bold.
        italic: Set italic.
        underline: Set underline.
        font_size: Font size in points.
        foreground_color: Hex color (e.g. '#FF0000').
    """
    svc = _slides()
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
    if font_size is not None:
        style["fontSize"] = {"magnitude": font_size, "unit": "PT"}
        fields.append("fontSize")
    if foreground_color:
        r = int(foreground_color[1:3], 16) / 255
        g = int(foreground_color[3:5], 16) / 255
        b = int(foreground_color[5:7], 16) / 255
        style["foregroundColor"] = {"opaqueColor": {"rgbColor": {"red": r, "green": g, "blue": b}}}
        fields.append("foregroundColor")

    svc.presentations().batchUpdate(presentationId=presentation_id, body={
        "requests": [{
            "updateTextStyle": {
                "objectId": shape_id,
                "textRange": {"type": "FIXED_RANGE", "startIndex": start_index, "endIndex": end_index},
                "style": style,
                "fields": ",".join(fields),
            }
        }]
    }).execute()
    return json.dumps({"status": "text_formatted", "shapeId": shape_id})


def slides_get_thumbnail(presentation_id: str, slide_id: str) -> str:
    """Get a thumbnail image URL for a slide.

    Args:
        presentation_id: The presentation ID.
        slide_id: The slide object ID.
    """
    svc = _slides()
    result = svc.presentations().pages().getThumbnail(
        presentationId=presentation_id, pageObjectId=slide_id,
        thumbnailProperties_thumbnailSize="LARGE"
    ).execute()
    return json.dumps({
        "slideId": slide_id,
        "contentUrl": result.get("contentUrl", ""),
        "width": result.get("width", 0),
        "height": result.get("height", 0),
    })
