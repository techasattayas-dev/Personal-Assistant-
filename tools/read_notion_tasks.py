"""
Tool: read_notion_tasks — Read and summarize tasks from Notion Tasks Database.

Queries the [CC] Tasks Database in Notion and returns a structured summary
including open tasks, overdue items, completion stats, and categorized views.

Requires NOTION_API_KEY and NOTION_TASKS_DB_ID in .env.
"""

import os
from datetime import date, datetime

import requests


NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _get_headers() -> dict | None:
    """Build Notion API headers. Returns None if API key is missing."""
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        return None
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _parse_task(page: dict) -> dict:
    """Extract task fields from a Notion page object."""
    props = page.get("properties", {})

    # Title
    title_arr = props.get("Task", {}).get("title", [])
    title = title_arr[0]["plain_text"] if title_arr else "Untitled"

    # Done (checkbox)
    done = props.get("Done", {}).get("checkbox", False)

    # Due Date
    due_data = props.get("Due Date", {}).get("date")
    due_str = due_data.get("start") if due_data else None

    # Recurring
    recurring = props.get("Recurring?", {}).get("checkbox", False)

    # Owner
    owners = props.get("Owner", {}).get("people", [])
    owner_names = [o.get("name", "Unknown") for o in owners]

    # Text (notes)
    text_arr = props.get("Text", {}).get("rich_text", [])
    text = text_arr[0]["plain_text"] if text_arr else ""

    # Page URL
    url = page.get("url", "")

    return {
        "title": title,
        "done": done,
        "due": due_str,
        "recurring": recurring,
        "owner": ", ".join(owner_names) or "Unassigned",
        "text": text,
        "url": url,
    }


def _compute_overdue_days(due_str: str) -> int:
    """Return number of days overdue (negative = not yet due)."""
    try:
        due_date = date.fromisoformat(due_str)
        return (date.today() - due_date).days
    except (ValueError, TypeError):
        return 0


def read_notion_tasks(
    view: str = "summary",
    filter_status: str = "all",
) -> str:
    """Read and summarize tasks from Notion Tasks Database.

    Args:
        view: Output format — 'summary' (default overview), 'detailed' (full list),
              or 'overdue' (only overdue tasks).
        filter_status: Filter by status — 'all', 'open', or 'done'.

    Returns:
        Formatted markdown summary of tasks.
    """
    headers = _get_headers()
    if not headers:
        return "ERROR: NOTION_API_KEY not set in .env file."

    db_id = os.getenv("NOTION_TASKS_DB_ID")
    if not db_id:
        return "ERROR: NOTION_TASKS_DB_ID not set in .env file."

    # Validate inputs
    valid_views = {"summary", "detailed", "overdue"}
    if view not in valid_views:
        return f"ERROR: Invalid view '{view}'. Valid: {sorted(valid_views)}"

    valid_filters = {"all", "open", "done"}
    if filter_status not in valid_filters:
        return f"ERROR: Invalid filter_status '{filter_status}'. Valid: {sorted(valid_filters)}"

    # Build query
    payload = {
        "page_size": 100,
        "sorts": [{"property": "Due Date", "direction": "ascending"}],
    }

    # Apply Notion-level filter for status
    if filter_status == "open":
        payload["filter"] = {"property": "Done", "checkbox": {"equals": False}}
    elif filter_status == "done":
        payload["filter"] = {"property": "Done", "checkbox": {"equals": True}}

    # Fetch tasks
    try:
        resp = requests.post(
            f"{NOTION_API_URL}/databases/{db_id}/query",
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.RequestException as e:
        return f"ERROR: Failed to connect to Notion API: {type(e).__name__}"

    if resp.status_code != 200:
        error = resp.json().get("message", resp.text[:200])
        return f"ERROR: Notion API returned {resp.status_code}: {error}"

    data = resp.json()
    results = data.get("results", [])

    if not results:
        return "No tasks found in the database."

    # Handle pagination if needed
    while data.get("has_more"):
        payload["start_cursor"] = data["next_cursor"]
        try:
            resp = requests.post(
                f"{NOTION_API_URL}/databases/{db_id}/query",
                headers=headers,
                json=payload,
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                results.extend(data.get("results", []))
            else:
                break
        except requests.RequestException:
            break

    # Parse all tasks
    tasks = [_parse_task(page) for page in results]
    today = date.today()

    # Categorize
    open_tasks = [t for t in tasks if not t["done"]]
    done_tasks = [t for t in tasks if t["done"]]
    overdue_tasks = []
    upcoming_tasks = []

    for t in open_tasks:
        if t["due"]:
            days = _compute_overdue_days(t["due"])
            t["days_overdue"] = days
            if days > 0:
                overdue_tasks.append(t)
            else:
                upcoming_tasks.append(t)
        else:
            t["days_overdue"] = 0
            upcoming_tasks.append(t)

    # Sort overdue by most overdue first
    overdue_tasks.sort(key=lambda t: t["days_overdue"], reverse=True)

    # Build output based on view
    lines = []
    lines.append(f"# [CC] Tasks Database Summary")
    lines.append(f"**Date**: {today.isoformat()}")
    lines.append("")

    # Stats block (always shown)
    lines.append("## Overview")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Tasks | {len(tasks)} |")
    lines.append(f"| Open | {len(open_tasks)} |")
    lines.append(f"| Done | {len(done_tasks)} |")
    lines.append(f"| Overdue | {len(overdue_tasks)} |")
    lines.append(f"| Upcoming | {len(upcoming_tasks)} |")
    if tasks:
        pct = len(done_tasks) / len(tasks) * 100
        lines.append(f"| Completion Rate | {pct:.0f}% |")
    lines.append("")

    if view == "overdue":
        # Overdue-only view
        if not overdue_tasks:
            lines.append("No overdue tasks.")
        else:
            lines.append(f"## Overdue Tasks ({len(overdue_tasks)})")
            lines.append("")
            lines.append("| # | Task | Due Date | Overdue | Owner |")
            lines.append("|---|------|----------|---------|-------|")
            for i, t in enumerate(overdue_tasks, 1):
                lines.append(
                    f"| {i} | {t['title']} | {t['due']} | "
                    f"{t['days_overdue']}d | {t['owner']} |"
                )
            lines.append("")

    elif view == "detailed":
        # Full list
        if open_tasks:
            lines.append(f"## Open Tasks ({len(open_tasks)})")
            lines.append("")
            for t in open_tasks:
                rec = " [Recurring]" if t["recurring"] else ""
                overdue_label = ""
                if t.get("days_overdue", 0) > 0:
                    overdue_label = f" — **OVERDUE {t['days_overdue']}d**"
                lines.append(f"- **{t['title']}**{rec}{overdue_label}")
                lines.append(f"  - Due: {t['due'] or 'No date'} | Owner: {t['owner']}")
                if t["text"]:
                    lines.append(f"  - Note: {t['text'][:200]}")
            lines.append("")

        if done_tasks:
            lines.append(f"## Completed Tasks ({len(done_tasks)})")
            lines.append("")
            for t in done_tasks:
                lines.append(f"- ~~{t['title']}~~ (Due: {t['due'] or 'N/A'})")
            lines.append("")

    else:
        # Summary view (default)
        if overdue_tasks:
            lines.append(f"## OVERDUE ({len(overdue_tasks)})")
            lines.append("")
            lines.append("| # | Task | Due Date | Overdue | Owner |")
            lines.append("|---|------|----------|---------|-------|")
            for i, t in enumerate(overdue_tasks, 1):
                lines.append(
                    f"| {i} | {t['title']} | {t['due']} | "
                    f"{t['days_overdue']}d | {t['owner']} |"
                )
            lines.append("")

        if upcoming_tasks:
            lines.append(f"## Upcoming ({len(upcoming_tasks)})")
            lines.append("")
            for t in upcoming_tasks:
                rec = " [Recurring]" if t["recurring"] else ""
                lines.append(f"- {t['title']}{rec} — Due: {t['due'] or 'No date'} | {t['owner']}")
            lines.append("")

        # Recent completions (last 5)
        recent_done = [t for t in done_tasks if t["due"]]
        recent_done.sort(key=lambda t: t["due"], reverse=True)
        if recent_done[:5]:
            lines.append("## Recently Completed (last 5)")
            lines.append("")
            for t in recent_done[:5]:
                lines.append(f"- ~~{t['title']}~~ (Done, due was {t['due']})")
            lines.append("")

    return "\n".join(lines)
