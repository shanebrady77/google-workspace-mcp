"""Google Forms tools — create forms, read form details, list responses."""

import json
from auth import get_service


def _forms():
    return get_service("forms", "v1")


def forms_create(title: str, description: str = "") -> str:
    """Create a new Google Form.

    Args:
        title: Form title.
        description: Form description.
    """
    svc = _forms()
    form = {"info": {"title": title}}
    if description:
        form["info"]["description"] = description

    result = svc.forms().create(body=form).execute()
    return json.dumps({
        "status": "created",
        "formId": result["formId"],
        "responderUri": result.get("responderUri", ""),
        "url": f"https://docs.google.com/forms/d/{result['formId']}/edit"
    })


def forms_read(form_id: str) -> str:
    """Read a Google Form's structure and questions.

    Args:
        form_id: The form ID.
    """
    svc = _forms()
    form = svc.forms().get(formId=form_id).execute()

    questions = []
    for item in form.get("items", []):
        q = item.get("questionItem", {}).get("question", {})
        q_info = {
            "itemId": item.get("itemId", ""),
            "title": item.get("title", ""),
            "questionId": q.get("questionId", ""),
            "required": q.get("required", False),
        }
        # Determine question type
        if "choiceQuestion" in q:
            q_info["type"] = q["choiceQuestion"].get("type", "RADIO")
            q_info["options"] = [o.get("value", "") for o in q["choiceQuestion"].get("options", [])]
        elif "textQuestion" in q:
            q_info["type"] = "TEXT"
            q_info["paragraph"] = q["textQuestion"].get("paragraph", False)
        elif "scaleQuestion" in q:
            q_info["type"] = "SCALE"
            q_info["low"] = q["scaleQuestion"].get("low", 1)
            q_info["high"] = q["scaleQuestion"].get("high", 5)
        else:
            q_info["type"] = "UNKNOWN"
        questions.append(q_info)

    return json.dumps({
        "formId": form["formId"],
        "title": form.get("info", {}).get("title", ""),
        "description": form.get("info", {}).get("description", ""),
        "responderUri": form.get("responderUri", ""),
        "questions": questions,
    }, indent=2)


def forms_list_responses(form_id: str, max_results: int = 50) -> str:
    """List responses to a Google Form.

    Args:
        form_id: The form ID.
        max_results: Maximum responses to return.
    """
    svc = _forms()
    result = svc.forms().responses().list(formId=form_id, pageSize=max_results).execute()

    responses = []
    for r in result.get("responses", []):
        answers = {}
        for qid, answer in r.get("answers", {}).items():
            text_answers = answer.get("textAnswers", {}).get("answers", [])
            answers[qid] = [a.get("value", "") for a in text_answers]
        responses.append({
            "responseId": r["responseId"],
            "createTime": r.get("createTime", ""),
            "lastSubmittedTime": r.get("lastSubmittedTime", ""),
            "answers": answers,
        })

    return json.dumps({"total": len(responses), "responses": responses}, indent=2)


def forms_add_question(form_id: str, title: str, question_type: str = "TEXT",
                       required: bool = False, options: list[str] = None,
                       paragraph: bool = False, index: int = -1) -> str:
    """Add a question to a Google Form.

    Args:
        form_id: The form ID.
        title: Question title/text.
        question_type: Question type — 'TEXT', 'PARAGRAPH', 'RADIO', 'CHECKBOX', 'DROP_DOWN', 'SCALE'.
        required: Whether the question is required.
        options: List of options for RADIO, CHECKBOX, or DROP_DOWN questions.
        paragraph: If True for TEXT type, makes it a long-answer field.
        index: Position to insert at (-1 = end).
    """
    svc = _forms()
    question = {"required": required}

    if question_type in ("RADIO", "CHECKBOX", "DROP_DOWN"):
        question["choiceQuestion"] = {
            "type": question_type,
            "options": [{"value": o} for o in (options or ["Option 1"])],
        }
    elif question_type == "SCALE":
        question["scaleQuestion"] = {"low": 1, "high": 5, "lowLabel": "", "highLabel": ""}
    else:
        question["textQuestion"] = {"paragraph": paragraph or question_type == "PARAGRAPH"}

    item = {"title": title, "questionItem": {"question": question}}
    request = {"createItem": {"item": item, "location": {"index": max(index, 0) if index >= 0 else 0}}}

    result = svc.forms().batchUpdate(formId=form_id, body={"requests": [request]}).execute()
    return json.dumps({"status": "question_added", "formId": form_id})


def forms_update_question(form_id: str, item_index: int, title: str = "",
                          required: bool = None) -> str:
    """Update an existing question in a Google Form.

    Args:
        form_id: The form ID.
        item_index: The 0-based index of the item to update.
        title: New title (empty = no change).
        required: New required setting (None = no change).
    """
    svc = _forms()
    requests = []
    update_mask = []

    item = {}
    if title:
        item["title"] = title
        update_mask.append("title")
    if required is not None:
        item["questionItem"] = {"question": {"required": required}}
        update_mask.append("questionItem.question.required")

    if update_mask:
        requests.append({
            "updateItem": {
                "item": item,
                "location": {"index": item_index},
                "updateMask": ",".join(update_mask),
            }
        })

    svc.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()
    return json.dumps({"status": "question_updated", "formId": form_id, "index": item_index})


def forms_delete_question(form_id: str, item_index: int) -> str:
    """Delete a question from a Google Form.

    Args:
        form_id: The form ID.
        item_index: The 0-based index of the item to delete.
    """
    svc = _forms()
    svc.forms().batchUpdate(formId=form_id, body={
        "requests": [{"deleteItem": {"location": {"index": item_index}}}]
    }).execute()
    return json.dumps({"status": "question_deleted", "formId": form_id, "index": item_index})


def forms_move_question(form_id: str, from_index: int, to_index: int) -> str:
    """Move/reorder a question in a Google Form.

    Args:
        form_id: The form ID.
        from_index: Current 0-based index of the item.
        to_index: New 0-based index to move it to.
    """
    svc = _forms()
    svc.forms().batchUpdate(formId=form_id, body={
        "requests": [{
            "moveItem": {
                "originalLocation": {"index": from_index},
                "newLocation": {"index": to_index},
            }
        }]
    }).execute()
    return json.dumps({"status": "question_moved", "from": from_index, "to": to_index})


def forms_update_settings(form_id: str, is_quiz: bool = None,
                          description: str = "") -> str:
    """Update form info and settings.

    Args:
        form_id: The form ID.
        is_quiz: Set True to make this a quiz, False for regular form.
        description: New form description (empty = no change).
    """
    svc = _forms()
    requests = []
    if is_quiz is not None:
        requests.append({
            "updateSettings": {
                "settings": {"quizSettings": {"isQuiz": is_quiz}},
                "updateMask": "quizSettings.isQuiz",
            }
        })
    if description:
        requests.append({
            "updateFormInfo": {
                "info": {"description": description},
                "updateMask": "description",
            }
        })

    if requests:
        svc.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()
    return json.dumps({"status": "settings_updated", "formId": form_id})
