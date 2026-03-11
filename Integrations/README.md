# Integrations

## Overview

This directory contains configuration and sync logs for external service integrations.

## Active Integrations

### Gmail
**Status**: Configured (credentials needed)
**Sync Frequency**: Every 15 minutes
**Purpose**: Email-to-inbox capture, task extraction

[Setup Instructions](./gmail/README.md)

### Google Calendar
**Status**: Configured (credentials needed)
**Sync Frequency**: Every 15 minutes
**Purpose**: Calendar event sync to daily logs

[Setup Instructions](./google-calendar/README.md)

### Notion
**Status**: Configured (credentials needed)
**Sync Frequency**: Hourly
**Purpose**: Bidirectional sync of tasks, projects, and knowledge base

[Setup Instructions](./notion/README.md)

## Integration Strategy

**Philosophy**: Markdown files are the source of truth. External services sync to/from markdown.

**Sync Pattern**:
1. External service → Local markdown (import/sync)
2. Local markdown → External service (export/sync)
3. Conflict resolution: Manual review when needed

## Setting Up Integrations

### 1. Obtain API Credentials

Each service requires authentication:
- **Gmail**: OAuth 2.0 client credentials
- **Google Calendar**: OAuth 2.0 client credentials (can share with Gmail)
- **Notion**: Integration token and database IDs

### 2. Set Environment Variables

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Gmail
export GMAIL_CLIENT_ID="your-client-id"
export GMAIL_CLIENT_SECRET="your-client-secret"

# Google Calendar (can share Gmail credentials)
export GOOGLE_CALENDAR_CLIENT_ID="your-client-id"
export GOOGLE_CALENDAR_CLIENT_SECRET="your-client-secret"

# Notion
export NOTION_API_KEY="your-integration-token"
export NOTION_WORKSPACE_ID="your-workspace-id"
export NOTION_KB_DATABASE_ID="your-knowledge-base-db-id"
export NOTION_TASKS_DATABASE_ID="your-tasks-db-id"
export NOTION_PROJECTS_DATABASE_ID="your-projects-db-id"
export NOTION_JOURNAL_DATABASE_ID="your-journal-db-id"
```

### 3. Configure Sync Settings

Edit the configuration files:
- Main config: `../config/integrations.json`
- Service-specific: `{service}/sync-config.json`

### 4. Test Integration

Each service folder contains a README with testing instructions.

## Sync Logs

All sync operations are logged in:
- `{service}/sync-log.md` - Main sync history
- `{service}/change-log.md` - Conflict resolutions (Notion only)

## Troubleshooting

### Sync Not Working
1. Check credentials are set correctly
2. Review sync-log.md for error messages
3. Verify API quotas haven't been exceeded
4. Test API access manually

### Conflicts
When local and remote changes conflict:
1. Sync operation pauses
2. Conflict logged in change-log.md
3. Manual review required
4. Choose local or remote version
5. Resume sync

### Rate Limiting
If you hit API rate limits:
- Reduce sync frequency in config.yaml
- Batch operations when possible
- Review quota usage in service dashboard

## Security Notes

- **Never commit credentials** to version control
- Store credentials in environment variables only
- Use `.gitignore` to exclude sync logs with sensitive data
- Regularly rotate API keys
- Use OAuth when available (Gmail, Calendar)

## Future Integrations

Potential services to add:
- [ ] Todoist
- [ ] Trello
- [ ] Slack
- [ ] GitHub
- [ ] Google Drive
- [ ] Dropbox

---

**Last Updated**: 2026-03-11
**Active Integrations**: 0 (credentials needed)
**Next Review**: 2026-04-01
