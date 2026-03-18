"""
Tool: read_notion_projects — Read and summarize projects from Notion Projects Database.

Queries the [CC] Projects Database in Notion and returns a structured summary
including project status, timelines, related tasks/notes counts, and categorized views.

Requires NOTION_API_KEY and NOTION_PROJECTS_DB_ID in .env.
"""

import os
from datetime import date

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


def _parse_project(page: dict) -> dict:
    """Extract project fields from a Notion page object."""
    props = page.get("properties", {})

    # Title
    title_arr = props.get("Project", {}).get("title", [])
    title = title_arr[0]["plain_text"] if title_arr else "Untitled"

    # Status (select)
    status_data = props.get("Status", {}).get("select")
    status = status_data.get("name", "No status") if status_data else "No status"

    # End Date
    end_data = props.get("End Date", {}).get("date")
    end_str = end_data.get("start") if end_data else None

    # Project Folder (URL)
    folder = props.get("Project Folder", {}).get("url", "")

    # Related tasks count
    tasks_rel = props.get("Related to Tasks Database", {}).get("relation", [])
    task_count = len(tasks_rel)

    # Related notes count
    notes_rel = props.get("Related to Notes Database", {}).get("relation", [])
    notes_count = len(notes_rel)

    # Page URL
    url = page.get("url", "")

    # Created / Last edited
    created = page.get("created_time", "")[:10]
    last_edited = page.get("last_edited_time", "")[:10]

    return {
        "title": title,
        "status": status,
        "end_date": end_str,
        "folder": folder,
        "task_count": task_count,
        "notes_count": notes_count,
        "url": url,
        "created": created,
        "last_edited": last_edited,
    }


def read_notion_projects(
    view: str = "summary",
    filter_status: str = "all",
) -> str:
    """Read and summarize projects from Notion Projects Database.

    Args:
        view: Output format — 'summary' (default overview), 'detailed' (full info).
        filter_status: Filter — 'all', 'wip', 'not_started', 'completed', 'on_hold', 'archived'.

    Returns:
        Formatted markdown summary of projects.
    """
    headers = _get_headers()
    if not headers:
        return "ERROR: NOTION_API_KEY not set in .env file."

    db_id = os.getenv("NOTION_PROJECTS_DB_ID")
    if not db_id:
        return "ERROR: NOTION_PROJECTS_DB_ID not set in .env file."

    valid_views = {"summary", "detailed"}
    if view not in valid_views:
        return f"ERROR: Invalid view '{view}'. Valid: {sorted(valid_views)}"

    status_map = {
        "all": None,
        "wip": "WIP",
        "not_started": "Not Started",
        "completed": "Completed",
        "on_hold": "On Hold",
        "archived": "Archived",
    }
    if filter_status not in status_map:
        return f"ERROR: Invalid filter_status '{filter_status}'. Valid: {sorted(status_map.keys())}"

    # Build query
    payload = {"page_size": 100}

    # Apply Notion-level filter for status
    notion_status = status_map[filter_status]
    if notion_status:
        payload["filter"] = {
            "property": "Status",
            "select": {"equals": notion_status},
        }

    # Fetch projects
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
        return "No projects found in the database."

    # Parse all projects
    projects = [_parse_project(page) for page in results]
    today = date.today()

    # Categorize by status
    by_status = {}
    for p in projects:
        by_status.setdefault(p["status"], []).append(p)

    # Identify overdue projects (WIP with past end date)
    overdue_projects = []
    for p in projects:
        if p["status"] == "WIP" and p["end_date"]:
            try:
                end = date.fromisoformat(p["end_date"])
                if end < today:
                    p["days_overdue"] = (today - end).days
                    overdue_projects.append(p)
            except (ValueError, TypeError):
                pass
    overdue_projects.sort(key=lambda p: p.get("days_overdue", 0), reverse=True)

    # Build output
    lines = []
    lines.append("# [CC] Projects Database Summary")
    lines.append(f"**Date**: {today.isoformat()}")
    lines.append("")

    # Stats
    lines.append("## Overview")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Projects | {len(projects)} |")
    for status_name in ["WIP", "Not Started", "Completed", "On Hold", "Archived"]:
        count = len(by_status.get(status_name, []))
        if count > 0:
            lines.append(f"| {status_name} | {count} |")
    if overdue_projects:
        lines.append(f"| Overdue (past end date) | {len(overdue_projects)} |")
    total_tasks = sum(p["task_count"] for p in projects)
    total_notes = sum(p["notes_count"] for p in projects)
    lines.append(f"| Total Linked Tasks | {total_tasks} |")
    lines.append(f"| Total Linked Notes | {total_notes} |")
    lines.append("")

    if view == "detailed":
        # Full details per project
        for status_name in ["WIP", "Not Started", "On Hold", "Completed", "Archived"]:
            group = by_status.get(status_name, [])
            if not group:
                continue
            lines.append(f"## {status_name} ({len(group)})")
            lines.append("")
            for p in group:
                overdue_label = ""
                if p.get("days_overdue", 0) > 0:
                    overdue_label = f" — **OVERDUE {p['days_overdue']}d**"
                lines.append(f"### {p['title']}{overdue_label}")
                lines.append(f"- **Status**: {p['status']}")
                lines.append(f"- **End Date**: {p['end_date'] or 'Not set'}")
                lines.append(f"- **Tasks**: {p['task_count']} | **Notes**: {p['notes_count']}")
                lines.append(f"- **Last Edited**: {p['last_edited']}")
                if p["folder"]:
                    lines.append(f"- **Folder**: {p['folder']}")
                lines.append("")

    else:
        # Summary view
        if overdue_projects:
            lines.append("## OVERDUE Projects")
            lines.append("")
            lines.append("| Project | End Date | Overdue | Tasks | Notes |")
            lines.append("|---------|----------|---------|-------|-------|")
            for p in overdue_projects:
                lines.append(
                    f"| {p['title']} | {p['end_date']} | "
                    f"{p['days_overdue']}d | {p['task_count']} | {p['notes_count']} |"
                )
            lines.append("")

        # Active projects table
        active = by_status.get("WIP", [])
        if active:
            lines.append(f"## Active Projects ({len(active)})")
            lines.append("")
            lines.append("| # | Project | End Date | Tasks | Notes |")
            lines.append("|---|---------|----------|-------|-------|")
            for i, p in enumerate(active, 1):
                end = p["end_date"] or "No date"
                lines.append(
                    f"| {i} | {p['title']} | {end} | "
                    f"{p['task_count']} | {p['notes_count']} |"
                )
            lines.append("")

        # Not started
        not_started = by_status.get("Not Started", [])
        if not_started:
            lines.append(f"## Not Started ({len(not_started)})")
            lines.append("")
            for p in not_started:
                lines.append(f"- {p['title']} (Tasks: {p['task_count']})")
            lines.append("")

    return "\n".join(lines)
