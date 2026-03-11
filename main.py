#!/usr/bin/env python3
"""
WAT Framework — CLI Entry Point

Usage:
    python main.py "Analyze the sales data in data/sales.csv"
    python main.py --interactive
    python main.py --list-workflows
    python main.py --list-tools
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent / ".env")

from agent.runner import Agent
from agent.workflow_loader import list_workflows
from tools.registry import TOOL_DEFINITIONS


def run_interactive():
    """Run the agent in interactive mode."""
    agent = Agent()
    print("\n  WAT Framework — Interactive Mode")
    print("  Type your task and press Enter. Type 'quit' to exit.\n")

    while True:
        try:
            task = input("  You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n  Goodbye.")
            break

        if not task:
            continue
        if task.lower() in ("quit", "exit", "q"):
            print("  Goodbye.")
            break

        result = agent.run(task)
        print(f"\n  Agent: {result}\n")


def run_single(task: str):
    """Run the agent on a single task."""
    agent = Agent()
    result = agent.run(task)
    print(f"\n{result}")


def show_workflows():
    """List all available workflows."""
    workflows = list_workflows()
    if not workflows:
        print("  No workflows found in workflows/")
        return
    print("\n  Available Workflows:")
    print("  " + "-" * 50)
    for w in workflows:
        print(f"  {w['name']}")
        print(f"    {w['objective']}")
    print()


def show_tools():
    """List all available tools."""
    print("\n  Available Tools:")
    print("  " + "-" * 50)
    for t in TOOL_DEFINITIONS:
        desc = t["description"].split(".")[0]
        print(f"  {t['name']}")
        print(f"    {desc}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="WAT Framework — Agentic AI for Data Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Analyze the dataset in data/sales.csv"
  python main.py "Generate a report from the last analysis and push to Notion"
  python main.py --interactive
  python main.py --list-workflows
        """,
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="The task to execute (e.g. 'Analyze data/sales.csv')",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode",
    )
    parser.add_argument(
        "--list-workflows", "-w",
        action="store_true",
        help="List available workflows",
    )
    parser.add_argument(
        "--list-tools", "-t",
        action="store_true",
        help="List available tools",
    )

    args = parser.parse_args()

    if args.list_workflows:
        show_workflows()
    elif args.list_tools:
        show_tools()
    elif args.interactive:
        run_interactive()
    elif args.task:
        run_single(args.task)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
