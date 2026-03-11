# Push to Notion

## Objective
Deliver analysis results to a Notion database page for easy sharing and collaboration.

## Required Inputs
- `title`: Title for the Notion page
- `content`: Markdown content to publish (or reference to a saved report file)
- `database_id` (optional): Notion database ID. Falls back to NOTION_DATABASE_ID in .env.

## Tools Used
- `push_to_notion` — Create the Notion page

## Steps

### 1. Prepare Content
If the content references a local file (e.g., `.tmp/analysis_report.md`), read it first. Ensure the content is clean markdown.

### 2. Validate Configuration
Confirm that NOTION_API_KEY is set in the environment. If no database_id is provided, confirm that NOTION_DATABASE_ID is set.

### 3. Push to Notion
Call `push_to_notion` with the title and content. If the content exceeds Notion's limits, it will be truncated to 100 blocks.

### 4. Confirm Delivery
Report the Notion page URL back to the user.

## Expected Outputs
- A new Notion page with the analysis content

## Edge Cases
- **Missing API key**: Tell the user to set NOTION_API_KEY in .env.
- **Invalid database ID**: The Notion API will return a 404. Suggest the user verify the database ID and integration permissions.
- **Content too long**: Warn that content was truncated. Suggest splitting into multiple pages for very large reports.
- **Rate limiting**: If Notion returns 429, wait and retry once. If it fails again, save the content locally as a fallback.
