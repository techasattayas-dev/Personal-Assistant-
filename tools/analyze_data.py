"""
Tool: analyze_data — Run statistical analysis on the cached dataset.

Supported analysis types:
- summary: Descriptive statistics (describe())
- correlation: Correlation matrix of numeric columns
- group_by: Aggregate by a column
- value_counts: Frequency distribution of a column
- missing: Missing data report
- custom: Run a custom pandas expression
"""

import pandas as pd
from tabulate import tabulate

from tools.load_data import get_cached_df


def analyze_data(
    analysis_type: str,
    column: str | None = None,
    group_by_column: str | None = None,
    agg_column: str | None = None,
    agg_function: str = "mean",
    expression: str | None = None,
) -> str:
    """Run analysis on the cached DataFrame."""
    df = get_cached_df()
    if df is None:
        return "ERROR: No data loaded. Call load_data first."

    try:
        if analysis_type == "summary":
            result = df.describe(include="all").round(2)
            return f"Descriptive Statistics:\n\n{tabulate(result, headers='keys', tablefmt='simple')}"

        elif analysis_type == "correlation":
            numeric_df = df.select_dtypes(include="number")
            if numeric_df.empty:
                return "ERROR: No numeric columns found for correlation analysis."
            corr = numeric_df.corr().round(3)
            return f"Correlation Matrix:\n\n{tabulate(corr, headers='keys', tablefmt='simple', showindex=True)}"

        elif analysis_type == "group_by":
            if not group_by_column:
                return "ERROR: 'group_by_column' is required for group_by analysis."
            if not agg_column:
                return "ERROR: 'agg_column' is required for group_by analysis."
            if group_by_column not in df.columns:
                return f"ERROR: Column '{group_by_column}' not found. Available: {list(df.columns)}"
            if agg_column not in df.columns:
                return f"ERROR: Column '{agg_column}' not found. Available: {list(df.columns)}"

            grouped = df.groupby(group_by_column)[agg_column].agg(agg_function).reset_index()
            grouped.columns = [group_by_column, f"{agg_column}_{agg_function}"]
            return f"Group By Results ({group_by_column} → {agg_function}({agg_column})):\n\n{tabulate(grouped, headers='keys', tablefmt='simple', showindex=False)}"

        elif analysis_type == "value_counts":
            if not column:
                return "ERROR: 'column' is required for value_counts analysis."
            if column not in df.columns:
                return f"ERROR: Column '{column}' not found. Available: {list(df.columns)}"
            vc = df[column].value_counts().reset_index()
            vc.columns = [column, "count"]
            vc["percentage"] = (vc["count"] / len(df) * 100).round(1)
            return f"Value Counts for '{column}':\n\n{tabulate(vc.head(30), headers='keys', tablefmt='simple', showindex=False)}"

        elif analysis_type == "missing":
            missing = df.isnull().sum()
            total = len(df)
            report = pd.DataFrame({
                "column": missing.index,
                "missing": missing.values,
                "percentage": (missing.values / total * 100).round(1),
            })
            report = report[report["missing"] > 0].sort_values("missing", ascending=False)
            if report.empty:
                return "No missing values found in the dataset."
            return f"Missing Data Report:\n\n{tabulate(report, headers='keys', tablefmt='simple', showindex=False)}"

        elif analysis_type == "custom":
            if not expression:
                return "ERROR: 'expression' is required for custom analysis."
            # Restricted execution environment
            result = eval(expression, {"__builtins__": {}}, {"df": df, "pd": pd})
            if isinstance(result, pd.DataFrame):
                return f"Custom Analysis Result:\n\n{tabulate(result.head(50), headers='keys', tablefmt='simple', showindex=True)}"
            elif isinstance(result, pd.Series):
                return f"Custom Analysis Result:\n\n{result.to_string()}"
            else:
                return f"Custom Analysis Result:\n\n{result}"

        else:
            return f"ERROR: Unknown analysis type '{analysis_type}'. Use: summary, correlation, group_by, value_counts, missing, custom."

    except Exception as e:
        return f"ERROR: Analysis failed: {type(e).__name__}: {e}"
