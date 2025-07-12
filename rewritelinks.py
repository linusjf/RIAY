#!/usr/bin/env python3
"""Script to rewrite absolute GitHub raw URLs to relative paths in markdown files."""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Match

from dotenv import load_dotenv


DEFAULT_ENV_FILE = "config.env"
GITHUB_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/{user}/{repo}/refs/heads/main/"
)
RELATIVE_PREFIX = "/_static/"
GH_MARKDOWN_PREFIX = "/"
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def get_github_base_url() -> str:
    """Construct GitHub base URL from environment variables.

    Reads REPO_OWNER and REPO_NAME from environment.

    Returns:
        str: Formatted GitHub raw content base URL

    Raises:
        ValueError: If required environment variables are missing
    """
    load_dotenv(dotenv_path=DEFAULT_ENV_FILE)

    user = os.getenv("REPO_OWNER", "")
    repo = os.getenv("REPO_NAME", "")

    if not user or not repo:
        raise ValueError(
            "REPO_OWNER and REPO_NAME must be set in environment variables"
        )

    return GITHUB_URL_TEMPLATE.format(user=user, repo=repo)


def make_relative(match: Match, replacement_count: int) -> tuple[str, int]:
    """Create relative path from matched URL.

    Args:
        match: Regex match object
        replacement_count: Current count of replacements

    Returns:
        tuple: (replacement string, updated replacement count)
    """
    replacement_count += 1
    file_path = match.group(1)
    return f"{RELATIVE_PREFIX}{file_path}", replacement_count


def gh_to_rtd_relative(match: Match, replacement_count: int) -> tuple[str, int]:
    """Convert GitHub-style relative links to RTD /_static/ links.

    Args:
        match: Regex match object
        replacement_count: Current count of replacements

    Returns:
        tuple: (replacement string, updated replacement count)
    """
    replacement_count += 1
    return f"](/_static/{match.group(2)})", replacement_count


def gh_to_rtd_naked(match: Match, replacement_count: int) -> tuple[str, int]:
    """Convert GitHub-style naked urls to RTD /_static/ links.

    Args:
        match: Regex match object
        replacement_count: Current count of replacements

    Returns:
        tuple: (replacement string, updated replacement count)
    """
    replacement_count += 1
    return f"</_static/{match.group(2)}>", replacement_count


def rewrite_links_in_file(
    md_file: Path,
    use_gh_markdown: bool = False,
    gh_to_rtd: bool = False
) -> int:
    """Rewrite GitHub raw URLs to relative paths in a markdown file.

    Args:
        md_file: Path to markdown file to process
        use_gh_markdown: Convert to GitHub markdown relative links if True
        gh_to_rtd: Convert GitHub markdown links to RTD /_static/ links if True

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

    if gh_to_rtd:
        # Handle regular markdown links [text](/path)
        pattern = re.compile(r'(\]\()/(?!_static/)([^)]+)\)')
        modified_text, replacement_count = pattern.subn(
            lambda m: gh_to_rtd_relative(m, replacement_count),
            original_text
        )
        # Handle naked URLs </path>
        pattern = re.compile(r'(<)/(?!_static/)([^>]+)(>)')
        modified_text, count = pattern.subn(
            lambda m: gh_to_rtd_naked(m, replacement_count),
            modified_text
        )
        replacement_count += count
    else:
        modified_text, replacement_count = pattern.subn(
            lambda m: make_relative(m, replacement_count),
            original_text
        )

    if replacement_count > 0:
        md_file.write_text(modified_text)
        print(
            f"Updated {md_file}: {replacement_count} link(s) modified",
            file=sys.stdout
        )

    return replacement_count


def parse_args() -> argparse.Namespace:
    """Parse and validate command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments

    Raises:
        SystemExit: If arguments are invalid
    """
    parser = argparse.ArgumentParser(
        description='Rewrite GitHub raw URLs in markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  rewritelinks.py README.md
  rewritelinks.py --abs-to-gh-markdown -- *.md
  rewritelinks.py --gh-markdown-to-rtd -- *.md
  rewritelinks.py --help"""
    )
    parser.add_argument(
        'files',
        nargs='+',
        help='Markdown files to process'
    )
    parser.add_argument(
        '--abs-to-gh-markdown',
        action='store_true',
        help='Convert absolute URLs to GitHub markdown relative links'
    )
    parser.add_argument(
        '--gh-markdown-to-rtd',
        action='store_true',
        help='Convert GitHub markdown relative links to ReadTheDocs paths'
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(EXIT_FAILURE)

    args = parser.parse_args()

    if args.abs_to_gh_markdown and args.gh_markdown_to_rtd:
        print(
            "Error: Cannot use both --abs-to-gh-markdown and --gh-markdown-to-rtd",
            file=sys.stderr
        )
        sys.exit(EXIT_FAILURE)

    return args


def main() -> int:
    """Main entry point for the script.

    Returns:
        int: Exit code (0 for success)
    """
    args = parse_args()

    total_changes = 0
    for file_path in args.files:
        total_changes += rewrite_links_in_file(
            Path(file_path),
            args.abs_to_gh_markdown,
            args.gh_markdown_to_rtd
        )

    if total_changes == 0:
        print("No links were modified in any files", file=sys.stdout)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
