# Notion Integration

## Overview

Bidirectional sync between local markdown files and Notion databases for tasks, projects, and knowledge base.

## Features

- Two-way sync: Local ↔ Notion
- Task database sync
- Project database sync
- Knowledge base sync
- Daily journal sync
- Conflict resolution with manual review

## Setup Instructions

### 1. Create Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Name it "Personal Assistant"
4. Select your workspace
5. Copy the "Internal Integration Token"

### 2. Create Notion Databases

Create these databases in Notion:

**Tasks Database**:
- Properties: Name, Status, Priority, Due Date, Tags, Project
- Share with your integration

**Projects Database**:
- Properties: Name, Status, Start Date, End Date, Owner, Progress
- Share with your integration

**Knowledge Base**:
- Properties: Title, Type, Tags, Created, Source
- Share with your integration

**Journal Database**:
- Properties: Date, Day, Week, Tags
- Share with your integration

### 3. Get Database IDs

For each database:
1. Open database in Notion
2. Copy URL (looks like: `https://notion.so/workspace/DATABASE_ID?v=...`)
3. Extract DATABASE_ID from URL

### 4. Set Environment Variables

```bash
export NOTION_API_KEY="secret_xxxxxxxxxxxxx"
export NOTION_WORKSPACE_ID="your-workspace-id"
export NOTION_KB_DATABASE_ID="knowledge-base-db-id"
export NOTION_TASKS_DATABASE_ID="tasks-db-id"
export NOTION_PROJECTS_DATABASE_ID="projects-db-id"
export NOTION_JOURNAL_DATABASE_ID="journal-db-id"
```

### 5. Configure Sync Mapping

Edit `sync-mapping.json` to customize field mappings between local markdown and Notion properties.

### 6. First Sync

Run sync script:
```bash
./sync-notion.sh
```

Choose sync direction for first sync:
- notion-to-local: Import from Notion
- local-to-notion: Export to Notion
- bidirectional: Sync both ways

## Configuration

See `sync-mapping.json` for:
- Database ID mapping
- Field property mapping
- Sync direction per database
- Conflict resolution strategy

## Sync Strategy

**Bidirectional Sync**:
1. Compare local file timestamps with Notion last_edited_time
2. Newer version wins (or manual review)
3. Sync changes in both directions
4. Log conflicts for manual resolution

**Local → Notion**:
- YAML frontmatter → Notion properties
- Markdown content → Notion blocks
- Preserve Notion-specific features

**Notion → Local**:
- Notion properties → YAML frontmatter
- Notion blocks → Markdown content
- Export to markdown format

## Field Mapping

### Tasks
| Local (YAML) | Notion Property |
|--------------|-----------------|
| title | Name |
| status | Status |
| priority | Priority |
| due-date | Due Date |
| tags | Tags |
| project | Project |

### Projects
| Local (YAML) | Notion Property |
|--------------|-----------------|
| title | Name |
| status | Status |
| start-date | Start Date |
| end-date | End Date |
| owner | Owner |
| progress | Progress |

### Knowledge Base
| Local (YAML) | Notion Property |
|--------------|-----------------|
| title | Title |
| type | Type |
| tags | Tags |
| created | Created |
| source | Source |

## Conflict Resolution

When local and Notion versions conflict:

1. **Auto-resolve** (if timestamps clearly indicate newer):
   - Newer version wins
   - Log the resolution

2. **Manual review** (if ambiguous):
   - Log conflict in change-log.md
   - Pause sync for that item
   - User reviews and chooses version
   - Resume sync after resolution

## Usage

### Sync Tasks

Create tasks in either location:
- Local: Create markdown file with task template
- Notion: Create new task in database

Both will sync within the hour (or on-demand).

### Sync Projects

Update project status in either location and it syncs bidirectionally.

### Sync Knowledge Base

Write permanent notes in markdown, they sync to Notion for mobile access and vice versa.

## Sync Logs

- `sync-log.md` - All sync operations
- `change-log.md` - Conflict resolutions and manual reviews

## Troubleshooting

**Sync Failures**:
- Verify API key is valid
- Check database IDs are correct
- Ensure integration has access to databases
- Review sync-log.md for errors

**Field Mapping Issues**:
- Verify property names match exactly
- Check property types (text, select, date, etc.)
- Update sync-mapping.json if needed

**Conflicts**:
- Review change-log.md
- Choose preferred version
- Update conflict resolution strategy if needed

---

**Status**: Awaiting credentials
**Last Sync**: Never
**Databases Connected**: 0
