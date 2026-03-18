---
title: "System Improvements Backlog"
status: planned
start-date: 2026-03-13
owner: Wut
tags: [system, improvement, backlog, WAT-framework]
progress: 0
created: 2026-03-13
---

# System Improvements Backlog

**Status**: Not Started — Checklist for future improvement sprints

---

## Critical

- [ ] Add pagination to 4 Notion read tools (projects, areas, resources, friends) — currently silently truncates at 100 entries
- [ ] Build `update_notion` tool — system can only CREATE, cannot modify existing tasks/projects/contacts (need PATCH `/pages/{page_id}`)
- [ ] Fix `config/.notion-credentials` security — contains live API key, not in `.gitignore`, could be committed
- [ ] Extract shared Notion utilities — `_get_headers()` + constants duplicated across 6 files, move to `tools/_notion_utils.py`

## High

- [ ] Build `search_notion` tool — cannot find entries by keyword/title across databases
- [ ] Add date validation on `push_to_notion` — `due_date`/`end_date` accept any string, malformed input fails silently at API
- [ ] Update `workflows/push_to_notion.md` — still references old single-DB behavior, needs update for 6-target multi-DB support
- [ ] Add API key redaction to `scrape_web.py` — other tools redact keys in errors, scraper doesn't
- [ ] Add Notion API rate limit handling (429 retry logic) — no retry on any Notion tool

## Medium

- [ ] Add date range filtering for tasks — can't query "tasks due this week" or by date range
- [ ] Add owner/assignee filtering for tasks
- [ ] Add consistent sorting across all Notion read tools
- [ ] Remove empty `Projects/Sample-Project/` folder or add content
- [ ] Build Notion re-sync mechanism — local `project.md` files are one-time snapshots, no drift detection
- [ ] Load actual KPI data into `Areas/Business-Units/*/data/` folders
- [ ] Add API key redaction to `scrape_web.py` error messages
- [ ] Set up automated backup/commit workflow or pre-push checks

## Low

- [ ] Add output format options to read tools (CSV/JSON export)
- [ ] Add caching between Notion API calls within same session
- [ ] Build Inbox processing tool — `Inbox/` folder exists but no automation
- [ ] Build Schedule automation — auto-generate daily/weekly log files
- [ ] Start populating Knowledge Base (Fleeting/Literature/Permanent Notes)
- [ ] Add unit tests for tools
- [ ] Build `delete_notion` tool for archiving/removing entries
- [ ] Gmail & Google Calendar integration (currently stub configs only)

---

**Created**: 2026-03-13
**Source**: Full system audit
