# Analyze Dataset

## Objective
Perform comprehensive exploratory data analysis on a dataset and produce a structured report with visualizations.

## Required Inputs
- `file_path`: Path to the dataset file (CSV, XLSX, or JSON)

## Tools Used
- `load_data` — Load and inspect the dataset
- `analyze_data` — Run statistical analyses
- `generate_chart` — Create visualizations
- `save_output` — Save the final report locally

## Steps

### 1. Load the Data
Call `load_data` with the provided file path. Review the output to understand:
- Number of rows and columns
- Column names, types, and null counts
- Preview of the first rows

### 2. Check Data Quality
Call `analyze_data` with `analysis_type: "missing"` to identify any missing data patterns. Note any columns with significant missing values (>5%).

### 3. Generate Descriptive Statistics
Call `analyze_data` with `analysis_type: "summary"` to get descriptive statistics for all columns. Note key metrics: means, medians, ranges, and standard deviations.

### 4. Explore Distributions
For each important numeric column, call `generate_chart` with `chart_type: "histogram"` to visualize distributions. Look for skewness, outliers, or multimodal patterns.

### 5. Analyze Relationships
Call `analyze_data` with `analysis_type: "correlation"` to find relationships between numeric columns. For any strong correlations (|r| > 0.7), generate a `scatter` chart.

### 6. Categorical Analysis
For important categorical columns, call `analyze_data` with `analysis_type: "value_counts"` to understand category distributions. Generate `bar` or `pie` charts for key categories.

### 7. Compile Report
Write a markdown report that includes:
- Dataset overview (rows, columns, types)
- Data quality findings
- Key statistical insights
- Notable patterns and correlations
- Recommendations for further analysis

Save the report using `save_output` with filename `analysis_report.md`.

## Expected Outputs
- `analysis_report.md` — Full markdown report in `.tmp/`
- Chart PNGs — Visualizations in `.tmp/`

## Edge Cases
- **Empty dataset**: Report the issue and stop. Do not attempt analysis on empty data.
- **All-null columns**: Mention them in the data quality section and exclude from analysis.
- **Very large datasets (>1M rows)**: Warn the user that analysis may be slow. Consider sampling.
- **Non-numeric data only**: Skip correlation and histogram steps. Focus on value counts and categorical analysis.
- **Mixed data types in columns**: Note type inconsistencies in the report.
