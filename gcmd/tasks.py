"""
Google Tasks operations module.
"""

from typing import Optional
from datetime import datetime

from .client import get_tasks_service


def list_tasks(tasklist_id: str = "@default", max_results: int = 100, show_completed: bool = False, show_hidden: bool = False) -> list[dict]:
    """
    List tasks from a task list.

    Args:
        tasklist_id: Task list ID (default: @default for the user's default task list)
        max_results: Maximum number of tasks to return
        show_completed: Include completed tasks
        show_hidden: Include hidden (deleted) tasks

    Returns:
        List of task dictionaries
    """
    service = get_tasks_service()

    # Build parameters
    params = {
        "tasklist": tasklist_id,
        "maxResults": max_results,
    }

    if show_completed:
        params["showCompleted"] = True

    if show_hidden:
        params["showHidden"] = True

    # Fetch tasks
    result = service.tasks().list(**params).execute()
    tasks = result.get("items", [])

    return tasks


def list_task_lists(max_results: int = 100) -> list[dict]:
    """
    List all task lists for the authenticated user.

    Args:
        max_results: Maximum number of task lists to return

    Returns:
        List of task list dictionaries
    """
    service = get_tasks_service()

    result = service.tasklists().list(maxResults=max_results).execute()
    task_lists = result.get("items", [])

    return task_lists


def format_task_list(tasks: list[dict], verbose: bool = False) -> str:
    """
    Format tasks for display.

    Args:
        tasks: List of task dictionaries
        verbose: Show detailed information

    Returns:
        Formatted string output
    """
    if not tasks:
        return "No tasks found."

    lines = []
    lines.append(f"\n{'='*70}")
    lines.append(f"TASKS ({len(tasks)} total)")
    lines.append(f"{'='*70}\n")

    for task in tasks:
        title = task.get("title", "(No title)")
        status = task.get("status", "needsAction")

        # Status indicator
        if status == "completed":
            indicator = "✓"
        else:
            indicator = "○"

        lines.append(f"{indicator} {title}")

        if verbose:
            # Show more details
            task_id = task.get("id", "N/A")
            lines.append(f"  ID: {task_id}")

            # Due date
            due = task.get("due")
            if due:
                try:
                    due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
                    lines.append(f"  Due: {due_dt.strftime('%Y-%m-%d %H:%M')}")
                except:
                    lines.append(f"  Due: {due}")

            # Notes
            notes = task.get("notes")
            if notes:
                # Truncate long notes
                if len(notes) > 100:
                    notes = notes[:100] + "..."
                lines.append(f"  Notes: {notes}")

            # Completed time
            if status == "completed":
                completed = task.get("completed")
                if completed:
                    try:
                        completed_dt = datetime.fromisoformat(completed.replace("Z", "+00:00"))
                        lines.append(f"  Completed: {completed_dt.strftime('%Y-%m-%d %H:%M')}")
                    except:
                        lines.append(f"  Completed: {completed}")

            # Updated time
            updated = task.get("updated")
            if updated:
                try:
                    updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    lines.append(f"  Updated: {updated_dt.strftime('%Y-%m-%d %H:%M')}")
                except:
                    lines.append(f"  Updated: {updated}")

            # Web link
            self_link = task.get("selfLink")
            if self_link:
                lines.append(f"  Link: {self_link}")

            lines.append("")  # Blank line between tasks

    lines.append(f"{'='*70}\n")
    return "\n".join(lines)


def format_task_lists(task_lists: list[dict]) -> str:
    """
    Format task lists for display.

    Args:
        task_lists: List of task list dictionaries

    Returns:
        Formatted string output
    """
    if not task_lists:
        return "No task lists found."

    lines = []
    lines.append(f"\n{'='*70}")
    lines.append(f"TASK LISTS ({len(task_lists)} total)")
    lines.append(f"{'='*70}\n")

    for task_list in task_lists:
        title = task_list.get("title", "(No title)")
        task_list_id = task_list.get("id", "N/A")
        updated = task_list.get("updated", "N/A")

        lines.append(f"📋 {title}")
        lines.append(f"   ID: {task_list_id}")

        try:
            updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            lines.append(f"   Updated: {updated_dt.strftime('%Y-%m-%d %H:%M')}")
        except:
            lines.append(f"   Updated: {updated}")

        lines.append("")  # Blank line between lists

    lines.append(f"{'='*70}\n")
    return "\n".join(lines)
