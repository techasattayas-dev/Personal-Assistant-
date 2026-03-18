"""
Tool: push_to_notion — Create entries in any connected Notion database.

Supports all 5 PARA databases + generic Notes:
  - tasks: Create a task with title, due date, owner, recurring flag
  - projects: Create a project with title, status, end date, folder URL
  - areas: Create an area with title, pillar
  - resources: Create a resource with title, tags
  - friends: Create a contact with name, relationship, city, channel, contact info
  - notes: Create a page in the default Notes database (title + body content)

Requires NOTION_API_KEY and corresponding DB IDs in .env.
"""

import os
import re

import requests


NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Maps target name -> env var holding the database ID
_DB_ENV_KEYS = {
    "tasks": "NOTION_TASKS_DB_ID",
    "projects": "NOTION_PROJECTS_DB_ID",
    "areas": "NOTION_AREAS_DB_ID",
    "resources": "NOTION_RESOURCES_DB_ID",
    "friends": "NOTION_FRIENDS_DB_ID",
    "notes": "NOTION_DATABASE_ID",
}


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


def _markdown_to_notion_blocks(markdown: str) -> list[dict]:
    """Convert simple markdown to Notion block objects."""
    blocks = []
    lines = markdown.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Headings
        if line.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:].strip()}}]},
            })
        elif line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:].strip()}}]},
            })
        elif line.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]},
            })
        # Bullet list
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            content = re.sub(r"^[\s]*[-*]\s+", "", line)
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": content}}]},
            })
        # Code block
        elif line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": "\n".join(code_lines)}}],
                    "language": "plain text",
                },
            })
        # Divider
        elif line.strip() in ("---", "***", "___"):
            blocks.append({"object": "block", "type": "divider", "divider": {}})
        # Regular paragraph (skip empty lines)
        elif line.strip():
            content = line.strip()
            if len(content) > 2000:
                content = content[:2000]
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]},
            })

        i += 1

    return blocks


def _build_task_properties(title: str, due_date: str | None, recurring: bool) -> dict:
    """Build Notion properties for the Tasks database."""
    props = {
        "Task": {"title": [{"text": {"content": title}}]},
        "Done": {"checkbox": False},
    }
    if due_date:
        props["Due Date"] = {"date": {"start": due_date}}
    if recurring:
        props["Recurring?"] = {"checkbox": True}
    return props


def _build_project_properties(
    title: str, status: str | None, end_date: str | None, folder_url: str | None
) -> dict:
    """Build Notion properties for the Projects database."""
    props = {
        "Project": {"title": [{"text": {"content": title}}]},
    }
    if status:
        props["Status"] = {"select": {"name": status}}
    if end_date:
        props["End Date"] = {"date": {"start": end_date}}
    if folder_url:
        props["Project Folder"] = {"url": folder_url}
    return props


def _build_area_properties(title: str, pillar: str | None) -> dict:
    """Build Notion properties for the Areas database."""
    props = {
        "Area": {"title": [{"text": {"content": title}}]},
    }
    if pillar:
        props["Area Pillar"] = {"select": {"name": pillar}}
    return props


def _build_resource_properties(title: str, tags: list[str] | None) -> dict:
    """Build Notion properties for the Resources database."""
    props = {
        "Resource": {"title": [{"text": {"content": title}}]},
    }
    if tags:
        props["Tags"] = {"multi_select": [{"name": t} for t in tags]}
    return props


def _build_friend_properties(
    name: str,
    relationship: str | None,
    city: list[str] | None,
    comms_channel: list[str] | None,
    contact_info: str | None,
) -> dict:
    """Build Notion properties for the Friends database."""
    props = {
        "Name": {"title": [{"text": {"content": name}}]},
    }
    if relationship:
        props["Relationship"] = {"select": {"name": relationship}}
    if city:
        props["City"] = {"multi_select": [{"name": c} for c in city]}
    if comms_channel:
        props["Comms Channel"] = {"multi_select": [{"name": ch} for ch in comms_channel]}
    if contact_info:
        props["Contact info"] = {
            "rich_text": [{"type": "text", "text": {"content": contact_info}}]
        }
    return props


def _build_notes_properties(title: str) -> dict:
    """Build Notion properties for the Notes database (generic)."""
    return {
        "title": {"title": [{"text": {"content": title}}]},
    }


def push_to_notion(
    title: str,
    target: str = "notes",
    content: str | None = None,
    database_id: str | None = None,
    # Task-specific
    due_date: str | None = None,
    recurring: bool = False,
    # Project-specific
    status: str | None = None,
    end_date: str | None = None,
    folder_url: str | None = None,
    # Area-specific
    pillar: str | None = None,
    # Resource-specific
    tags: list[str] | None = None,
    # Friend-specific
    relationship: str | None = None,
    city: list[str] | None = None,
    comms_channel: list[str] | None = None,
    contact_info: str | None = None,
) -> str:
    """Create an entry in any connected Notion database.

    Args:
        title: Title/name of the entry (required for all targets).
        target: Which database to push to — 'tasks', 'projects', 'areas',
                'resources', 'friends', or 'notes' (default).
        content: Markdown body content (appended as page blocks). Optional.
        database_id: Override database ID. Uses .env default for the target if not provided.
        due_date: ISO date string for task due date (tasks only).
        recurring: Whether the task is recurring (tasks only).
        status: Project status — 'Not Started', 'WIP', 'Completed', 'On Hold', 'Archived' (projects only).
        end_date: ISO date string for project end date (projects only).
        folder_url: Google Drive or folder URL (projects only).
        pillar: Area pillar — 'Personal', 'Business', 'Workplace' (areas only).
        tags: List of tags — 'SOP', 'Reference', 'Records' (resources only).
        relationship: Relationship type — 'Friend', 'Business', 'Google', 'EY', 'Creator', 'High School' (friends only).
        city: List of city names (friends only).
        comms_channel: List of communication channels (friends only).
        contact_info: Contact information text (friends only).

    Returns:
        Success message with Notion page URL, or "ERROR: ..." on failure.
    """
    headers = _get_headers()
    if not headers:
        return "ERROR: NOTION_API_KEY not set in .env file."

    # Validate target
    valid_targets = set(_DB_ENV_KEYS.keys())
    if target not in valid_targets:
        return f"ERROR: Invalid target '{target}'. Valid: {sorted(valid_targets)}"

    # Resolve database ID
    db_id = database_id or os.getenv(_DB_ENV_KEYS[target])
    if not db_id:
        env_key = _DB_ENV_KEYS[target]
        return f"ERROR: No database_id provided and {env_key} not set in .env."

    # Build properties based on target
    if target == "tasks":
        properties = _build_task_properties(title, due_date, recurring)
    elif target == "projects":
        properties = _build_project_properties(title, status, end_date, folder_url)
    elif target == "areas":
        properties = _build_area_properties(title, pillar)
    elif target == "resources":
        properties = _build_resource_properties(title, tags)
    elif target == "friends":
        properties = _build_friend_properties(title, relationship, city, comms_channel, contact_info)
    else:
        # notes (default)
        properties = _build_notes_properties(title)

    # Build page payload
    payload = {
        "parent": {"database_id": db_id},
        "properties": properties,
    }

    # Add body content as blocks if provided
    if content:
        blocks = _markdown_to_notion_blocks(content)
        if len(blocks) > 100:
            blocks = blocks[:100]
        payload["children"] = blocks

    # Create page
    try:
        resp = requests.post(
            f"{NOTION_API_URL}/pages",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if resp.status_code == 200:
            page_url = resp.json().get("url", "unknown")
            target_label = target.capitalize()
            return f"{target_label} created in Notion: {page_url}"
        else:
            error = resp.json().get("message", resp.text[:300])
            return f"ERROR: Notion API returned {resp.status_code}: {error}"

    except requests.RequestException as e:
        return f"ERROR: Failed to connect to Notion API: {e}"
