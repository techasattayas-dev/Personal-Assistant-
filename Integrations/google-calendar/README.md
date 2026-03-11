# Google Calendar Integration

## Overview

Automatically sync calendar events to daily log files for integrated schedule and task management.

## Features

- Sync calendar events to Schedule/daily/*.md files
- Auto-generate daily logs with calendar events
- Two-way sync (local changes → calendar)
- Recurring event handling
- Multi-calendar support

## Setup Instructions

### 1. Create Google Cloud Project

Can use the same project as Gmail:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Calendar API
3. Use existing OAuth credentials or create new ones

### 2. Configure OAuth Consent Screen

Add Calendar scopes:
- `https://www.googleapis.com/auth/calendar.readonly`
- `https://www.googleapis.com/auth/calendar.events`

### 3. Set Environment Variables

```bash
export GOOGLE_CALENDAR_CLIENT_ID="your-client-id"
export GOOGLE_CALENDAR_CLIENT_SECRET="your-client-secret"
```

Can use same credentials as Gmail if preferred.

### 4. Configure Sync Settings

Edit `sync-config.json` to customize:
- Calendars to sync
- Event mapping rules
- Sync direction
- Recurring event handling

### 5. First-Time Authorization

Run the sync script:
```bash
./sync-calendar.sh
```

## Configuration

See `sync-config.json` for:
- Calendar list
- Event-to-file mapping
- Sync frequency
- Event filters

## Sync Strategy

**Calendar → Local**:
- Events → Schedule/daily/[DATE].md
- All-day events → "Today's Focus" section
- Timed events → "Calendar Events" section
- Recurring events → Generated for each occurrence

**Local → Calendar** (optional):
- Create events from daily log
- Update event details
- Mark as complete

## Event Format in Daily Logs

```markdown
## Calendar Events

- 09:00 - Meeting with Team
- 14:00 - Client Call
- 16:00 - Project Review
```

All-day events appear in "Today's Focus" section.

## Usage

### Auto-Sync Events

Calendar events automatically appear in your daily log files. Check Schedule/daily/[today].md to see today's events.

### Create Events from Daily Log

(Optional bidirectional sync):
Add events to your daily log and they'll sync to Google Calendar:

```markdown
## Calendar Events
- 15:00 - New Meeting (will sync to calendar)
```

## Sync Log

All operations logged in `sync-log.md`:
- Synced calendars
- Events imported
- Conflicts resolved
- Errors encountered

## Troubleshooting

**No Events Syncing**:
- Check calendar names in config
- Verify OAuth authorization
- Review sync-log.md

**Duplicate Events**:
- Check incremental sync setting
- Review conflict resolution strategy
- May need to clear sync state

**Missing Events**:
- Verify sync-future-days setting
- Check event visibility in calendar
- Ensure not declined/cancelled

---

**Status**: Awaiting credentials
**Last Sync**: Never
**Calendars**: 0 connected
