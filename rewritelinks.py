#!/usr/bin/env python3
"""Script to rewrite absolute GitHub raw URLs to relative paths in markdown files."""

import re
import sys
import argparse
import os
from pathlib import Path
from typing import Match, Optional, Pattern

from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory


config = ConfigEnv("config.env")
logger = LoggerFactory.get_logger(
    name=os.path.basename(__file__),
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)

DEFAULT_ENV_FILE = "config.env"
GITHUB_URL_TEMPLATE = "https://raw.githubusercontent.com/{user}/{repo}/refs/heads/main/"
RELATIVE_PREFIX = "/_static/"
GH_MARKDOWN_PREFIX = "/"


class LinkRewriter:
    """Handles link rewriting operations with configurable behavior."""

    def __init__(self, use_gh_markdown: bool = False, gh_to_rtd: bool = False) -> None:
        self.use_gh_markdown: bool = use_gh_markdown
        self.gh_to_rtd: bool = gh_to_rtd
        self.replacement_count: int = 0
        self.url_base: Optional[str] = None
        self.config: ConfigEnv = ConfigEnv(DEFAULT_ENV_FILE)

    def get_github_base_url(self) -> str:
        """Construct the GitHub base URL from environment variables.

        Returns:
            str: Formatted GitHub raw content base URL
        """
        user: Optional[str] = self.config.get("REPO_OWNER", "")
        repo: Optional[str] = self.config.get("REPO_NAME", "")

        if not user or not repo:
            logger.error("REPO_OWNER and REPO_NAME must be set in environment variables")
            raise ValueError(
                "REPO_OWNER and REPO_NAME must be set in environment variables"
            )

        return GITHUB_URL_TEMPLATE.format(user=user, repo=repo)

    def make_relative(self, match: Match[str]) -> str:
        """Create relative path from matched URL."""
        self.replacement_count += 1
        file_path: str = match.group(1)
        prefix: str = GH_MARKDOWN_PREFIX if self.use_gh_markdown else RELATIVE_PREFIX
        return f"{prefix}{file_path}"

    def gh_to_rtd_relative(self, match: Match[str]) -> str:
        """Convert GitHub-style relative links to RTD /_static/ links."""
        self.replacement_count += 1
        return f"](/_static/{match.group(2)})"

    def gh_to_rtd_naked(self, match: Match[str]) -> str:
        """Convert GitHub-style naked urls to RTD /_static/ links."""
        self.replacement_count += 1
        return f"</_static/{match.group(2)}>"

    def rewrite_links(self, text: str) -> str:
        """Apply the appropriate link rewriting based on configuration."""
        pattern: Pattern[str]
        if self.gh_to_rtd:
            # Handle regular markdown links [text](/path)
            pattern = re.compile(r'(\]\()/(?!_static/)([^)]+)\)')
            text = pattern.sub(self.gh_to_rtd_relative, text)
            # Handle naked URLs </path>
            pattern = re.compile(r'(<)/(?!_static/)([^>]+)(>)')
            text = pattern.sub(self.gh_to_rtd_naked, text)
        else:
            if not self.url_base:
                self.url_base = self.get_github_base_url()
            pattern = re.compile(re.escape(self.url_base) + r"([^)]+)")
            text = pattern.sub(self.make_relative, text)
        return text


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
        logger.error(f"File not found - {md_file}")
        return 0

    rewriter: LinkRewriter = LinkRewriter(use_gh_markdown, gh_to_rtd)
    original_text: str = md_file.read_text()
    modified_text: str = rewriter.rewrite_links(original_text)

    if rewriter.replacement_count > 0:
        md_file.write_text(modified_text)
        logger.info(f"Updated {md_file}: {rewriter.replacement_count} link(s) modified")

    return rewriter.replacement_count


def main() -> int:
    """Main entry point for the script.

    Returns:
        int: Exit code (0 for success)
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
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

    args: argparse.Namespace
    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        parser.print_help()
        return 1

    if args.abs_to_gh_markdown and args.gh_markdown_to_rtd:
        logger.error("Cannot use both --abs-to-gh-markdown and --gh-markdown-to-rtd together")
        return 1

    total_changes: int = 0
    for file_path in args.files:
        total_changes += rewrite_links_in_file(
            Path(file_path),
            args.abs_to_gh_markdown,
            args.gh_markdown_to_rtd
        )

    if total_changes == 0:
        logger.info("No links were modified in any files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
