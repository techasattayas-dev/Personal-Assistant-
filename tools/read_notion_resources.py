"""
Tool: read_notion_resources — Read and summarize resources from Notion Resources Database.

Queries the [CC] Resources Database in Notion and returns a structured summary
with tags (SOP, Reference, Records, Archived) and linked areas/projects/notes counts.

Requires NOTION_API_KEY and NOTION_RESOURCES_DB_ID in .env.
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


def _parse_resource(page: dict) -> dict:
    """Extract resource fields from a Notion page object."""
    props = page.get("properties", {})

    title_arr = props.get("Resource", {}).get("title", [])
    title = title_arr[0]["plain_text"] if title_arr else "Untitled"

    tags_data = props.get("Tags", {}).get("multi_select", [])
    tags = [t["name"] for t in tags_data]

    areas_rel = props.get("Related to Areas Database", {}).get("relation", [])
    projects_rel = props.get("Related to Projects Database", {}).get("relation", [])
    notes_rel = props.get("Related to Notes Database", {}).get("relation", [])

    last_edited = page.get("last_edited_time", "")[:10]

    return {
        "title": title,
        "tags": tags,
        "area_count": len(areas_rel),
        "project_count": len(projects_rel),
        "notes_count": len(notes_rel),
        "last_edited": last_edited,
        "url": page.get("url", ""),
    }


def read_notion_resources(
    view: str = "summary",
    filter_tag: str = "all",
) -> str:
    """Read and summarize resources from Notion Resources Database.

    Args:
        view: Output format — 'summary' (default overview) or 'detailed' (full info).
        filter_tag: Filter by tag — 'all', 'sop', 'reference', 'records', or 'archived'.

    Returns:
        Formatted markdown summary of resources.
    """
    headers = _get_headers()
    if not headers:
        return "ERROR: NOTION_API_KEY not set in .env file."

    db_id = os.getenv("NOTION_RESOURCES_DB_ID")
    if not db_id:
        return "ERROR: NOTION_RESOURCES_DB_ID not set in .env file."

    valid_views = {"summary", "detailed"}
    if view not in valid_views:
        return f"ERROR: Invalid view '{view}'. Valid: {sorted(valid_views)}"

    tag_map = {
        "all": None,
        "sop": "SOP",
        "reference": "Reference",
        "records": "Records",
        "archived": "Archived",
    }
    if filter_tag not in tag_map:
        return f"ERROR: Invalid filter_tag '{filter_tag}'. Valid: {sorted(tag_map.keys())}"

    # Build query
    payload = {"page_size": 100}

    notion_tag = tag_map[filter_tag]
    if notion_tag:
        payload["filter"] = {
            "property": "Tags",
            "multi_select": {"contains": notion_tag},
        }

    # Fetch resources
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
        return "No resources found in the database."

    resources = [_parse_resource(page) for page in results]

    # Group by tag
    by_tag = {}
    for r in resources:
        if r["tags"]:
            for tag in r["tags"]:
                by_tag.setdefault(tag, []).append(r)
        else:
            by_tag.setdefault("Untagged", []).append(r)

    # Build output
    lines = []
    lines.append("# [CC] Resources Database Summary")
    lines.append("")

    # Stats
    lines.append("## Overview")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Resources | {len(resources)} |")
    for tag_name in ["SOP", "Reference", "Records", "Archived", "Untagged"]:
        count = len(by_tag.get(tag_name, []))
        if count > 0:
            lines.append(f"| {tag_name} | {count} |")
    total_notes = sum(r["notes_count"] for r in resources)
    lines.append(f"| Total Linked Notes | {total_notes} |")
    lines.append("")

    if view == "detailed":
        for tag_name in ["SOP", "Reference", "Records", "Archived", "Untagged"]:
            group = by_tag.get(tag_name, [])
            if not group:
                continue
            lines.append(f"## {tag_name} ({len(group)})")
            lines.append("")
            for r in group:
                lines.append(f"### {r['title']}")
                lines.append(f"- **Tags**: {', '.join(r['tags']) or 'None'}")
                lines.append(f"- **Areas**: {r['area_count']} | **Projects**: {r['project_count']} | **Notes**: {r['notes_count']}")
                lines.append(f"- **Last Edited**: {r['last_edited']}")
                lines.append("")
    else:
        # Summary table
        lines.append("## All Resources")
        lines.append("")
        lines.append("| # | Resource | Tags | Areas | Projects | Notes | Last Edited |")
        lines.append("|---|----------|------|-------|----------|-------|-------------|")
        for i, r in enumerate(resources, 1):
            tags_str = ", ".join(r["tags"]) or "—"
            lines.append(
                f"| {i} | {r['title']} | {tags_str} | "
                f"{r['area_count']} | {r['project_count']} | {r['notes_count']} | {r['last_edited']} |"
            )
        lines.append("")

    return "\n".join(lines)
