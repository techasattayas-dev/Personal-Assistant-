"""
Tool: read_notion_areas — Read and summarize areas from Notion Areas Database.

Queries the [CC] Areas Database in Notion and returns a structured summary
grouped by pillar (Personal, Business, Workplace) with linked projects/notes counts.

Requires NOTION_API_KEY and NOTION_AREAS_DB_ID in .env.
"""

import os

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


def _parse_area(page: dict) -> dict:
    """Extract area fields from a Notion page object."""
    props = page.get("properties", {})

    title_arr = props.get("Area", {}).get("title", [])
    title = title_arr[0]["plain_text"] if title_arr else "Untitled"

    pillar_data = props.get("Area Pillar", {}).get("select")
    pillar = pillar_data.get("name", "Uncategorized") if pillar_data else "Uncategorized"

    archived = props.get("Archived?", {}).get("checkbox", False)

    folder = props.get("Area Folder", {}).get("url", "")

    projects_rel = props.get("Related to Projects Database", {}).get("relation", [])
    notes_rel = props.get("Related to Notes Database", {}).get("relation", [])

    last_edited = page.get("last_edited_time", "")[:10]

    return {
        "title": title,
        "pillar": pillar,
        "archived": archived,
        "folder": folder,
        "project_count": len(projects_rel),
        "notes_count": len(notes_rel),
        "last_edited": last_edited,
        "url": page.get("url", ""),
    }


def read_notion_areas(
    view: str = "summary",
    filter_pillar: str = "all",
    include_archived: bool = False,
) -> str:
    """Read and summarize areas from Notion Areas Database.

    Args:
        view: Output format — 'summary' (default overview) or 'detailed' (full info).
        filter_pillar: Filter by pillar — 'all', 'personal', 'business', or 'workplace'.
        include_archived: Whether to include archived areas (default: False).

    Returns:
        Formatted markdown summary of areas.
    """
    headers = _get_headers()
    if not headers:
        return "ERROR: NOTION_API_KEY not set in .env file."

    db_id = os.getenv("NOTION_AREAS_DB_ID")
    if not db_id:
        return "ERROR: NOTION_AREAS_DB_ID not set in .env file."

    valid_views = {"summary", "detailed"}
    if view not in valid_views:
        return f"ERROR: Invalid view '{view}'. Valid: {sorted(valid_views)}"

    pillar_map = {
        "all": None,
        "personal": "Personal",
        "business": "Business",
        "workplace": "Workplace",
    }
    if filter_pillar not in pillar_map:
        return f"ERROR: Invalid filter_pillar '{filter_pillar}'. Valid: {sorted(pillar_map.keys())}"

    # Build query
    payload = {"page_size": 100}

    # Build filter conditions
    filters = []
    notion_pillar = pillar_map[filter_pillar]
    if notion_pillar:
        filters.append({
            "property": "Area Pillar",
            "select": {"equals": notion_pillar},
        })
    if not include_archived:
        filters.append({
            "property": "Archived?",
            "checkbox": {"equals": False},
        })

    if len(filters) == 1:
        payload["filter"] = filters[0]
    elif len(filters) > 1:
        payload["filter"] = {"and": filters}

    # Fetch areas
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
        return "No areas found in the database."

    areas = [_parse_area(page) for page in results]

    # Group by pillar
    by_pillar = {}
    for a in areas:
        by_pillar.setdefault(a["pillar"], []).append(a)

    # Build output
    lines = []
    lines.append("# [CC] Areas Database Summary")
    lines.append("")

    # Stats
    lines.append("## Overview")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Areas | {len(areas)} |")
    for pillar_name in ["Workplace", "Business", "Personal"]:
        count = len(by_pillar.get(pillar_name, []))
        if count > 0:
            lines.append(f"| {pillar_name} | {count} |")
    total_projects = sum(a["project_count"] for a in areas)
    total_notes = sum(a["notes_count"] for a in areas)
    lines.append(f"| Total Linked Projects | {total_projects} |")
    lines.append(f"| Total Linked Notes | {total_notes} |")
    lines.append("")

    if view == "detailed":
        for pillar_name in ["Workplace", "Business", "Personal", "Uncategorized"]:
            group = by_pillar.get(pillar_name, [])
            if not group:
                continue
            lines.append(f"## {pillar_name} ({len(group)})")
            lines.append("")
            for a in group:
                archived_label = " [Archived]" if a["archived"] else ""
                lines.append(f"### {a['title']}{archived_label}")
                lines.append(f"- **Pillar**: {a['pillar']}")
                lines.append(f"- **Projects**: {a['project_count']} | **Notes**: {a['notes_count']}")
                lines.append(f"- **Last Edited**: {a['last_edited']}")
                if a["folder"]:
                    lines.append(f"- **Folder**: {a['folder']}")
                lines.append("")
    else:
        # Summary view — table per pillar
        for pillar_name in ["Workplace", "Business", "Personal", "Uncategorized"]:
            group = by_pillar.get(pillar_name, [])
            if not group:
                continue
            lines.append(f"## {pillar_name} ({len(group)})")
            lines.append("")
            lines.append("| Area | Projects | Notes | Last Edited |")
            lines.append("|------|----------|-------|-------------|")
            for a in group:
                lines.append(
                    f"| {a['title']} | {a['project_count']} | "
                    f"{a['notes_count']} | {a['last_edited']} |"
                )
            lines.append("")

    return "\n".join(lines)
