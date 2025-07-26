#!/usr/bin/env python3
"""Remove table of contents blocks from markdown files.

This script scans markdown files and removes any blocks delimited by
'<!-- toc -->' and '<!-- tocstop -->' comments. The changes are made
in-place to the files.
"""

import re
import os
from pathlib import Path
from typing import Iterator, Pattern

from configconstants import ConfigConstants
from configenv import ConfigEnv
from loggerutil import LoggerFactory


# Initialize logger using LoggerFactory
config = ConfigEnv("config.env")
logger = LoggerFactory.get_logger(
    name=os.path.basename(__file__),
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)

TOC_START_MARKER: str = "<!-- toc -->"
TOC_END_MARKER: str = "<!-- tocstop -->"
TOC_PATTERN: Pattern[str] = re.compile(
    rf"{re.escape(TOC_START_MARKER)}.*?{re.escape(TOC_END_MARKER)}",
    flags=re.DOTALL,
)


def find_markdown_files(directory: str = ".") -> Iterator[Path]:
    """Generate paths to markdown files in directory.

    Args:
        directory: Root directory to search for markdown files

    Yields:
        Path objects for each .md file found
    """
    yield from Path(directory).rglob("*.md")


def strip_toc_from_file(file_path: Path) -> bool:
    """Remove table of contents from a markdown file.

    Args:
        file_path: Path to markdown file to process

    Returns:
        True if changes were made, False otherwise
    """
    original_text: str = file_path.read_text(encoding="utf-8")
    new_text: str = TOC_PATTERN.sub("", original_text)

    if new_text != original_text:
        file_path.write_text(new_text, encoding="utf-8")
        return True
    return False


def strip_toc_blocks(directory: str = ".") -> int:
    """Remove table of contents from all markdown files in directory.

    Args:
        directory: Root directory to search for markdown files

    Returns:
        Number of files modified
    """
    modified_count: int = 0

    for md_file in find_markdown_files(directory):
        if strip_toc_from_file(md_file):
            logger.info(f"Stripped ToC from: {md_file}")
            modified_count += 1

    return modified_count


def main() -> None:
    """Main entry point for the script."""
    modified: int = strip_toc_blocks()
    logger.info(f"Modified {modified} files")


if __name__ == "__main__":
    main()
