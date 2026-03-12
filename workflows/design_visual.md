# Design Visual Content (Infographic / Image)

## Objective
Generate professional visual content — infographics, images, diagrams, and branded assets — using Google Gemini's image generation capabilities.

## Required Inputs
- **request_type**: "infographic" or "image"
- **description**: What the user wants to create (topic, data, purpose)
- **context**: Any supporting data, text, or specifications

## Optional Inputs
- **infographic_type**: dashboard | comparison | process_flow | timeline | statistics | org_chart | swot | custom
- **color_scheme**: Brand colors or theme preference
- **aspect_ratio**: Output dimensions (default: 3:4 for infographics, 16:9 for presentations)
- **style**: Photorealistic, flat vector, watercolor, minimalist, corporate, etc.

## Tools Used
- **generate_image**: For general image creation (photos, illustrations, banners, icons)
- **design_infographic**: For structured data visualization (dashboards, comparisons, flows)
- **save_output**: To save any accompanying text/description
- **push_to_notion**: To push visual content references to Notion

## Steps

### 1. Understand the Request
Analyze what the user needs:
- Is this a data visualization (infographic) or creative image?
- What is the target audience? (executive presentation, social media, internal report)
- What format/size is needed? (slide, poster, mobile, print)

### 2. Choose the Right Tool

**Use `design_infographic` when:**
- Visualizing data, KPIs, metrics, or statistics
- Creating comparison charts, SWOT analysis, or org charts
- Building process flows or timelines
- Making business dashboards or report visuals

**Use `generate_image` when:**
- Creating illustrations, banners, or hero images
- Generating product mockups or concept art
- Making social media graphics
- Creating icons or decorative elements

### 3. Craft the Prompt
For best results:
- Be specific about layout, colors, and typography
- Include all text content that should appear in the image
- Specify the visual style (corporate, modern, playful, etc.)
- Mention the brand (VCF Group, VC Meat, etc.) if relevant

### 4. Generate the Visual
Call the appropriate tool with optimized parameters:
- **Infographics**: Use 3:4 aspect ratio, 2K size for print quality
- **Presentation slides**: Use 16:9 aspect ratio, 2K size
- **Social media posts**: Use 1:1 for Instagram, 9:16 for Stories
- **Banners**: Use 21:9 or 16:9

### 5. Review and Iterate
- Check if the output matches the request
- If text is unclear, try regenerating with simplified text
- Offer to adjust colors, layout, or content

### 6. Deliver
- Save the image to .tmp/ (automatic)
- Optionally push a reference to Notion
- Provide the file path to the user

## Expected Outputs
- PNG image file in .tmp/ directory
- Optional markdown description saved alongside

## Infographic Type Guide

| Type | Best For | Example Use Case |
|------|----------|-----------------|
| dashboard | KPI overview, metrics summary | Monthly farm production report |
| comparison | Side-by-side evaluation | ERP system comparison (SAP vs Dynamics) |
| process_flow | Step-by-step procedures | Feed mill production process |
| timeline | Project milestones, history | Myanmar expansion timeline |
| statistics | Key numbers, achievements | Annual revenue highlights |
| org_chart | Team structure, hierarchy | VCF Group organizational structure |
| swot | Strategic analysis | New market entry analysis |
| custom | Free-form design | Any unique layout need |

## Edge Cases

- **Too much text**: Gemini may not render all text clearly. Break into multiple infographics if content is dense.
- **Brand-specific fonts**: Gemini generates approximate typography. For exact brand fonts, use the output as a layout reference and refine in design tools.
- **Complex data tables**: Use `generate_chart` (matplotlib) for precise data charts, then `generate_image` for the visual wrapper.
- **No API key**: Tool returns clear error with setup instructions.

## Example Prompts

### Dashboard Infographic
```
Title: "VCF Group Q1 2026 Performance"
Content: "Revenue: 450M THB (+12%), Production: 85,000 pigs, Feed Output: 120,000 tons, Export Volume: 15,000 carcasses, Employee Count: 2,500"
Type: dashboard
Color scheme: "VCF corporate blue and gold"
```

### Process Flow
```
Title: "Feed Mill Production Process"
Content: "1. Raw Material Intake → 2. Grinding & Milling → 3. Batching & Mixing → 4. Pelleting → 5. Cooling → 6. Screening → 7. Bagging/Bulk Loading → 8. Quality Control → 9. Dispatch"
Type: process_flow
```

### Comparison
```
Title: "ERP System Comparison"
Content: "SAP: Enterprise-grade, High cost, Long implementation, Best for large corps. Dynamics 365: Mid-range, Moderate cost, Faster setup, Good integration with Office. Odoo: Open source, Low cost, Highly customizable, Community support."
Type: comparison
```
