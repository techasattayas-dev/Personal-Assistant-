"""
Tool: generate_chart — Create data visualizations and save as PNG.

Supports: bar, line, scatter, histogram, box, pie, heatmap.
Charts are saved to .tmp/ and the file path is returned.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd

from tools.load_data import get_cached_df


TMP_DIR = Path(__file__).parent.parent / ".tmp"


def generate_chart(
    chart_type: str,
    x_column: str | None = None,
    y_column: str | None = None,
    title: str | None = None,
    color_column: str | None = None,
) -> str:
    """Generate a chart from the cached DataFrame."""
    df = get_cached_df()
    if df is None:
        return "ERROR: No data loaded. Call load_data first."

    TMP_DIR.mkdir(exist_ok=True)

    # Sanitize title for filename
    safe_title = (title or chart_type).lower().replace(" ", "_")[:40]
    output_path = TMP_DIR / f"chart_{safe_title}.png"

    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        if chart_type == "bar":
            if not x_column or not y_column:
                return "ERROR: bar chart requires x_column and y_column."
            if color_column and color_column in df.columns:
                for name, group in df.groupby(color_column):
                    ax.bar(group[x_column].astype(str), group[y_column], label=str(name), alpha=0.8)
                ax.legend()
            else:
                ax.bar(df[x_column].astype(str), df[y_column])
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            plt.xticks(rotation=45, ha="right")

        elif chart_type == "line":
            if not x_column or not y_column:
                return "ERROR: line chart requires x_column and y_column."
            if color_column and color_column in df.columns:
                for name, group in df.groupby(color_column):
                    ax.plot(group[x_column], group[y_column], label=str(name), marker="o", markersize=3)
                ax.legend()
            else:
                ax.plot(df[x_column], df[y_column], marker="o", markersize=3)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)

        elif chart_type == "scatter":
            if not x_column or not y_column:
                return "ERROR: scatter chart requires x_column and y_column."
            if color_column and color_column in df.columns:
                for name, group in df.groupby(color_column):
                    ax.scatter(group[x_column], group[y_column], label=str(name), alpha=0.6)
                ax.legend()
            else:
                ax.scatter(df[x_column], df[y_column], alpha=0.6)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)

        elif chart_type == "histogram":
            col = y_column or x_column
            if not col:
                return "ERROR: histogram requires x_column or y_column."
            ax.hist(df[col].dropna(), bins=30, edgecolor="black", alpha=0.7)
            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")

        elif chart_type == "box":
            col = y_column or x_column
            if not col:
                return "ERROR: box chart requires x_column or y_column."
            if x_column and y_column and x_column in df.columns:
                groups = [group[y_column].dropna() for _, group in df.groupby(x_column)]
                labels = [str(name) for name, _ in df.groupby(x_column)]
                ax.boxplot(groups, labels=labels)
                ax.set_xlabel(x_column)
                ax.set_ylabel(y_column)
                plt.xticks(rotation=45, ha="right")
            else:
                ax.boxplot(df[col].dropna())
                ax.set_ylabel(col)

        elif chart_type == "pie":
            col = y_column or x_column
            if not col:
                return "ERROR: pie chart requires x_column or y_column (the category column)."
            counts = df[col].value_counts().head(10)
            ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")

        elif chart_type == "heatmap":
            numeric_df = df.select_dtypes(include="number")
            if numeric_df.empty:
                return "ERROR: No numeric columns for heatmap."
            corr = numeric_df.corr()
            im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
            ax.set_xticks(range(len(corr.columns)))
            ax.set_yticks(range(len(corr.columns)))
            ax.set_xticklabels(corr.columns, rotation=45, ha="right")
            ax.set_yticklabels(corr.columns)
            fig.colorbar(im)

        else:
            return f"ERROR: Unknown chart type '{chart_type}'."

        if title:
            ax.set_title(title)
        plt.tight_layout()
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        return f"Chart saved to: {output_path}"

    except Exception as e:
        plt.close("all")
        return f"ERROR: Chart generation failed: {type(e).__name__}: {e}"
