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
from tools.generate_image import generate_image
from tools.design_infographic import design_infographic
from tools.kpi_calculator import calculate_kpis
from tools.scrape_web import scrape_web
from tools.read_notion_tasks import read_notion_tasks
from tools.read_notion_projects import read_notion_projects
from tools.read_notion_areas import read_notion_areas
from tools.read_notion_resources import read_notion_resources
from tools.read_notion_friends import read_notion_friends
from tools.read_notion_command_center import read_notion_command_center
from tools.google_maps import google_maps


# Maps tool name -> handler function
_HANDLERS = {
    "load_data": load_data,
    "analyze_data": analyze_data,
    "generate_chart": generate_chart,
    "save_output": save_output,
    "push_to_notion": push_to_notion,
    "export_pdf": export_pdf,
    "generate_image": generate_image,
    "design_infographic": design_infographic,
    "calculate_kpis": calculate_kpis,
    "scrape_web": scrape_web,
    "read_notion_tasks": read_notion_tasks,
    "read_notion_projects": read_notion_projects,
    "read_notion_areas": read_notion_areas,
    "read_notion_resources": read_notion_resources,
    "read_notion_friends": read_notion_friends,
    "read_notion_command_center": read_notion_command_center,
    "google_maps": google_maps,
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
            "Create an entry in any connected Notion database. Supports 6 targets: "
            "'tasks' (create task with due date, recurring), "
            "'projects' (create project with status, end date, folder), "
            "'areas' (create area with pillar), "
            "'resources' (create resource with tags), "
            "'friends' (create contact with relationship, city, channel, contact info), "
            "'notes' (create a generic page with title + markdown body). "
            "Set 'target' to choose the database. Each target accepts its own specific properties."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title/name of the entry (required for all targets).",
                },
                "target": {
                    "type": "string",
                    "enum": ["tasks", "projects", "areas", "resources", "friends", "notes"],
                    "description": (
                        "Which Notion database to create the entry in. "
                        "'tasks': [CC] Tasks DB, 'projects': [CC] Projects DB, "
                        "'areas': [CC] Areas DB, 'resources': [CC] Resources DB, "
                        "'friends': [CC] Friends DB, 'notes': Notes DB (default)."
                    ),
                },
                "content": {
                    "type": "string",
                    "description": "Optional markdown body content appended as page blocks.",
                },
                "database_id": {
                    "type": "string",
                    "description": "Override database ID. Uses .env default for the target if not provided.",
                },
                "due_date": {
                    "type": "string",
                    "description": "ISO date (YYYY-MM-DD) for task due date. Target: tasks.",
                },
                "recurring": {
                    "type": "boolean",
                    "description": "Whether the task is recurring (default: false). Target: tasks.",
                },
                "status": {
                    "type": "string",
                    "enum": ["Not Started", "WIP", "Completed", "On Hold", "Archived"],
                    "description": "Project status. Target: projects.",
                },
                "end_date": {
                    "type": "string",
                    "description": "ISO date (YYYY-MM-DD) for project end date. Target: projects.",
                },
                "folder_url": {
                    "type": "string",
                    "description": "Google Drive or folder URL. Target: projects.",
                },
                "pillar": {
                    "type": "string",
                    "enum": ["Personal", "Business", "Workplace"],
                    "description": "Area pillar category. Target: areas.",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Resource tags (e.g. ['SOP', 'Reference']). Target: resources.",
                },
                "relationship": {
                    "type": "string",
                    "enum": ["Friend", "Business", "Google", "EY", "Creator", "High School"],
                    "description": "Relationship type. Target: friends.",
                },
                "city": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "City names (e.g. ['Bangkok', 'Chiang Mai']). Target: friends.",
                },
                "comms_channel": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Communication channels (e.g. ['LINE', 'Email']). Target: friends.",
                },
                "contact_info": {
                    "type": "string",
                    "description": "Contact information text (phone, email, etc.). Target: friends.",
                },
            },
            "required": ["title"],
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
    {
        "name": "generate_image",
        "description": (
            "Generate images from text prompts using Google Gemini API. "
            "Creates high-quality images for presentations, documents, social media, and creative content. "
            "Supports various aspect ratios and sizes. Saves output as PNG to .tmp/."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": (
                        "Detailed image generation prompt. Be specific about subject, style, colors, "
                        "composition, and mood. Minimum 5 characters."
                    ),
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
                    "description": "Image aspect ratio (default: 1:1). Use 16:9 for presentations, 9:16 for mobile, 3:4 for posters.",
                },
                "image_size": {
                    "type": "string",
                    "enum": ["512", "1K", "2K"],
                    "description": "Output image resolution (default: 1K). Use 2K for print quality.",
                },
                "output_name": {
                    "type": "string",
                    "description": "Optional output filename (e.g. 'hero_banner.png'). Auto-generated if not provided.",
                },
                "style_prefix": {
                    "type": "string",
                    "description": (
                        "Optional style instruction prepended to prompt. "
                        "Examples: 'Photorealistic photography', 'Flat vector illustration', "
                        "'Watercolor painting', 'Minimalist corporate design', 'Isometric 3D render'."
                    ),
                },
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "design_infographic",
        "description": (
            "Design professional infographics and visual documents using Google Gemini API. "
            "Supports dashboard, comparison, process_flow, timeline, statistics, org_chart, swot, and custom types. "
            "Ideal for business presentations, reports, and data visualization. Saves output as PNG to .tmp/."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Infographic title displayed at the top of the design.",
                },
                "content": {
                    "type": "string",
                    "description": (
                        "The data/text to visualize. Can be bullet points, statistics, process steps, "
                        "comparison items, or any structured information."
                    ),
                },
                "infographic_type": {
                    "type": "string",
                    "enum": ["dashboard", "comparison", "process_flow", "timeline", "statistics", "org_chart", "swot", "custom"],
                    "description": (
                        "Type of infographic layout. "
                        "dashboard: KPI/metrics overview. comparison: side-by-side feature comparison. "
                        "process_flow: step-by-step workflow. timeline: chronological milestones. "
                        "statistics: big numbers with icons. org_chart: hierarchical structure. "
                        "swot: SWOT analysis quadrant. custom: free-form design."
                    ),
                },
                "color_scheme": {
                    "type": "string",
                    "description": "Optional color scheme (e.g. 'corporate blue and white', 'green sustainability theme', 'VCF Group brand colors: red and gold').",
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"],
                    "description": "Infographic aspect ratio (default: 3:4 portrait). Use 16:9 for slides, 9:16 for mobile.",
                },
                "image_size": {
                    "type": "string",
                    "enum": ["512", "1K", "2K"],
                    "description": "Output resolution (default: 2K for print quality).",
                },
                "output_name": {
                    "type": "string",
                    "description": "Optional output filename. Auto-generated if not provided.",
                },
                "additional_instructions": {
                    "type": "string",
                    "description": "Any additional design instructions or requirements.",
                },
            },
            "required": ["title", "content"],
        },
    },
    {
        "name": "calculate_kpis",
        "description": (
            "Calculate KPI scorecard for a business unit. Reads KPI definitions from "
            "Areas/Business-Units/{BU}/kpi-definitions.yaml and optionally loads actual data "
            "from a CSV file. Returns a formatted markdown scorecard with traffic-light status "
            "(GREEN/YELLOW/RED), achievement percentages, alerts, and trend analysis. "
            "Available BUs: VCF-Group, VC-Meat-Processing, VC-Meat-Distribution, GT21-Myanmar."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "business_unit": {
                    "type": "string",
                    "enum": ["VCF-Group", "VC-Meat-Processing", "VC-Meat-Distribution", "GT21-Myanmar"],
                    "description": "Business unit folder name.",
                },
                "period": {
                    "type": "string",
                    "description": "Report period in YYYY-MM format (e.g. '2026-03'). Used in header and auto-detects data file.",
                },
                "data_file": {
                    "type": "string",
                    "description": (
                        "Optional path to CSV with actual KPI values. "
                        "CSV columns: metric_key, actual, prior_period (optional). "
                        "If not provided, auto-checks {BU}/data/kpi-{period}.csv."
                    ),
                },
            },
            "required": ["business_unit"],
        },
    },
    {
        "name": "scrape_web",
        "description": (
            "Scrape content from a web page. Uses Apify cloud scraper for robust JavaScript-rendered "
            "content (requires APIFY_TOKEN in .env), automatically falls back to BeautifulSoup for "
            "standard HTML when Apify quota is exhausted or unavailable. Returns extracted text content. "
            "Use for research, competitor analysis, market data, news articles, and any web content extraction."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to scrape (must start with http:// or https://).",
                },
                "content_selector": {
                    "type": "string",
                    "description": (
                        "Optional CSS selector to extract specific content from the page. "
                        "Examples: 'article', '.main-content', '#product-description', 'table.pricing'."
                    ),
                },
                "max_content_length": {
                    "type": "integer",
                    "description": "Max characters to return (default: 50000). Reduce for focused extraction.",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "read_notion_tasks",
        "description": (
            "Read and summarize tasks from the Notion [CC] Tasks Database. "
            "Returns a structured overview of open, overdue, and completed tasks with stats. "
            "Supports three views: 'summary' (overview with overdue + upcoming), "
            "'detailed' (full task list), 'overdue' (only overdue tasks). "
            "Can filter by status: 'all', 'open', or 'done'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "view": {
                    "type": "string",
                    "enum": ["summary", "detailed", "overdue"],
                    "description": (
                        "Output format. 'summary': overview with overdue + upcoming (default). "
                        "'detailed': full list of all tasks. 'overdue': only overdue tasks."
                    ),
                },
                "filter_status": {
                    "type": "string",
                    "enum": ["all", "open", "done"],
                    "description": "Filter by task status. 'all' (default), 'open' (todo only), 'done' (completed only).",
                },
            },
            "required": [],
        },
    },
    {
        "name": "read_notion_projects",
        "description": (
            "Read and summarize projects from the Notion [CC] Projects Database. "
            "Returns a structured overview of all projects with status, timelines, "
            "linked tasks/notes counts, and overdue detection. "
            "Supports two views: 'summary' (overview table) and 'detailed' (full per-project info). "
            "Can filter by status: 'all', 'wip', 'not_started', 'completed', 'on_hold', 'archived'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "view": {
                    "type": "string",
                    "enum": ["summary", "detailed"],
                    "description": (
                        "Output format. 'summary': overview table (default). "
                        "'detailed': full info per project with folder links."
                    ),
                },
                "filter_status": {
                    "type": "string",
                    "enum": ["all", "wip", "not_started", "completed", "on_hold", "archived"],
                    "description": "Filter by project status. 'all' (default), 'wip', 'not_started', 'completed', 'on_hold', 'archived'.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "read_notion_areas",
        "description": (
            "Read and summarize areas from the Notion [CC] Areas Database. "
            "Returns areas grouped by pillar (Personal, Business, Workplace) "
            "with linked projects and notes counts. "
            "Supports two views: 'summary' (table per pillar) and 'detailed' (full per-area info). "
            "Can filter by pillar: 'all', 'personal', 'business', 'workplace'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "view": {
                    "type": "string",
                    "enum": ["summary", "detailed"],
                    "description": "Output format. 'summary' (default) or 'detailed'.",
                },
                "filter_pillar": {
                    "type": "string",
                    "enum": ["all", "personal", "business", "workplace"],
                    "description": "Filter by area pillar. 'all' (default), 'personal', 'business', 'workplace'.",
                },
                "include_archived": {
                    "type": "boolean",
                    "description": "Include archived areas (default: false).",
                },
            },
            "required": [],
        },
    },
    {
        "name": "read_notion_resources",
        "description": (
            "Read and summarize resources from the Notion [CC] Resources Database. "
            "Returns resources with tags (SOP, Reference, Records, Archived) "
            "and linked areas/projects/notes counts. "
            "Supports two views: 'summary' (table) and 'detailed' (full per-resource info). "
            "Can filter by tag: 'all', 'sop', 'reference', 'records', 'archived'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "view": {
                    "type": "string",
                    "enum": ["summary", "detailed"],
                    "description": "Output format. 'summary' (default) or 'detailed'.",
                },
                "filter_tag": {
                    "type": "string",
                    "enum": ["all", "sop", "reference", "records", "archived"],
                    "description": "Filter by tag. 'all' (default), 'sop', 'reference', 'records', 'archived'.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "read_notion_friends",
        "description": (
            "Read and summarize contacts from the Notion [CC] Friends Database. "
            "Returns contacts with relationship type, city, communication channels, and contact info. "
            "Supports two views: 'summary' (table) and 'detailed' (full contact info per person). "
            "Can filter by relationship: 'all', 'friend', 'business', 'google', 'ey', 'creator', 'high_school'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "view": {
                    "type": "string",
                    "enum": ["summary", "detailed"],
                    "description": "Output format. 'summary' (default) or 'detailed'.",
                },
                "filter_relationship": {
                    "type": "string",
                    "enum": ["all", "friend", "business", "google", "ey", "creator", "high_school"],
                    "description": "Filter by relationship type. 'all' (default).",
                },
                "include_archived": {
                    "type": "boolean",
                    "description": "Include archived contacts (default: false).",
                },
            },
            "required": [],
        },
    },
    {
        "name": "read_notion_command_center",
        "description": (
            "Read the Notion Command Center dashboard page. Returns a unified view combining: "
            "Today's routine checklist (daily to-dos), Tasks summary (open/overdue/due today), "
            "Projects summary (by status + overdue), and Areas summary (by pillar). "
            "Three views: 'dashboard' (full overview), 'today' (checklist only), "
            "'status' (quick stats only). This is the main daily briefing tool."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "view": {
                    "type": "string",
                    "enum": ["dashboard", "today", "status"],
                    "description": (
                        "Output format. 'dashboard': full overview with today + tasks + projects + areas (default). "
                        "'today': only today's routine checklist. "
                        "'status': quick stats for tasks and projects."
                    ),
                },
            },
            "required": [],
        },
    },
    {
        "name": "google_maps",
        "description": (
            "Access Google Maps Platform APIs for location intelligence. "
            "Actions: 'search_places' (text search for businesses/places), "
            "'nearby_search' (find places near coordinates), "
            "'place_details' (full info: phone, hours, website for a place_id), "
            "'geocode' (address → coordinates), "
            "'reverse_geocode' (coordinates → address), "
            "'directions' (route with distance/duration between two points), "
            "'distance_matrix' (distances between multiple origins/destinations), "
            "'static_map' (generate map image with markers). "
            "Useful for: finding suppliers, logistics planning, branch location analysis, "
            "competitor mapping, delivery route optimization."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "search_places", "nearby_search", "place_details",
                        "geocode", "reverse_geocode", "directions",
                        "distance_matrix", "static_map",
                    ],
                    "description": "The Google Maps action to perform.",
                },
                "query": {
                    "type": "string",
                    "description": (
                        "Search query or address. Used by: search_places (e.g. 'pig feed suppliers Phichit'), "
                        "nearby_search (keyword filter), geocode (address to convert)."
                    ),
                },
                "location": {
                    "type": "string",
                    "description": (
                        "Location as 'lat,lng' (e.g. '13.7563,100.5018' for Bangkok) or address string. "
                        "Used by: search_places (center point), nearby_search (required center), "
                        "reverse_geocode (required), static_map (map center)."
                    ),
                },
                "radius": {
                    "type": "integer",
                    "description": "Search radius in meters (default: 5000). Max: 50000. Used by search_places, nearby_search.",
                },
                "place_id": {
                    "type": "string",
                    "description": "Google Place ID from search results. Required for place_details action.",
                },
                "origin": {
                    "type": "string",
                    "description": "Starting point (address or lat,lng). Required for directions.",
                },
                "destination": {
                    "type": "string",
                    "description": "End point (address or lat,lng). Required for directions.",
                },
                "origins": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of origin addresses/coordinates. Required for distance_matrix.",
                },
                "destinations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of destination addresses/coordinates. Required for distance_matrix.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["driving", "walking", "bicycling", "transit"],
                    "description": "Travel mode (default: driving). Used by directions, distance_matrix.",
                },
                "language": {
                    "type": "string",
                    "description": "Response language code (default: 'en'). Use 'th' for Thai.",
                },
                "place_type": {
                    "type": "string",
                    "description": (
                        "Filter by place type (e.g. 'restaurant', 'supermarket', 'store', "
                        "'food', 'veterinary_care', 'gas_station'). Used by search_places, nearby_search."
                    ),
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max number of results to return (default: 10, max: 20).",
                },
                "map_zoom": {
                    "type": "integer",
                    "description": "Map zoom level 1-20 (default: 14). Used by static_map.",
                },
                "map_size": {
                    "type": "string",
                    "description": "Map image size as 'WxH' (default: '600x400'). Used by static_map.",
                },
                "markers": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": (
                        "Map markers for static_map. Each marker: "
                        "{'location': 'lat,lng or address', 'label': 'A', 'color': 'red'}."
                    ),
                },
            },
            "required": ["action"],
        },
    },
]


def execute_tool(name: str, inputs: dict) -> str:
    """Execute a registered tool by name with the given inputs."""
    handler = _HANDLERS.get(name)
    if not handler:
        return f"ERROR: Unknown tool '{name}'. Available tools: {list(_HANDLERS.keys())}"
    return handler(**inputs)
