"""
Tool: push_to_notion — Push analysis results to a Notion page.

Creates a new page in the configured Notion database with title and markdown content.
Requires NOTION_API_KEY and NOTION_DATABASE_ID in .env.
"""

import os
import re

import requests


NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


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
            # Notion has a 2000 char limit per rich_text block
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


def push_to_notion(
    title: str,
    content: str,
    database_id: str | None = None,
) -> str:
    """Create a Notion page with the given title and markdown content."""
    api_key = os.getenv("NOTION_API_KEY")
    if not api_key:
        return "ERROR: NOTION_API_KEY not set in .env file."

    db_id = database_id or os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        return "ERROR: No database_id provided and NOTION_DATABASE_ID not set in .env."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }

    blocks = _markdown_to_notion_blocks(content)

    # Notion limits to 100 blocks per request
    if len(blocks) > 100:
        blocks = blocks[:100]

    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "title": {
                "title": [{"text": {"content": title}}],
            },
        },
        "children": blocks,
    }

    try:
        resp = requests.post(
            f"{NOTION_API_URL}/pages",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if resp.status_code == 200:
            page_url = resp.json().get("url", "unknown")
            return f"Notion page created successfully: {page_url}"
        else:
            error = resp.json().get("message", resp.text)
            return f"ERROR: Notion API returned {resp.status_code}: {error}"

    except requests.RequestException as e:
        return f"ERROR: Failed to connect to Notion API: {e}"
