"""
Agent Runner — The core agentic loop powered by Claude.

This is the decision-making layer of the WAT framework. It:
1. Accepts a user task
2. Selects and loads the relevant workflow
3. Executes tools in the correct sequence
4. Handles errors and adapts
5. Delivers results
"""

import json
import os
from pathlib import Path

import anthropic

from agent.workflow_loader import list_workflows, get_workflow_context
from tools.registry import TOOL_DEFINITIONS, execute_tool


PROJECT_ROOT = Path(__file__).parent.parent

SYSTEM_PROMPT = """You are an AI data analyst agent operating within the WAT framework (Workflows, Agents, Tools).

Your role:
- You are the AGENT layer — you handle reasoning and orchestration
- WORKFLOWS (markdown files) tell you what to do step by step
- TOOLS (Python scripts) handle deterministic execution — always use them instead of doing work yourself

How to operate:
1. When given a task, first call `list_workflows` to see available workflows
2. Call `load_workflow` to read the relevant workflow instructions
3. Follow the workflow steps precisely, calling the appropriate tools
4. If a tool fails, read the error, fix your approach, and retry
5. Deliver final outputs as specified in the workflow

Rules:
- NEVER try to analyze data yourself — always use the analysis tools
- NEVER skip workflow steps unless explicitly told to
- If you're unsure which workflow to use, ask the user
- Always report what you did and what the results are

You have access to these tool categories:
- Workflow tools: list and load workflow SOPs
- Data tools: load, analyze, and chart data from files
- Output tools: save results locally or push to Notion
"""


class Agent:
    """Core agent that runs the WAT agentic loop."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
        self.max_turns = int(os.getenv("MAX_AGENT_TURNS", "25"))
        self.messages: list[dict] = []
        self.active_workflow: str | None = None

    def _get_tools(self) -> list[dict]:
        """Build the combined tool list for Claude API."""
        # Meta-tools for workflow management
        meta_tools = [
            {
                "name": "list_workflows",
                "description": "List all available workflow SOPs with their objectives. Call this first to find the right workflow for a task.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "load_workflow",
                "description": "Load a specific workflow by name to get step-by-step instructions. Use the name from list_workflows (without .md extension).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Workflow name (e.g. 'analyze_dataset')",
                        }
                    },
                    "required": ["name"],
                },
            },
        ]
        return meta_tools + TOOL_DEFINITIONS

    def _handle_tool_call(self, tool_name: str, tool_input: dict) -> str:
        """Route a tool call to the appropriate handler."""
        if tool_name == "list_workflows":
            workflows = list_workflows()
            if not workflows:
                return "No workflows found in workflows/ directory."
            lines = ["Available workflows:"]
            for w in workflows:
                lines.append(f"  - {w['name']}: {w['objective']}")
            return "\n".join(lines)

        elif tool_name == "load_workflow":
            name = tool_input["name"]
            self.active_workflow = name
            context = get_workflow_context(name)
            return context

        else:
            # Delegate to tool registry
            return execute_tool(tool_name, tool_input)

    def run(self, task: str) -> str:
        """Run the agent on a task. Returns the final response."""
        self.messages = [{"role": "user", "content": task}]

        print(f"\n{'='*60}")
        print(f"  AGENT STARTED")
        print(f"  Task: {task[:80]}{'...' if len(task) > 80 else ''}")
        print(f"  Model: {self.model}")
        print(f"{'='*60}\n")

        for turn in range(self.max_turns):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8096,
                system=SYSTEM_PROMPT,
                tools=self._get_tools(),
                messages=self.messages,
            )

            # Check if the agent is done (no tool use)
            if response.stop_reason == "end_turn":
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text
                print(f"\n{'='*60}")
                print(f"  AGENT FINISHED (turns: {turn + 1})")
                print(f"{'='*60}\n")
                return final_text

            # Process tool calls
            assistant_content = response.content
            self.messages.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            for block in assistant_content:
                if block.type == "text" and block.text.strip():
                    print(f"  [Agent] {block.text.strip()[:200]}")
                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    print(f"  [Tool Call] {tool_name}({json.dumps(tool_input, default=str)[:120]})")

                    try:
                        result = self._handle_tool_call(tool_name, tool_input)
                        print(f"  [Tool OK] {str(result)[:150]}")
                    except Exception as e:
                        result = f"ERROR: {type(e).__name__}: {e}"
                        print(f"  [Tool FAIL] {result[:150]}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })

            self.messages.append({"role": "user", "content": tool_results})

        return "Agent reached maximum turns without completing the task."
