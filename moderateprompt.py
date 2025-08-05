#!/usr/bin/env python
"""Moderate user prompts using OpenAI's moderation API.

This script checks if a given text prompt violates content policies by sending it
to OpenAI's moderation endpoint. It returns a JSON response indicating any flagged
content categories.

Usage:
    moderationprompt.py "your prompt here"
    moderationprompt.py -h | --help
"""

import json
import os
import sys
import asyncio
import argparse
from typing import Dict, Any, Optional

from openai import AsyncOpenAI
from openai.types.moderation import Moderation

MODEL_NAME: str = "omni-moderation-latest"
MAX_PROMPT_LENGTH: int = 4096


async def check_prompt(prompt: str) -> Moderation:
    """Check if prompt violates content policies using OpenAI moderation.

    Args:
        prompt: Text string to be checked for policy violations

    Returns:
        Moderation results including flagged categories and scores

    Raises:
        SystemExit: If API call fails
    """
    client: AsyncOpenAI = AsyncOpenAI()

    try:
        response: Any = await client.moderations.create(
            model=MODEL_NAME,
            input=prompt,
        )
        return response.results[0]
    except Exception as error:
        print(f"Error calling moderation API: {error}", file=sys.stderr)
        sys.exit(4)


def format_results(result: Moderation) -> Dict[str, Any]:
    """Format moderation results into a filtered dictionary.

    Args:
        result: Raw moderation result object

    Returns:
        Filtered results with only relevant flagged categories
    """
    if not result.flagged:
        return {"flagged": False}

    categories: Dict[str, bool] = vars(result.categories)
    scores: Dict[str, float] = vars(result.category_scores)
    input_types: Dict[str, Optional[str]] = vars(result.category_applied_input_types)

    filtered: Dict[str, Any] = {
        "flagged": True,
        "categories": {},
        "category_scores": {},
        "category_applied_input_types": {}
    }

    for category, is_flagged in categories.items():
        if is_flagged:
            filtered["categories"][category] = True
            filtered["category_scores"][category] = scores.get(category, 0.0)
            if category in input_types:
                filtered["category_applied_input_types"][category] = (
                    input_types[category]
                )

    return filtered


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Moderate user prompts using OpenAI's moderation API",
        usage="moderationprompt.py [-h] \"your prompt\""
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Text prompt to be checked for policy violations"
    )
    parser.add_argument(
        "-h", "--help",
        action="help",
        help="Show this help message and exit"
    )
    return parser.parse_args()


async def async_main() -> None:
    """Main entry point for the script."""
    args = parse_args()

    if not args.prompt:
        print(
            "Error: No prompt provided\n",
            file=sys.stderr
        )
        parse_args().print_help()
        sys.exit(2)

    prompt: str = args.prompt

    if not os.getenv("OPENAI_API_KEY"):
        print(
            "Error: OPENAI_API_KEY environment variable is not set.",
            file=sys.stderr
        )
        sys.exit(3)

    if len(prompt) > MAX_PROMPT_LENGTH:
        print(
            f"Error: Prompt exceeds maximum length of {MAX_PROMPT_LENGTH} characters",
            file=sys.stderr
        )
        sys.exit(5)

    result: Moderation = await check_prompt(prompt)
    formatted: Dict[str, Any] = format_results(result)
    print(json.dumps(formatted, indent=2))
    sys.exit(1 if result.flagged else 0)


def main() -> None:
    """Synchronous wrapper for async_main."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
