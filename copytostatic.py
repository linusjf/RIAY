#!/usr/bin/env python3
"""Copy image and PDF files to static directory while excluding specified directories.

This script recursively searches through the source directory for files with
supported extensions (.jpg, .pdf) and copies them to the target static directory,
while skipping any directories listed in EXCLUDED_DIRS.

Example:
    To run the script from the project root:
    $ python3 copytostatic.py
"""

import os
import shutil
from pathlib import Path
from typing import Generator, Tuple

from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory

config = ConfigEnv("config.env")
logger = LoggerFactory.get_logger(
    name=os.path.basename(__file__),
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)


# Module-level constants
SOURCE_ROOT = Path(".")  # Root of project directory
TARGET_ROOT = Path("_static")
EXCLUDED_DIRS = {"_static", "build", "styles", "tests", ".git"}
SUPPORTED_EXTENSIONS = {".jpg", ".pdf"}


def collect_files_with_paths(
    source_root: Path,
    target_root: Path
) -> Generator[Tuple[Path, Path], None, None]:
    """Generate source and destination paths for supported files.

    Walks through directory tree starting at source_root, skipping any directories
    in EXCLUDED_DIRS, and yields paths for files with supported extensions.

    Args:
        source_root: Root directory to search for files.
        target_root: Destination directory for copied files.

    Yields:
        Tuples of (source_path, destination_path) for each supported file found.
    """
    for root, dirs, files in os.walk(source_root):
        # Skip excluded directories (modifies dirs in-place)
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                rel_path = file_path.relative_to(source_root)
                dst_path = target_root / rel_path
                yield file_path, dst_path


def copy_files(source_root: Path, target_root: Path) -> int:
    """Copy supported files from source to target directory.

    Args:
        source_root: Source directory to search.
        target_root: Destination directory for copies.

    Returns:
        Number of files successfully copied.
    """
    copied_count = 0

    for src_path, dst_path in collect_files_with_paths(source_root, target_root):
        if src_path.resolve() != dst_path.resolve():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            logger.info(f"Copied {src_path} to {dst_path}")
            copied_count += 1

    return copied_count


def main() -> None:
    """Execute the main file copying operation."""
    copied = copy_files(SOURCE_ROOT, TARGET_ROOT)
    logger.info(f"Copied {copied} files to {TARGET_ROOT}")


if __name__ == "__main__":
    main()
