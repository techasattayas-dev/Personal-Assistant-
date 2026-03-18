"""
Tool: read_notion_command_center — Read the Command Center dashboard from Notion.

The Command Center is the top-level Notion dashboard page that aggregates:
- Today's checklist (daily routine items)
- Quick Actions & Key Views (links to filtered DB views)
- Tasks overview (linked view of Tasks DB)
- Projects overview (linked view of Projects DB)
- Areas overview (linked view of Areas DB)
- Notes overview (linked view of Notes DB)

Since the Command Center is a PAGE (not a database), this tool reads its
block structure and pulls live data from the connected databases to build
a unified dashboard view.

Requires NOTION_API_KEY and NOTION_COMMAND_CENTER_ID in .env.
Also reads from NOTION_TASKS_DB_ID, NOTION_PROJECTS_DB_ID, NOTION_AREAS_DB_ID.
"""

import os
from datetime import date

import requests


NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _get_headers() -> dict | None:
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        return None
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _fetch_today_checklist(headers: dict, page_id: str) -> list[dict]:
    """Extract to_do blocks from the 'Today' column of the Command Center."""
    todos = []
    # Get top-level children
    resp = requests.get(
        f"{NOTION_API_URL}/blocks/{page_id}/children?page_size=100",
        headers=headers, timeout=15,
    )
    if resp.status_code != 200:
        return todos

    blocks = resp.json().get("results", [])

    # Find column_lists and dig into them for to_do blocks
    for block in blocks:
        if block["type"] == "column_list" and block.get("has_children"):
            cl_resp = requests.get(
                f"{NOTION_API_URL}/blocks/{block['id']}/children?page_size=50",
                headers=headers, timeout=15,
            )
            if cl_resp.status_code != 200:
                continue
            for col in cl_resp.json().get("results", []):
                if col.get("has_children"):
                    inner_resp = requests.get(
                        f"{NOTION_API_URL}/blocks/{col['id']}/children?page_size=50",
                        headers=headers, timeout=15,
                    )
                    if inner_resp.status_code != 200:
                        continue
                    for inner in inner_resp.json().get("results", []):
                        if inner["type"] == "to_do":
                            td = inner.get("to_do", {})
                            text = "".join(
                                rt.get("plain_text", "")
                                for rt in td.get("rich_text", [])
                            )
                            if text.strip():
                                todos.append({
                                    "text": text.strip(),
                                    "checked": td.get("checked", False),
                                    "id": inner["id"],
                                })
    return todos


def _fetch_tasks_summary(headers: dict) -> dict:
    """Quick summary of tasks from Tasks DB."""
    db_id = os.getenv("NOTION_TASKS_DB_ID")
    if not db_id:
        return {"error": "NOTION_TASKS_DB_ID not set"}

    today = date.today()
    stats = {"total": 0, "open": 0, "done": 0, "overdue": 0, "due_today": 0}
    overdue_items = []

    payload = {"page_size": 100}
    resp = requests.post(
        f"{NOTION_API_URL}/databases/{db_id}/query",
        headers=headers, json=payload, timeout=30,
    )
    if resp.status_code != 200:
        return {"error": f"API {resp.status_code}"}

    data = resp.json()
    results = data.get("results", [])

    # Handle pagination
    while data.get("has_more"):
        payload["start_cursor"] = data["next_cursor"]
        r = requests.post(
            f"{NOTION_API_URL}/databases/{db_id}/query",
            headers=headers, json=payload, timeout=30,
        )
        if r.status_code == 200:
            data = r.json()
            results.extend(data.get("results", []))
        else:
            break

    for page in results:
        props = page.get("properties", {})
        done = props.get("Done", {}).get("checkbox", False)
        due_data = props.get("Due Date", {}).get("date")
        due_str = due_data.get("start") if due_data else None

        title_arr = props.get("Task", {}).get("title", [])
        title = title_arr[0]["plain_text"] if title_arr else "Untitled"

        stats["total"] += 1
        if done:
            stats["done"] += 1
        else:
            stats["open"] += 1
            if due_str:
                try:
                    due_date = date.fromisoformat(due_str)
                    if due_date < today:
                        stats["overdue"] += 1
                        days = (today - due_date).days
                        overdue_items.append({"title": title, "due": due_str, "days": days})
                    elif due_date == today:
                        stats["due_today"] += 1
                except (ValueError, TypeError):
                    pass

    overdue_items.sort(key=lambda x: x["days"], reverse=True)
    stats["overdue_items"] = overdue_items[:5]  # Top 5
    return stats


def _fetch_projects_summary(headers: dict) -> dict:
    """Quick summary of projects from Projects DB."""
    db_id = os.getenv("NOTION_PROJECTS_DB_ID")
    if not db_id:
        return {"error": "NOTION_PROJECTS_DB_ID not set"}

    today = date.today()
    stats = {"total": 0, "by_status": {}, "overdue": []}

    payload = {"page_size": 100}
    resp = requests.post(
        f"{NOTION_API_URL}/databases/{db_id}/query",
        headers=headers, json=payload, timeout=30,
    )
    if resp.status_code != 200:
        return {"error": f"API {resp.status_code}"}

    for page in resp.json().get("results", []):
        props = page.get("properties", {})
        title_arr = props.get("Project", {}).get("title", [])
        title = title_arr[0]["plain_text"] if title_arr else "Untitled"

        status_data = props.get("Status", {}).get("select")
        status = status_data.get("name", "No status") if status_data else "No status"

        end_data = props.get("End Date", {}).get("date")
        end_str = end_data.get("start") if end_data else None

        stats["total"] += 1
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        if status == "WIP" and end_str:
            try:
                if date.fromisoformat(end_str) < today:
                    stats["overdue"].append({"title": title, "end": end_str})
            except (ValueError, TypeError):
                pass

    return stats


def _fetch_areas_summary(headers: dict) -> dict:
    """Quick summary of areas from Areas DB."""
    db_id = os.getenv("NOTION_AREAS_DB_ID")
    if not db_id:
        return {"error": "NOTION_AREAS_DB_ID not set"}

    stats = {"total": 0, "by_pillar": {}}

    payload = {
        "page_size": 100,
        "filter": {"property": "Archived?", "checkbox": {"equals": False}},
    }
    resp = requests.post(
        f"{NOTION_API_URL}/databases/{db_id}/query",
        headers=headers, json=payload, timeout=30,
    )
    if resp.status_code != 200:
        return {"error": f"API {resp.status_code}"}

    for page in resp.json().get("results", []):
        props = page.get("properties", {})
        pillar_data = props.get("Area Pillar", {}).get("select")
        pillar = pillar_data.get("name", "Other") if pillar_data else "Other"

        stats["total"] += 1
        stats["by_pillar"][pillar] = stats["by_pillar"].get(pillar, 0) + 1

    return stats


def read_notion_command_center(
    view: str = "dashboard",
) -> str:
    """Read the Notion Command Center and return a unified dashboard.

    Args:
        view: Output format — 'dashboard' (full overview, default),
              'today' (today's checklist only),
              'status' (quick stats only).

    Returns:
        Formatted markdown dashboard.
    """
    headers = _get_headers()
    if not headers:
        return "ERROR: NOTION_API_KEY not set in .env file."

    page_id = os.getenv("NOTION_COMMAND_CENTER_ID")
    if not page_id:
        return "ERROR: NOTION_COMMAND_CENTER_ID not set in .env file."

    valid_views = {"dashboard", "today", "status"}
    if view not in valid_views:
        return f"ERROR: Invalid view '{view}'. Valid: {sorted(valid_views)}"

    today = date.today()
    lines = []
    lines.append("# Command Center")
    lines.append(f"**Date**: {today.isoformat()} ({today.strftime('%A')})")
    lines.append(f"**Source**: [Notion Command Center](https://www.notion.so/Command-Center-{page_id.replace('-', '')})")
    lines.append("")

    # --- Today's Checklist ---
    if view in ("dashboard", "today"):
        checklist = _fetch_today_checklist(headers, page_id)
        if checklist:
            done_count = sum(1 for t in checklist if t["checked"])
            lines.append(f"## Today's Routine ({done_count}/{len(checklist)} done)")
            lines.append("")
            for item in checklist:
                mark = "x" if item["checked"] else " "
                lines.append(f"- [{mark}] {item['text']}")
            lines.append("")
        else:
            lines.append("## Today's Routine")
            lines.append("No checklist items found.")
            lines.append("")

    if view == "today":
        return "\n".join(lines)

    # --- Tasks Summary ---
    if view in ("dashboard", "status"):
        tasks = _fetch_tasks_summary(headers)
        if "error" not in tasks:
            lines.append("## Tasks")
            lines.append("")
            lines.append(f"| Open | Done | Overdue | Due Today | Total |")
            lines.append(f"|------|------|---------|-----------|-------|")
            lines.append(
                f"| {tasks['open']} | {tasks['done']} | "
                f"{tasks['overdue']} | {tasks['due_today']} | {tasks['total']} |"
            )
            lines.append("")

            overdue_items = tasks.get("overdue_items", [])
            if overdue_items:
                lines.append("**Overdue:**")
                for item in overdue_items:
                    lines.append(f"- {item['title']} (due {item['due']}, {item['days']}d late)")
                lines.append("")
        else:
            lines.append(f"## Tasks\n\n_{tasks['error']}_\n")

    # --- Projects Summary ---
    if view in ("dashboard", "status"):
        projects = _fetch_projects_summary(headers)
        if "error" not in projects:
            lines.append("## Projects")
            lines.append("")
            status_parts = []
            for s in ["WIP", "Not Started", "Completed", "On Hold", "Archived"]:
                count = projects["by_status"].get(s, 0)
                if count > 0:
                    status_parts.append(f"**{s}**: {count}")
            lines.append(f"Total: {projects['total']} — " + " | ".join(status_parts))
            lines.append("")

            if projects["overdue"]:
                lines.append("**Overdue Projects:**")
                for p in projects["overdue"]:
                    lines.append(f"- {p['title']} (end date: {p['end']})")
                lines.append("")
        else:
            lines.append(f"## Projects\n\n_{projects['error']}_\n")

    # --- Areas Summary ---
    if view == "dashboard":
        areas = _fetch_areas_summary(headers)
        if "error" not in areas:
            lines.append("## Areas")
            lines.append("")
            pillar_parts = []
            for p in ["Workplace", "Business", "Personal"]:
                count = areas["by_pillar"].get(p, 0)
                if count > 0:
                    pillar_parts.append(f"**{p}**: {count}")
            lines.append(f"Total: {areas['total']} — " + " | ".join(pillar_parts))
            lines.append("")

    # --- Key Views ---
    if view == "dashboard":
        lines.append("## Key Views")
        lines.append("")
        lines.append("- [CC] Mobile Task")
        lines.append("- [CC] Projects")
        lines.append("- [CC] Area")
        lines.append("- [CC] Completed Tasks")
        lines.append("- [CC] Backend for Students")
        lines.append("")

    return "\n".join(lines)
