# Generate KPI Dashboard

## Objective
Generate a comprehensive KPI dashboard report for one or all business units, with scorecard, alerts, charts, and optional infographic visualization.

## Required Inputs
- **business_unit**: Which BU to generate for (VCF-Group, VC-Meat-Processing, VC-Meat-Distribution, GT21-Myanmar, or "all")
- **period**: Report period in YYYY-MM format (e.g. "2026-03")

## Optional Inputs
- **data_file**: Path to CSV with actual KPI values (auto-detected if in standard location)
- **output_format**: markdown, infographic, pdf, notion, or all (default: markdown)
- **include_charts**: Whether to generate matplotlib charts (default: true)

## Tools Used
- **calculate_kpis**: Compute KPI scorecard from definitions + data
- **generate_chart**: Create bar/line charts for KPI visualization
- **design_infographic**: Generate visual dashboard using Gemini
- **save_output**: Save markdown report to file
- **push_to_notion**: Push dashboard to Notion database
- **export_pdf**: Convert markdown dashboard to PDF

## Steps

### 1. Determine Scope
- If business_unit is "all", loop through all 4 BUs
- If specific BU, process only that one
- Validate the period format (YYYY-MM)

### 2. Calculate KPI Scorecard
Call `calculate_kpis` for each business unit:
```
calculate_kpis(business_unit="VCF-Group", period="2026-03")
```
This returns a formatted markdown scorecard with:
- Metric table (target vs actual vs achievement vs status)
- RED/YELLOW alerts
- Trend analysis (if prior period data available)
- Summary statistics

### 3. Generate Charts (if requested)
For each BU with data, generate visualizations:
- **Bar chart**: Actual vs Target for top 10 metrics
- **Pie chart**: Status distribution (GREEN/YELLOW/RED)

Use `generate_chart` with the loaded data:
```
generate_chart(chart_type="bar", x_column="metric", y_column="actual", title="VCF Group KPIs - March 2026")
```

### 4. Generate Infographic (if requested)
Use `design_infographic` with dashboard type:
```
design_infographic(
    title="VCF Group KPI Dashboard - March 2026",
    content="[scorecard summary text from step 2]",
    infographic_type="dashboard",
    color_scheme="corporate blue and gold",
    aspect_ratio="16:9"
)
```

### 5. Save Report
Save the markdown scorecard via `save_output`:
```
save_output(content="[full scorecard]", filename="kpi-dashboard-VCF-Group-2026-03.md", directory="Areas/Business-Units/VCF-Group")
```

### 6. Push to Notion (if requested)
```
push_to_notion(title="KPI Dashboard - VCF Group - March 2026", content="[scorecard markdown]")
```

### 7. Export PDF (if requested)
```
export_pdf(input_file="Areas/Business-Units/VCF-Group/kpi-dashboard-VCF-Group-2026-03.md")
```

### 8. Executive Summary (for "all" BUs)
If processing all business units, compile a cross-BU executive summary:
- Top 3 metrics per BU
- Traffic-light status per BU
- Cross-BU alert summary
- Overall portfolio health score

## Expected Outputs
- `Areas/Business-Units/{BU}/dashboard-{period}.md` — Markdown scorecard
- `.tmp/chart_kpi_{BU}_{period}.png` — Bar chart (if charts enabled)
- `.tmp/infographic_kpi_{BU}_{period}.png` — Visual dashboard (if infographic enabled)
- `.tmp/kpi-dashboard-{BU}-{period}.pdf` — PDF report (if PDF enabled)
- Notion page (if Notion push enabled)

## Edge Cases
- **No data file**: Calculator returns template scorecard with targets only and "---" for actuals. User can fill in manually.
- **Partial data**: Metrics without matching CSV rows show "---". Only metrics with data get status colors.
- **Status-type metrics** (e.g. compliance): Handled as categorical (compliant/in_progress/non_compliant) instead of numeric.
- **All BUs request**: Process sequentially, then compile executive summary.
- **Missing YAML definitions**: Tool returns clear error with available BU list.

## Example Usage

### Single BU Dashboard
```
"Generate KPI dashboard for VCF-Group for March 2026"
```

### All BUs Executive Summary
```
"Generate executive KPI summary for all business units, period 2026-03"
```

### Full Output Pipeline
```
"Generate KPI dashboard for VC-Meat-Processing March 2026, include charts and infographic, push to Notion, export PDF"
```
