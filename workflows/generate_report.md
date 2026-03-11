# Generate Report

## Objective
Create a polished analysis report from existing analysis results. This workflow is for generating or reformatting deliverables, not for running new analysis.

## Required Inputs
- Analysis results (either from a previous analyze_dataset run, or provided directly)
- `format`: Output format — "markdown", "text", or "json"
- `filename`: Desired output filename

## Tools Used
- `analyze_data` — Retrieve additional data points if needed
- `save_output` — Save the formatted report
- `push_to_notion` — Optionally push to Notion

## Steps

### 1. Gather Results
Review the analysis results provided. If the user references a previous analysis, check `.tmp/analysis_report.md` for existing findings.

### 2. Structure the Report
Organize the content into clear sections:
- **Executive Summary** — 2-3 sentence overview of key findings
- **Dataset Overview** — What data was analyzed, size, scope
- **Key Findings** — Numbered list of the most important insights
- **Detailed Analysis** — Full breakdown with supporting data
- **Visualizations** — Reference any generated charts
- **Recommendations** — Actionable next steps

### 3. Save Locally
Call `save_output` to save the report with the specified filename and format.

### 4. Push to Notion (if requested)
If the user wants the report in Notion, call `push_to_notion` with the report title and content.

## Expected Outputs
- Formatted report file in `.tmp/` (or specified directory)
- Notion page (if requested)

## Edge Cases
- **No previous analysis**: Inform the user they should run the `analyze_dataset` workflow first, or provide raw data.
- **Very long reports**: Split into sections and summarize. Notion has a 100-block limit per page.
- **Missing charts**: Note which visualizations are referenced but not found.
