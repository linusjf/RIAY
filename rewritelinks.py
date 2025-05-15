#!/usr/bin/env python3
"""Script to rewrite absolute GitHub raw URLs to relative paths in markdown files."""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import Match

from dotenv import load_dotenv


DEFAULT_ENV_FILE = "config.env"
GITHUB_URL_TEMPLATE = "https://raw.githubusercontent.com/{user}/{repo}/refs/heads/main/"
RELATIVE_PREFIX = "/_static/"
GH_MARKDOWN_PREFIX = "/"


def get_github_base_url() -> str:
    """Construct the GitHub base URL from environment variables.

    Returns:
        str: Formatted GitHub raw content base URL
    """
    load_dotenv(dotenv_path=DEFAULT_ENV_FILE)

    user = os.getenv("REPO_OWNER", "")
    repo = os.getenv("REPO_NAME", "")

    if not user or not repo:
        raise ValueError(
            "REPO_OWNER and REPO_NAME must be set in environment variables"
        )

    return GITHUB_URL_TEMPLATE.format(user=user, repo=repo)


def rewrite_links_in_file(md_file: Path, use_gh_markdown: bool = False, gh_to_rtd: bool = False) -> int:
    """Rewrite GitHub raw URLs to relative paths in a markdown file.

    Args:
        md_file: Path to markdown file to process
        use_gh_markdown: If True, convert to GitHub markdown relative links
        gh_to_rtd: If True, convert GitHub markdown links to RTD /_static/ links

    Returns:
        int: Number of links modified (0 if none)
    """
    if not md_file.is_file():
        print(f"Error: File not found - {md_file}", file=sys.stderr)
        return 0

    url_base = get_github_base_url()
    pattern = re.compile(re.escape(url_base) + r"([^)]+)")
    original_text = md_file.read_text()
    replacement_count = 0

    def make_relative(match: Match) -> str:
        """Create relative path from matched URL."""
        nonlocal replacement_count
        replacement_count += 1
        file_path = match.group(1)
        prefix = GH_MARKDOWN_PREFIX if use_gh_markdown else RELATIVE_PREFIX
        return f"{prefix}{file_path}"

    def gh_to_rtd_relative(match: Match) -> str:
        """Convert GitHub-style relative links to RTD /_static/ links."""
        nonlocal replacement_count
        replacement_count += 1
        return f"](/_static/{match.group(2)})"

    def gh_to_rtd_naked(match: Match) -> str:
        """Convert GitHub-style naked urls to RTD /_static/ links."""
        nonlocal replacement_count
        replacement_count += 1
        return f"</_static/{match.group(2)}>"

    modified_text = original_text

    if gh_to_rtd:
        # Handle regular markdown links [text](/path)
        pattern = re.compile(r'(\]\()/(?!_static/)([^)]+)\)')
        modified_text = pattern.sub(gh_to_rtd_relative, modified_text)
        # Handle naked URLs </path>
        pattern = re.compile(r'(<)/(?!_static/)([^>]+)(>)')
        modified_text = pattern.sub(gh_to_rtd_naked, modified_text)
    else:
        modified_text = pattern.sub(make_relative, modified_text)

    if replacement_count > 0:
        md_file.write_text(modified_text)
        print(
            f"Updated {md_file}: {replacement_count} link(s) modified",
            file=sys.stdout
        )

    return replacement_count


def main() -> int:
    """Main entry point for the script.

    Returns:
        int: Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(
        description='Rewrite GitHub raw URLs in markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  rewritelinks.py README.md
  rewritelinks.py --abs-to-gh-markdown -- *.md
  rewritelinks.py --gh-markdown-to-rtd -- *.md
  rewritelinks.py --help""")
    parser.add_argument('files', nargs='+', help='Markdown files to process')
    parser.add_argument('--abs-to-gh-markdown', action='store_true',
                       help='Convert absolute URLs to GitHub markdown relative links (default: convert to /_static/ paths)')
    parser.add_argument('--gh-markdown-to-rtd', action='store_true',
                       help='Convert GitHub markdown relative links (starting with /) to ReadTheDocs /_static/ paths, except those already starting with /_static/')

    if len(sys.argv) == 1:
        parser.print_help()
        return 1

    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        parser.print_help()
        return 1

    if args.abs_to_gh_markdown and args.gh_markdown_to_rtd:
        print("Error: Cannot use both --abs-to-gh-markdown and --gh-markdown-to-rtd together", file=sys.stderr)
        return 1

    total_changes = 0
    for file_path in args.files:
        total_changes += rewrite_links_in_file(
            Path(file_path),
            args.abs_to_gh_markdown,
            args.gh_markdown_to_rtd
        )

    if total_changes == 0:
        print("No links were modified in any files", file=sys.stdout)

    return 0


if __name__ == "__main__":
    sys.exit(main())
