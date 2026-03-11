"""
Tool Registry — Maps tool names to their implementations and defines schemas.

Each tool is a Python function that takes structured input and returns a string result.
The registry provides the Claude API tool definitions and a dispatch function.
"""

from tools.load_data import load_data
from tools.analyze_data import analyze_data
from tools.generate_chart import generate_chart
from tools.save_output import save_output
from tools.push_to_notion import push_to_notion
from tools.export_pdf import export_pdf


# Maps tool name -> handler function
_HANDLERS = {
    "load_data": load_data,
    "analyze_data": analyze_data,
    "generate_chart": generate_chart,
    "save_output": save_output,
    "push_to_notion": push_to_notion,
    "export_pdf": export_pdf,
}


# Claude API tool definitions
TOOL_DEFINITIONS = [
    {
        "name": "load_data",
        "description": (
            "Load a data file (CSV, Excel, or JSON) and return a summary of its structure. "
            "Returns column names, data types, row count, and a preview of the first rows. "
            "The data is cached in .tmp/ for use by other tools."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the data file (CSV, XLSX, or JSON). Can be absolute or relative to project root.",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "analyze_data",
        "description": (
            "Run statistical analysis on the loaded dataset. Supports: 'summary' (descriptive stats), "
            "'correlation' (correlation matrix), 'group_by' (aggregate by column), 'value_counts' (frequency of values), "
            "'missing' (missing data report), 'custom' (run a custom pandas expression)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "analysis_type": {
                    "type": "string",
                    "enum": ["summary", "correlation", "group_by", "value_counts", "missing", "custom"],
                    "description": "Type of analysis to perform.",
                },
                "column": {
                    "type": "string",
                    "description": "Column name for value_counts or group_by analysis.",
                },
                "group_by_column": {
                    "type": "string",
                    "description": "Column to group by (for group_by analysis).",
                },
                "agg_column": {
                    "type": "string",
                    "description": "Column to aggregate (for group_by analysis).",
                },
                "agg_function": {
                    "type": "string",
                    "enum": ["mean", "sum", "count", "min", "max", "median", "std"],
                    "description": "Aggregation function for group_by analysis.",
                },
                "expression": {
                    "type": "string",
                    "description": "Pandas expression for custom analysis. The DataFrame is available as 'df'. Example: 'df[df[\"age\"] > 30].describe()'",
                },
            },
            "required": ["analysis_type"],
        },
    },
    {
        "name": "generate_chart",
        "description": (
            "Generate a chart/visualization from the loaded data. "
            "Supports bar, line, scatter, histogram, box, pie, and heatmap chart types. "
            "Saves the chart as a PNG file in .tmp/ and returns the file path."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "enum": ["bar", "line", "scatter", "histogram", "box", "pie", "heatmap"],
                    "description": "Type of chart to generate.",
                },
                "x_column": {
                    "type": "string",
                    "description": "Column for x-axis (not needed for histogram or pie).",
                },
                "y_column": {
                    "type": "string",
                    "description": "Column for y-axis (or the value column for histogram/pie).",
                },
                "title": {
                    "type": "string",
                    "description": "Chart title.",
                },
                "color_column": {
                    "type": "string",
                    "description": "Optional column to color/group data points by.",
                },
            },
            "required": ["chart_type"],
        },
    },
    {
        "name": "save_output",
        "description": (
            "Save analysis results to a local file. Supports saving as markdown (.md), "
            "text (.txt), CSV (.csv), or JSON (.json). Files are saved in .tmp/ by default."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The content to save.",
                },
                "filename": {
                    "type": "string",
                    "description": "Output filename (e.g. 'report.md'). Saved in .tmp/ by default.",
                },
                "directory": {
                    "type": "string",
                    "description": "Optional directory to save in (default: .tmp/).",
                },
            },
            "required": ["content", "filename"],
        },
    },
    {
        "name": "push_to_notion",
        "description": (
            "Push analysis results to a Notion page. Creates a new page in the configured "
            "Notion database with the provided title and content (markdown)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title for the Notion page.",
                },
                "content": {
                    "type": "string",
                    "description": "Markdown content for the page body.",
                },
                "database_id": {
                    "type": "string",
                    "description": "Optional Notion database ID. Uses NOTION_DATABASE_ID from .env if not provided.",
                },
            },
            "required": ["title", "content"],
        },
    },
    {
        "name": "export_pdf",
        "description": (
            "Convert a markdown file to a professionally styled PDF report. "
            "Uses WeasyPrint for high-quality PDF output with proper typography, tables, and page layout."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Path to the markdown file to convert. Can be absolute or relative to project root.",
                },
                "output_file": {
                    "type": "string",
                    "description": "Optional output PDF path. Defaults to same name as input with .pdf extension.",
                },
            },
            "required": ["input_file"],
        },
    },
]


def execute_tool(name: str, inputs: dict) -> str:
    """Execute a registered tool by name with the given inputs."""
    handler = _HANDLERS.get(name)
    if not handler:
        return f"ERROR: Unknown tool '{name}'. Available tools: {list(_HANDLERS.keys())}"
    return handler(**inputs)
