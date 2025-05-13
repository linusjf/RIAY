#!/usr/bin/env python3
"""Copy image and PDF files from source directory to static directory, excluding specified directories."""

import os
import shutil
from pathlib import Path
from typing import Generator, Tuple

# Constants should be uppercase with underscores
SOURCE_ROOT = Path(".")  # Root of project directory
TARGET_ROOT = Path("_static")
EXCLUDED_DIRS = {"_static", "build", "styles", "tests", ".git"}
SUPPORTED_EXTENSIONS = {".jpg", ".pdf"}


def collect_files_with_paths(
    source_root: Path, target_root: Path
) -> Generator[Tuple[Path, Path], None, None]:
    """Generate source and destination paths for supported files.
    
    Args:
        source_root: Root directory to search for files
        target_root: Destination directory for copied files
        
    Yields:
        Tuples of (source_path, destination_path) for each supported file
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
        source_root: Source directory to search
        target_root: Destination directory for copies
        
    Returns:
        int: Number of files copied
    """
    copied_count = 0
    
    for src_path, dst_path in collect_files_with_paths(source_root, target_root):
        if src_path.resolve() != dst_path.resolve():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"Copied {src_path} to {dst_path}")
            copied_count += 1
            
    return copied_count


def main() -> None:
    """Main entry point for the script."""
    copied = copy_files(SOURCE_ROOT, TARGET_ROOT)
    print(f"Copied {copied} files to {TARGET_ROOT}")


if __name__ == "__main__":
    main()
