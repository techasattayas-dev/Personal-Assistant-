"""
Workflow Loader — Parses markdown SOPs from workflows/ into structured context.

Each workflow is a markdown file with sections that define:
- Objective
- Required Inputs
- Tools Used
- Steps
- Expected Outputs
- Edge Cases
"""

import os
from pathlib import Path


WORKFLOWS_DIR = Path(__file__).parent.parent / "workflows"


def list_workflows() -> list[dict]:
    """List all available workflows with their objectives."""
    workflows = []
    for f in sorted(WORKFLOWS_DIR.glob("*.md")):
        objective = ""
        with open(f) as fh:
            for line in fh:
                if line.startswith("## Objective"):
                    objective = next(fh, "").strip()
                    break
        workflows.append({
            "name": f.stem,
            "file": f.name,
            "objective": objective,
        })
    return workflows


def load_workflow(name: str) -> str | None:
    """Load a workflow's full markdown content by name (without .md extension)."""
    path = WORKFLOWS_DIR / f"{name}.md"
    if not path.exists():
        return None
    return path.read_text()


def get_workflow_context(name: str) -> str:
    """Load a workflow and format it as agent context."""
    content = load_workflow(name)
    if not content:
        return f"Workflow '{name}' not found."
    return (
        f"=== ACTIVE WORKFLOW: {name} ===\n"
        f"Follow these instructions precisely.\n\n"
        f"{content}\n"
        f"=== END WORKFLOW ==="
    )
