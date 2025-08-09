#!/usr/bin/env python
"""
Extractimagemetadata.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : extractimagemetadata
# @created     : Saturday Aug 09, 2025 13:41:02 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import csv
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from configenv import ConfigEnv

class ImageMetadataExtractor:
    """Class for extracting image metadata from markdown files."""

    def __init__(self):
        self.config = ConfigEnv()
        self.year = int(self.config.get("YEAR", datetime.now().year))
        self.max_days = 366 if self._is_leap_year() else 365

    def _is_leap_year(self) -> bool:
        """Check if the current year is a leap year."""
        if self.year % 4 != 0:
            return False
        elif self.year % 100 != 0:
            return True
        else:
            return self.year % 400 == 0

    def _validate_day_range(self, start_day: int, end_day: int) -> None:
        """Validate the day range is within bounds for the year."""
        if start_day < 1 or end_day > self.max_days:
            raise ValueError(f"Day range must be between 1 and {self.max_days}")
        if start_day > end_day:
            raise ValueError("Start day must be less than or equal to end day")

    def extract_from_markdown(self, md_path: Path, csv_path: Path) -> None:
        """Extract image metadata from markdown and save to CSV."""
        # Read the markdown content
        with open(md_path, encoding='utf-8') as f:
            content = f.read()

        # Regex to extract image metadata (skip video thumbnails)
        image_links = re.findall(r'\[!\[(.*?)\]\((.*?)\)\]\((.*?)\s+"(.*?)"\)', content)

        image_data = [
            (title, img_path, link_url)
            for alt_text, img_path, link_url, title in image_links
            if not link_url.startswith("https://youtu.be")
        ]

        # Open the CSV file in append mode, create if it doesn't exist
        write_headers = not csv_path.exists() or csv_path.stat().st_size == 0

        with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if write_headers:
                writer.writerow(["caption", "image_filepath", "image_url"])
            for caption, img_path, img_url in image_data:
                writer.writerow([caption, img_path, img_url])

        if self.config.get("LOGGING", False):
            print(f"✅ Appended {len(image_data)} image entries to {csv_path}")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract image metadata from markdown files"
    )
    parser.add_argument(
        "markdown_file",
        type=Path,
        help="Path to the markdown file to process"
    )
    parser.add_argument(
        "output_csv",
        type=Path,
        help="Path to the output CSV file"
    )
    parser.add_argument(
        "--start-day",
        type=int,
        default=1,
        help="Starting day number (1-365/366)"
    )
    parser.add_argument(
        "--end-day",
        type=int,
        default=366,
        help="Ending day number (1-365/366)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    extractor = ImageMetadataExtractor()

    try:
        extractor._validate_day_range(args.start_day, args.end_day)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    if not args.markdown_file.is_file():
        print(f"❌ Markdown file not found: {args.markdown_file}")
        sys.exit(1)

    extractor.extract_from_markdown(args.markdown_file, args.output_csv)

if __name__ == "__main__":
    main()
