"""Google Tasks tools — list, create, update, delete tasks and task lists."""

import json
from auth import get_service


def _tasks():
    return get_service("tasks", "v1")


def tasks_list_tasklists() -> str:
    """List all task lists."""
    svc = _tasks()
    result = svc.tasklists().list().execute()
    lists = [{"id": tl["id"], "title": tl["title"], "updated": tl.get("updated", "")}
             for tl in result.get("items", [])]
    return json.dumps(lists, indent=2)


def tasks_list(tasklist_id: str = "@default", show_completed: bool = False,
               max_results: int = 50) -> str:
    """List tasks in a task list.

    Args:
        tasklist_id: Task list ID (default '@default' for the primary list).
        show_completed: Whether to include completed tasks.
        max_results: Maximum tasks to return.
    """
    svc = _tasks()
    result = svc.tasks().list(
        tasklist=tasklist_id, maxResults=max_results,
        showCompleted=show_completed, showHidden=show_completed
    ).execute()
    tasks = []
    for t in result.get("items", []):
        tasks.append({
            "id": t["id"],
            "title": t.get("title", ""),
            "status": t.get("status", ""),
            "due": t.get("due", ""),
            "notes": t.get("notes", ""),
            "parent": t.get("parent", ""),
            "updated": t.get("updated", ""),
        })
    return json.dumps(tasks, indent=2)


def tasks_create(title: str, tasklist_id: str = "@default", notes: str = "",
                 due: str = "", parent: str = "") -> str:
    """Create a new task.

    Args:
        title: Task title.
        tasklist_id: Task list ID (default '@default').
        notes: Task notes/description.
        due: Due date in RFC3339 format (e.g. '2026-04-01T00:00:00Z').
        parent: Parent task ID for creating subtasks.
    """
    svc = _tasks()
    task = {"title": title}
    if notes:
        task["notes"] = notes
    if due:
        task["due"] = due

    kwargs = {"tasklist": tasklist_id, "body": task}
    if parent:
        kwargs["parent"] = parent

    result = svc.tasks().insert(**kwargs).execute()
    return json.dumps({"status": "created", "id": result["id"], "title": result["title"]})


def tasks_update(task_id: str, tasklist_id: str = "@default", title: str = "",
                 notes: str = "", status: str = "", due: str = "") -> str:
    """Update an existing task.

    Args:
        task_id: The task ID.
        tasklist_id: Task list ID.
        title: New title (empty = no change).
        notes: New notes (empty = no change).
        status: New status — 'needsAction' or 'completed'.
        due: New due date in RFC3339 format.
    """
    svc = _tasks()
    task = svc.tasks().get(tasklist=tasklist_id, task=task_id).execute()

    if title:
        task["title"] = title
    if notes:
        task["notes"] = notes
    if status:
        task["status"] = status
    if due:
        task["due"] = due

    result = svc.tasks().update(tasklist=tasklist_id, task=task_id, body=task).execute()
    return json.dumps({"status": "updated", "id": result["id"], "title": result["title"]})


def tasks_delete(task_id: str, tasklist_id: str = "@default") -> str:
    """Delete a task.

    Args:
        task_id: The task ID to delete.
        tasklist_id: Task list ID.
    """
    svc = _tasks()
    svc.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
    return json.dumps({"status": "deleted", "id": task_id})


def tasks_create_tasklist(title: str) -> str:
    """Create a new task list.

    Args:
        title: Name of the new task list.
    """
    svc = _tasks()
    result = svc.tasklists().insert(body={"title": title}).execute()
    return json.dumps({"status": "created", "id": result["id"], "title": result["title"]})
