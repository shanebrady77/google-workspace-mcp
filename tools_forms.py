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
