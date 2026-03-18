# Scrape & Research

## Objective
Scrape web content from specified URLs, extract relevant information, and compile structured research outputs. Uses Apify for robust scraping (handles JS-rendered content), with automatic fallback to BeautifulSoup when Apify quota is exhausted.

## Required Inputs
- Target URL(s) to scrape
- Research topic or specific data to extract
- Optional: CSS selector for targeted content extraction

## Tools Used
- `scrape_web` — Primary scraping tool (Apify + BeautifulSoup fallback)
- `analyze_data` — Process and structure scraped content
- `save_output` — Save research output locally
- `push_to_notion` — Optionally deliver findings to Notion

## Steps

### 1. Define Research Scope
Identify the target URLs and what information needs to be extracted. Determine if a CSS selector is needed for specific page sections.

### 2. Scrape Content
Use `scrape_web` to retrieve page content:
- **Apify** (primary): Handles JavaScript-rendered pages, dynamic content, SPAs
- **BeautifulSoup** (fallback): Activates automatically when Apify quota is exhausted or unavailable

Parameters:
- `url` (required): Full URL starting with `http://` or `https://`
- `content_selector` (optional): CSS selector to extract specific content (e.g., `article`, `#main-content`, `.product-info`)
- `max_content_length` (optional): Max characters to return (default: 50,000)

### 3. Process Extracted Content
Review the scraped content for:
- Relevance to the research topic
- Data quality and completeness
- Whether additional pages need to be scraped

If scraping returned `[Scraped via BeautifulSoup — Apify fallback: ...]`, note that JS-rendered content may be missing.

### 4. Structure Findings
Organize the extracted data into a structured format:
- Key facts and figures
- Comparison tables (if multiple sources)
- Source attribution with URLs

### 5. Compile Research Report
Create a markdown report with findings, save locally, and optionally push to Notion.

## Expected Outputs
- Research report in `.tmp/` (markdown format)
- Extracted data tables (if applicable)
- Source list with URLs and scrape timestamps

## Edge Cases
- **JavaScript-heavy sites**: Apify handles these well. If fallback to BeautifulSoup, content may be incomplete — note this in the report.
- **Rate limiting / 429 errors**: Apify handles retries. BeautifulSoup fallback respects rate limits with a 15-second timeout.
- **Apify quota exhausted**: Automatic fallback to BeautifulSoup. A notice is prepended to the output.
- **Content behind login**: Neither engine handles authenticated content. Note the limitation.
- **Very large pages**: Content is truncated at `max_content_length` (default 50,000 chars). Increase if needed, but be mindful of token costs.
- **Invalid or unreachable URLs**: Returns `ERROR: ...` message. Check URL and retry.

## Scraping Strategy for Multi-Page Research
When researching a topic across multiple URLs:
1. Start with the most authoritative source
2. Scrape sequentially to avoid overwhelming targets
3. Use CSS selectors to extract only relevant sections (reduces noise and token cost)
4. Cross-reference data across sources for accuracy
