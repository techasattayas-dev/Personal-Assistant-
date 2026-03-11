"""
Tool: save_output — Save analysis results to a local file.

Supports markdown, text, CSV, and JSON output formats.
Default save location is .tmp/ but can be overridden.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = PROJECT_ROOT / ".tmp"


def save_output(
    content: str,
    filename: str,
    directory: str | None = None,
) -> str:
    """Save content to a file."""
    save_dir = Path(directory) if directory else TMP_DIR
    if not save_dir.is_absolute():
        save_dir = PROJECT_ROOT / save_dir

    save_dir.mkdir(parents=True, exist_ok=True)
    output_path = save_dir / filename

    try:
        output_path.write_text(content, encoding="utf-8")
        return f"File saved to: {output_path}"
    except Exception as e:
        return f"ERROR: Failed to save file: {type(e).__name__}: {e}"
