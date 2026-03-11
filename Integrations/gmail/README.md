# Gmail Integration

## Overview

Automatically capture important emails to your inbox for processing and task extraction.

## Features

- Auto-capture emails with specific labels to Inbox/quick-capture.md
- Extract tasks from emails
- Sync email metadata (sender, subject, date)
- Filter spam and promotions

## Setup Instructions

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials

### 2. Configure OAuth Consent Screen

1. Set application type: Desktop app
2. Add scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.labels`
3. Add test users (your email)

### 3. Download Credentials

1. Download OAuth client JSON
2. Extract client_id and client_secret
3. Set environment variables:

```bash
export GMAIL_CLIENT_ID="your-client-id-here"
export GMAIL_CLIENT_SECRET="your-client-secret-here"
```

### 4. Configure Sync Settings

Edit `sync-config.json` to customize:
- Labels to monitor
- Capture location
- Sync frequency
- Filters

### 5. First-Time Authorization

Run the sync script (to be created):
```bash
./sync-gmail.sh
```

This will:
1. Open browser for OAuth authorization
2. Save refresh token locally
3. Begin syncing emails

## Configuration

See `sync-config.json` for:
- Label mapping (Gmail labels → local files)
- Auto-capture settings
- Filter rules
- Batch size and frequency

## Sync Strategy

**Gmail → Local**:
- Emails with "assistant" label → Inbox/inbox.md
- Emails with "tasks" label → Inbox/to-process.md
- Important emails → Flagged for review

**Sync Process**:
1. Check for new emails every 15 minutes
2. Filter out spam/promotions
3. Extract metadata and content
4. Append to appropriate inbox file
5. Log sync operation

## Usage

### Auto-Capture Emails

Label an email in Gmail with "assistant" and it will automatically appear in your Inbox/quick-capture.md file within 15 minutes.

### Task Extraction

Emails labeled "tasks" are parsed for action items:
- Subject line becomes task title
- Body scanned for checkboxes or action words
- Added to Inbox/to-process.md for review

## Sync Log

All sync operations logged in `sync-log.md`:
- Timestamp
- Emails synced
- Errors encountered
- Actions taken

## Troubleshooting

**Authorization Failed**:
- Check credentials in environment variables
- Verify OAuth consent screen is configured
- Ensure test user is added

**No Emails Syncing**:
- Verify labels exist in Gmail
- Check sync frequency in config
- Review sync-log.md for errors

**Rate Limiting**:
- Reduce sync frequency
- Decrease batch size
- Check quota in Google Cloud Console

---

**Status**: Awaiting credentials
**Last Sync**: Never
**Next Sync**: After configuration
