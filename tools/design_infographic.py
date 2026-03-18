"""
Tool: design_infographic — Create infographics and visual documents using Google Gemini API.

Generates professional infographics by combining Gemini's image generation
with structured layout prompts optimized for business/data visualization.
Supports multiple infographic types: dashboard, comparison, process flow,
timeline, statistics, and custom layouts.

Requires GEMINI_API_KEY in .env.
"""

import os
from pathlib import Path
from datetime import datetime


TMP_DIR = Path(__file__).parent.parent / ".tmp"

# Pre-built infographic prompt templates
INFOGRAPHIC_TEMPLATES = {
    "dashboard": (
        "Create a professional business dashboard infographic with clean modern design. "
        "Use a dark blue and white color scheme with accent colors for highlights. "
        "Include clear data visualization sections with charts, KPI cards, and metrics. "
        "Layout: header with title at top, KPI summary row, main chart area, bottom details. "
    ),
    "comparison": (
        "Create a professional side-by-side comparison infographic with clean modern design. "
        "Use a split layout with two distinct columns. Include check/cross icons for features. "
        "Use contrasting colors for each side (blue vs orange). "
        "Layout: title at top, two equal columns with comparison points, summary at bottom. "
    ),
    "process_flow": (
        "Create a professional process flow infographic with numbered steps. "
        "Use connected arrows or lines between steps. Each step has an icon and description. "
        "Use a clean horizontal or vertical flow layout with modern flat design. "
        "Color gradient from start to finish step. "
    ),
    "timeline": (
        "Create a professional timeline infographic with milestones. "
        "Use a horizontal or vertical timeline with date markers and descriptions. "
        "Alternate left/right placement for entries. Use clean modern design with icons. "
        "Color code by category or phase. "
    ),
    "statistics": (
        "Create a professional statistics infographic with large bold numbers. "
        "Use icon-number pairs for each statistic. Clean modern layout with plenty of whitespace. "
        "Group related statistics together. Use a consistent color palette. "
    ),
    "org_chart": (
        "Create a professional organizational chart infographic. "
        "Use a hierarchical tree layout with clean boxes connected by lines. "
        "Include role titles and names. Use corporate blue color scheme. "
        "Clear visual hierarchy from top to bottom. "
    ),
    "swot": (
        "Create a professional SWOT analysis infographic with four quadrants. "
        "Strengths (green, top-left), Weaknesses (red, top-right), "
        "Opportunities (blue, bottom-left), Threats (orange, bottom-right). "
        "Each quadrant has an icon header and bullet points. Clean modern design. "
    ),
    "custom": "",
}


def design_infographic(
    title: str,
    content: str,
    infographic_type: str = "dashboard",
    color_scheme: str | None = None,
    aspect_ratio: str = "3:4",
    image_size: str = "2K",
    output_name: str | None = None,
    additional_instructions: str | None = None,
) -> str:
    """Design and generate a professional infographic using Gemini."""
    if not title or not title.strip():
        return "ERROR: Title is required."
    if not content or not content.strip():
        return "ERROR: Content is required. Provide the data/text to visualize."

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "ERROR: GEMINI_API_KEY not set in .env file. Get one at https://aistudio.google.com/apikey"

    if infographic_type not in INFOGRAPHIC_TEMPLATES:
        return f"ERROR: Invalid type '{infographic_type}'. Valid: {list(INFOGRAPHIC_TEMPLATES.keys())}"

    valid_ratios = [
        "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9",
    ]
    if aspect_ratio not in valid_ratios:
        return f"ERROR: Invalid aspect_ratio '{aspect_ratio}'. Valid: {valid_ratios}"

    valid_sizes = ["512", "1K", "2K"]
    if image_size not in valid_sizes:
        return f"ERROR: Invalid image_size '{image_size}'. Valid: {valid_sizes}"

    # Build the infographic generation prompt
    template_prefix = INFOGRAPHIC_TEMPLATES[infographic_type]

    color_instruction = ""
    if color_scheme:
        color_instruction = f"Use this color scheme: {color_scheme}. "

    full_prompt = (
        f"{template_prefix}"
        f"{color_instruction}"
        f"Title: '{title}'. "
        f"Content to visualize: {content}. "
        f"Make all text clearly readable. Use professional typography. "
        f"The design should be print-ready and presentation-quality."
    )

    if additional_instructions:
        full_prompt += f" Additional requirements: {additional_instructions}"

    TMP_DIR.mkdir(parents=True, exist_ok=True)

    # Generate output filename
    if output_name:
        safe_name = output_name.replace(" ", "_").replace("/", "_")
        if not safe_name.endswith(".png"):
            safe_name += ".png"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = title[:25].lower().replace(" ", "_")
        safe_title = "".join(c for c in safe_title if c.isalnum() or c == "_")
        safe_name = f"infographic_{safe_title}_{timestamp}.png"

    output_path = TMP_DIR / safe_name

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
            ),
        )

        # Extract image from response
        image_saved = False
        text_response = ""

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data is not None:
                    image = part.as_image()
                    image.save(str(output_path))
                    image_saved = True
                elif hasattr(part, "text") and part.text:
                    text_response = part.text

        if image_saved:
            result = (
                f"Infographic generated and saved to: {output_path}\n"
                f"Type: {infographic_type} | Size: {image_size} | Ratio: {aspect_ratio}"
            )
            if text_response:
                result += f"\nModel notes: {text_response[:300]}"
            return result
        else:
            return f"ERROR: No image was generated. Model response: {text_response or 'empty'}"

    except ImportError:
        return "ERROR: google-genai package not installed. Run: pip install google-genai"
    except Exception as e:
        err_msg = str(e)
        if api_key and api_key in err_msg:
            err_msg = err_msg.replace(api_key, "[REDACTED]")
        return f"ERROR: Infographic generation failed: {type(e).__name__}: {err_msg}"
