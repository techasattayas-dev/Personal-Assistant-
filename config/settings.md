# System Settings Documentation

**Last Updated**: 2026-03-11

## Overview

This document provides a human-readable overview of the Personal Assistant system configuration. For detailed settings, see the configuration files in this directory.

## Active Configurations

### Organization Method
- **Framework**: PARA Method (Projects, Areas, Resources, Archive)
- **Active Project Limit**: 5 projects maximum
- **Archive Threshold**: 90 days after completion
- **Inbox Processing**: Daily

### Data Format
- **Primary Format**: Markdown with YAML frontmatter
- **Backup Frequency**: Daily
- **Version Control**: Git (recommended)

## Integration Status

### Gmail
- **Status**: Enabled
- **Sync Frequency**: Every 15 minutes
- **Monitored Labels**: assistant, tasks, important
- **Auto-capture**: Enabled to Inbox/quick-capture.md

### Google Calendar
- **Status**: Enabled
- **Sync Frequency**: Every 15 minutes
- **Synced Calendars**: primary, tasks
- **Auto-generate Daily Logs**: Enabled

### Notion
- **Status**: Enabled
- **Sync Frequency**: Hourly
- **Bidirectional Sync**: Enabled
- **Synced Databases**: tasks, projects, knowledge-base

## Review Schedule

### Daily Review
- **Time**: 8:00 PM
- **Tasks**:
  - Process inbox items
  - Review today's tasks
  - Plan tomorrow's priorities
  - Update daily log

### Weekly Review
- **Day**: Sunday
- **Time**: 7:00 PM
- **Tasks**:
  - Review all active projects
  - Process inbox completely
  - Archive completed items
  - Update Areas
  - Plan next week

### Monthly Review
- **Day**: 1st of each month
- **Time**: 10:00 AM
- **Tasks**:
  - Financial review (budget vs. actual)
  - Evaluate progress on Areas
  - Clean up Resources
  - Review and update goals
  - System maintenance

## Financial Tracking

### Default Settings
- **Currency**: USD
- **Budget Period**: Monthly (starts on 1st)
- **Export Format**: CSV

### Tracking Categories
- Groceries
- Utilities
- Healthcare
- Transportation
- Entertainment
- Dining
- Shopping
- Education
- Investments
- Income

## Knowledge Base

### Method
- **Framework**: Zettelkasten
- **Auto-linking**: Enabled
- **Fleeting Note Retention**: 7 days
- **Tags**: Required for all permanent notes
- **Index File**: Resources/Knowledge-Base/index.md

### Note Types
1. **Fleeting Notes**: Quick captures, temporary (7-day retention)
2. **Literature Notes**: Summaries from external sources
3. **Permanent Notes**: Atomic, well-developed concepts

## Storage & Backup

### Local Storage
- **Location**: /Users/wuud/Desktop/Claude_Personal Assistance
- **Structure**: PARA method folders

### Backup Strategy
- **Frequency**: Daily
- **Method**: Git version control (recommended)
- **Cloud Backup**: Configure external backup service
- **Retention**: Keep all history

## Template Settings

### Available Templates
- Task Template (task-template.md)
- Project Template (project-template.md)
- Meeting Template (meeting-template.md)
- Daily Log Template (daily-log-template.md)
- Financial Transaction Template (financial-template.md)

### Auto-generation
- **Daily Logs**: Generated at midnight (00:00)
- **Calendar Events**: Synced to daily logs
- **Tasks Due**: Highlighted in daily logs

## Capture System

### Default Capture Location
- **Quick Capture**: Inbox/quick-capture.md
- **Detailed Capture**: Inbox/inbox.md
- **Processing Queue**: Inbox/to-process.md

### Processing Workflow
1. Items captured to Inbox
2. Daily processing during review
3. Categorize into Projects/Areas/Resources
4. Archive when completed

## Customization

### Updating Settings

To update system settings:

1. **Configuration Files**: Edit YAML/JSON files in `/config` directory
2. **Integration Credentials**: Set environment variables or update credentials in `integrations.json`
3. **Review Schedule**: Modify `schedule` section in `config.yaml`
4. **Financial Categories**: Update `finance.tracking-categories` in `config.yaml`

### Environment Variables

Required environment variables for integrations:

```bash
# Gmail
export GMAIL_CLIENT_ID="your-client-id"
export GMAIL_CLIENT_SECRET="your-client-secret"

# Google Calendar
export GOOGLE_CALENDAR_CLIENT_ID="your-client-id"
export GOOGLE_CALENDAR_CLIENT_SECRET="your-client-secret"

# Notion
export NOTION_API_KEY="your-api-key"
export NOTION_WORKSPACE_ID="your-workspace-id"
export NOTION_KB_DATABASE_ID="your-kb-database-id"
export NOTION_TASKS_DATABASE_ID="your-tasks-database-id"
export NOTION_PROJECTS_DATABASE_ID="your-projects-database-id"
export NOTION_JOURNAL_DATABASE_ID="your-journal-database-id"
```

## Support

For questions or issues:
1. Check the main README.md in the root directory
2. Review integration-specific README files
3. Consult configuration file comments
4. Review sync logs in Integrations/{service}/sync-log.md

---

**Note**: This is a living document. Update it whenever you make significant changes to your system configuration.
