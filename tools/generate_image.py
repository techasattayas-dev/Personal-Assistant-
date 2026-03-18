"""
Tool: generate_image — Generate images from text prompts using Google Gemini API.

Uses Gemini's native image generation (gemini-2.5-flash-image model) to create
images from text descriptions. Supports aspect ratio and size configuration.
Requires GEMINI_API_KEY in .env.
"""

import os
from pathlib import Path
from datetime import datetime


TMP_DIR = Path(__file__).parent.parent / ".tmp"


def generate_image(
    prompt: str,
    aspect_ratio: str = "1:1",
    image_size: str = "1K",
    output_name: str | None = None,
    style_prefix: str | None = None,
) -> str:
    """Generate an image using Google Gemini API."""
    if not prompt or len(prompt.strip()) < 5:
        return "ERROR: Prompt must be at least 5 characters."

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "ERROR: GEMINI_API_KEY not set in .env file. Get one at https://aistudio.google.com/apikey"

    valid_ratios = [
        "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9",
    ]
    if aspect_ratio not in valid_ratios:
        return f"ERROR: Invalid aspect_ratio '{aspect_ratio}'. Valid: {valid_ratios}"

    valid_sizes = ["512", "1K", "2K"]
    if image_size not in valid_sizes:
        return f"ERROR: Invalid image_size '{image_size}'. Valid: {valid_sizes}"

    # Build the full prompt with optional style prefix
    full_prompt = prompt
    if style_prefix:
        full_prompt = f"{style_prefix}. {prompt}"

    TMP_DIR.mkdir(parents=True, exist_ok=True)

    # Generate output filename
    if output_name:
        safe_name = output_name.replace(" ", "_").replace("/", "_")
        if not safe_name.endswith(".png"):
            safe_name += ".png"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = prompt[:30].lower().replace(" ", "_")
        safe_title = "".join(c for c in safe_title if c.isalnum() or c == "_")
        safe_name = f"gemini_{safe_title}_{timestamp}.png"

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

        # Extract image from response parts
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
            result = f"Image generated and saved to: {output_path}"
            if text_response:
                result += f"\nModel notes: {text_response[:200]}"
            return result
        else:
            return f"ERROR: No image was generated. Model response: {text_response or 'empty'}"

    except ImportError:
        return "ERROR: google-genai package not installed. Run: pip install google-genai"
    except Exception as e:
        # Sanitize error message to avoid leaking API keys
        err_msg = str(e)
        if api_key and api_key in err_msg:
            err_msg = err_msg.replace(api_key, "[REDACTED]")
        return f"ERROR: Image generation failed: {type(e).__name__}: {err_msg}"
