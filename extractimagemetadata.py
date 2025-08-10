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
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from configenv import ConfigEnv

class ImageMetadataExtractor:
    """Class for extracting image metadata from markdown files."""

    def __init__(self):
        self.config = ConfigEnv()
        self.year = int(self.config.get("YEAR", datetime.now().year))
        self.max_days = 366 if self._is_leap_year() else 365
        self.months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

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

    def _get_month_and_day(self, day_num: int) -> tuple[str, int]:
        """Get month name and day of month from day of year."""
        date = datetime(self.year, 1, 1) + timedelta(days=day_num - 1)
        return self.months[date.month - 1], date.day

    def extract_to_csv(self, csv_path: Path, start_day: int, end_day: int) -> None:
        """Extract image metadata from markdown files and save to CSV."""
        write_headers = not csv_path.exists() or csv_path.stat().st_size == 0
        total_images = 0

        with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if write_headers:
                writer.writerow(["day_number", "caption", "image_filepath", "image_url"])

            for day_num in range(start_day, end_day + 1):
                month_name, day_of_month = self._get_month_and_day(day_num)
                md_path = Path(f"{month_name}/Day{day_num:03d}.md")

                if not md_path.is_file():
                    continue

                with open(md_path, encoding='utf-8') as f:
                    content = f.read()

                # Regex to extract image metadata (skip video thumbnails)
                image_links = re.findall(r'\[!\[(.*?)\]\((.*?)\)\]\((.*?)\s+"(.*?)"\)', content)

                image_data = [
                    (day_num, title, img_path, link_url)
                    for alt_text, img_path, link_url, title in image_links
                    if not link_url.startswith("https://youtu.be")
                ]

                for day, caption, img_path, img_url in image_data:
                    writer.writerow([day, caption, img_path, img_url])

                total_images += len(image_data)

        if self.config.get("LOGGING", False):
            print(f"✅ Processed days {start_day}-{end_day}, found {total_images} images in {csv_path}")

    def extract_to_json(self, json_path: Path, start_day: int, end_day: int) -> None:
        """Extract image metadata from markdown files and save to JSON."""
        output_data = []
        total_images = 0

        for day_num in range(start_day, end_day + 1):
            month_name, day_of_month = self._get_month_and_day(day_num)
            md_path = Path(f"{month_name}/Day{day_num:03d}.md")

            if not md_path.is_file():
                continue

            with open(md_path, encoding='utf-8') as f:
                content = f.read()

            # Regex to extract image metadata (skip video thumbnails)
            image_links = re.findall(r'\[!\[(.*?)\]\((.*?)\)\]\((.*?)\s+"(.*?)"\)', content)

            image_data = [
                {"day_number": day_num, "caption": title, "image_filepath": img_path, "image_url": link_url}
                for alt_text, img_path, link_url, title in image_links
                if not link_url.startswith("https://youtu.be")
            ]

            output_data.extend(image_data)
            total_images += len(image_data)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)

        if self.config.get("LOGGING", False):
            print(f"✅ Processed days {start_day}-{end_day}, found {total_images} images in {json_path}")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    extractor = ImageMetadataExtractor()
    parser = argparse.ArgumentParser(
        description="Extract image metadata from markdown files"
    )
    parser.add_argument(
        "output_file",
        type=Path,
        help="Path to the output file"
    )
    parser.add_argument(
        "--start-day",
        type=int,
        default=1,
        help=f"Starting day number (1-{extractor.max_days})"
    )
    parser.add_argument(
        "--end-day",
        type=int,
        default=extractor.max_days,
        help=f"Ending day number (1-{extractor.max_days})"
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

    if str(args.output_file).lower().endswith('.json'):
        extractor.extract_to_json(args.output_file, args.start_day, args.end_day)
    else:
        extractor.extract_to_csv(args.output_file, args.start_day, args.end_day)

if __name__ == "__main__":
    main()
