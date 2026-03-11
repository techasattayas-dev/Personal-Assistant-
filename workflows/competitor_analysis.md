# Competitor Analysis

## Objective
Perform a structured competitor analysis using Porter's Five Forces, VRIN framework, and BCG Matrix to evaluate the company's competitive position against key industry rivals.

## Required Inputs
- Company brand guidelines (from `data/brand/`)
- Competitor names and data
- Industry context (market, geography, segments)

## Tools Used
- `load_data` — Load any structured competitor data files
- `analyze_data` — Run comparative analysis
- `generate_chart` — Visualize competitive positioning (BCG matrix, comparison charts)
- `save_output` — Save the final report locally
- `push_to_notion` — Optionally deliver to Notion

## Steps

### 1. Load Company Context
Read the brand guidelines from `data/brand/` to understand the company's identity, business segments, certifications, market position, and competitive advantages.

### 2. Identify Key Competitors
Based on the industry and geography, identify the top 3-5 direct competitors. Gather data on their revenue, market share, product lines, and strategic positioning.

### 3. Porter's Five Forces Analysis
Evaluate the industry through five dimensions:
- **Threat of New Entrants** — barriers to entry (capital, regulations, integration)
- **Bargaining Power of Suppliers** — raw material dependency, alternatives
- **Bargaining Power of Buyers** — customer concentration, switching costs
- **Threat of Substitutes** — alternative proteins, imports
- **Competitive Rivalry** — number of competitors, market concentration, differentiation

### 4. VRIN Analysis
Assess the company's resources and capabilities against VRIN criteria:
- **Valuable** — does the resource create value or neutralize threats?
- **Rare** — is it uncommon among competitors?
- **Inimitable** — is it costly or difficult to replicate?
- **Non-substitutable** — are there no strategic equivalents?

Compare the company's VRIN profile against each competitor.

### 5. BCG Matrix
Plot each business segment on the BCG growth-share matrix:
- **Stars** — high growth, high market share
- **Cash Cows** — low growth, high market share
- **Question Marks** — high growth, low market share
- **Dogs** — low growth, low market share

### 6. Compile Report
Create a comprehensive markdown report with all three frameworks, comparison tables, and strategic recommendations. Save locally and optionally push to Notion.

## Expected Outputs
- `competitor_analysis_report.md` — Full report in `.tmp/`
- Visualization charts (BCG matrix, Five Forces radar) in `.tmp/`

## Edge Cases
- **Limited public data on competitors**: Note data gaps explicitly. Use available proxies (employee count, facility count, export data).
- **Private companies**: Revenue may be estimated. Flag estimates clearly.
- **Multiple subsidiaries**: Analyze at the group level for consistency.
