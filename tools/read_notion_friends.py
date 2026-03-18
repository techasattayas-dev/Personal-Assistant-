"""
Tool: read_notion_friends — Read and summarize contacts from Notion Friends Database.

Queries the [CC] Friends Database in Notion and returns a structured summary
grouped by relationship type, city, or communication channel.

Requires NOTION_API_KEY and NOTION_FRIENDS_DB_ID in .env.
"""

import os
from collections import Counter

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


def _parse_friend(page: dict) -> dict:
    """Extract friend fields from a Notion page object."""
    props = page.get("properties", {})

    title_arr = props.get("Name", {}).get("title", [])
    name = title_arr[0]["plain_text"] if title_arr else "Unnamed"

    rel_data = props.get("Relationship", {}).get("select")
    relationship = rel_data.get("name", "Uncategorized") if rel_data else "Uncategorized"

    city_data = props.get("City", {}).get("multi_select", [])
    cities = [c["name"] for c in city_data]

    channel_data = props.get("Comms Channel", {}).get("multi_select", [])
    channels = [c["name"] for c in channel_data]

    contact_arr = props.get("Contact info", {}).get("rich_text", [])
    contact_info = contact_arr[0]["plain_text"] if contact_arr else ""

    archived = props.get("Archived", {}).get("checkbox", False)

    last_edited = page.get("last_edited_time", "")[:10]

    return {
        "name": name,
        "relationship": relationship,
        "cities": cities,
        "channels": channels,
        "contact_info": contact_info,
        "archived": archived,
        "last_edited": last_edited,
    }


def read_notion_friends(
    view: str = "summary",
    filter_relationship: str = "all",
    include_archived: bool = False,
) -> str:
    """Read and summarize contacts from Notion Friends Database.

    Args:
        view: Output format — 'summary' (default overview) or 'detailed' (full contact info).
        filter_relationship: Filter — 'all', 'friend', 'business', 'google', 'ey',
                             'creator', 'high_school'.
        include_archived: Whether to include archived contacts (default: False).

    Returns:
        Formatted markdown summary of contacts.
    """
    headers = _get_headers()
    if not headers:
        return "ERROR: NOTION_API_KEY not set in .env file."

    db_id = os.getenv("NOTION_FRIENDS_DB_ID")
    if not db_id:
        return "ERROR: NOTION_FRIENDS_DB_ID not set in .env file."

    valid_views = {"summary", "detailed"}
    if view not in valid_views:
        return f"ERROR: Invalid view '{view}'. Valid: {sorted(valid_views)}"

    rel_map = {
        "all": None,
        "friend": "Friend",
        "business": "Business",
        "google": "Google",
        "ey": "EY",
        "creator": "Creator",
        "high_school": "High School",
    }
    if filter_relationship not in rel_map:
        return f"ERROR: Invalid filter_relationship '{filter_relationship}'. Valid: {sorted(rel_map.keys())}"

    # Build query
    payload = {"page_size": 100}

    filters = []
    notion_rel = rel_map[filter_relationship]
    if notion_rel:
        filters.append({
            "property": "Relationship",
            "select": {"equals": notion_rel},
        })
    if not include_archived:
        filters.append({
            "property": "Archived",
            "checkbox": {"equals": False},
        })

    if len(filters) == 1:
        payload["filter"] = filters[0]
    elif len(filters) > 1:
        payload["filter"] = {"and": filters}

    # Fetch
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
        return "No contacts found in the database."

    friends = [_parse_friend(page) for page in results]

    # Group by relationship
    by_rel = {}
    for f in friends:
        by_rel.setdefault(f["relationship"], []).append(f)

    # City and channel stats
    city_counter = Counter()
    channel_counter = Counter()
    for f in friends:
        for c in f["cities"]:
            city_counter[c] += 1
        for ch in f["channels"]:
            channel_counter[ch] += 1

    # Build output
    lines = []
    lines.append("# [CC] Friends Database Summary")
    lines.append("")

    # Stats
    lines.append("## Overview")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Contacts | {len(friends)} |")
    for rel_name in ["Friend", "Business", "Google", "EY", "Creator", "High School", "Uncategorized"]:
        count = len(by_rel.get(rel_name, []))
        if count > 0:
            lines.append(f"| {rel_name} | {count} |")
    lines.append("")

    if city_counter:
        lines.append("**Top Cities**: " + ", ".join(f"{c} ({n})" for c, n in city_counter.most_common(5)))
        lines.append("")

    if channel_counter:
        lines.append("**Channels**: " + ", ".join(f"{ch} ({n})" for ch, n in channel_counter.most_common()))
        lines.append("")

    if view == "detailed":
        for rel_name in ["Friend", "Business", "Google", "EY", "Creator", "High School", "Uncategorized"]:
            group = by_rel.get(rel_name, [])
            if not group:
                continue
            lines.append(f"## {rel_name} ({len(group)})")
            lines.append("")
            for f in group:
                lines.append(f"### {f['name']}")
                lines.append(f"- **Relationship**: {f['relationship']}")
                if f["cities"]:
                    lines.append(f"- **City**: {', '.join(f['cities'])}")
                if f["channels"]:
                    lines.append(f"- **Channels**: {', '.join(f['channels'])}")
                if f["contact_info"]:
                    lines.append(f"- **Contact**: {f['contact_info']}")
                lines.append(f"- **Last Edited**: {f['last_edited']}")
                lines.append("")
    else:
        # Summary table
        lines.append("## Contacts")
        lines.append("")
        lines.append("| # | Name | Relationship | City | Channels |")
        lines.append("|---|------|-------------|------|----------|")
        for i, f in enumerate(friends, 1):
            cities_str = ", ".join(f["cities"]) or "—"
            channels_str = ", ".join(f["channels"]) or "—"
            lines.append(f"| {i} | {f['name']} | {f['relationship']} | {cities_str} | {channels_str} |")
        lines.append("")

    return "\n".join(lines)
