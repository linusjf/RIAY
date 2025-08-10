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
import openai

class ImageMetadataExtractor:
    """Class for extracting image metadata from markdown files."""

    def __init__(self):
        self.config = ConfigEnv(include_os_env=True)
        self.year = int(self.config.get("YEAR", datetime.now().year))
        self.max_days = 366 if self._is_leap_year() else 365
        self.months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.augment_meta_data_prompt = self.config.get("AUGMENT_META_DATA_PROMPT", "")
        self.text_llm_api_key = self.config.get("TEXT_LLM_API_KEY", "")
        self.text_llm_base_url = self.config.get("TEXT_LLM_BASE_URL", "")
        self.text_llm_model = self.config.get("TEXT_LLM_MODEL", "")
        
        # Configure OpenAI client
        self.client = openai.OpenAI(
            api_key=self.text_llm_api_key,
            base_url=self.text_llm_base_url
        )

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

    def _augment_metadata(self, metadata: list[dict]) -> list[dict]:
        """Augment metadata using LLM."""
        if not self.augment_meta_data_prompt or not self.text_llm_api_key:
            return metadata
            
        try:
            response = self.client.chat.completions.create(
                model=self.text_llm_model,
                messages=[
                    {"role": "system", "content": self.augment_meta_data_prompt},
                    {"role": "user", "content": json.dumps(metadata)}
                ],
                response_format={"type": "json_object"}
            )
            
            augmented_data = json.loads(response.choices[0].message.content)
            return augmented_data
        except Exception as e:
            if self.config.get("LOGGING", False):
                print(f"⚠️ Failed to augment metadata: {e}")
            return metadata

    def _extract_metadata(self, start_day: int, end_day: int) -> list[dict]:
        """Extract and augment metadata from markdown files."""
        output_data = []
        total_images = 0

        for day_num in range(start_day, end_day + 1):
            month_name, _ = self._get_month_and_day(day_num)
            md_path = Path(f"{month_name}/Day{day_num:03d}.md")

            if not md_path.is_file():
                continue

            with open(md_path, encoding='utf-8') as f:
                content = f.read()

            # Regex to extract image metadata (skip video thumbnails)
            image_links = re.findall(r'\[!\[(.*?)\]\((.*?)\)\]\((.*?)\s+"(.*?)"\)', content)

            image_data = [
                {
                    "day_number": day_num,
                    "caption": title,
                    "image_filepath": img_path,
                    "image_url": link_url,
                }
                for _, img_path, link_url, title in image_links
                if not link_url.startswith("https://youtu.be")
            ]

            output_data.extend(image_data)
            total_images += len(image_data)

        # Augment metadata with LLM if configured
        if self.augment_meta_data_prompt and self.text_llm_api_key:
            output_data = self._augment_metadata(output_data)

        if self.config.get("LOGGING", False):
            print(f"✅ Processed days {start_day}-{end_day}, found {total_images} images")
        return output_data

    def extract_to_csv(self, csv_path: Path, metadata: list[dict]) -> None:
        """Save metadata to CSV file."""
        write_headers = not csv_path.exists() or csv_path.stat().st_size == 0

        with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if write_headers:
                # Get all possible field names from the first augmented record
                fieldnames = set()
                for record in metadata:
                    fieldnames.update(record.keys())
                writer.writerow(sorted(fieldnames))

            for record in metadata:
                writer.writerow([record.get(field, "") for field in sorted(record.keys())])

    def extract_to_json(self, json_path: Path, metadata: list[dict]) -> None:
        """Save metadata to JSON file."""
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    extractor = ImageMetadataExtractor()
    parser = argparse.ArgumentParser(
        description="Extract image metadata from markdown files organized by month/day",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s images.csv --start-day 1 --end-day 30
  %(prog)s output.json --start-day 100
  %(prog)s all_images.csv

Output formats:
  CSV - Appends data if file exists, creates new with headers otherwise
  JSON - Always creates new file with complete dataset
"""
    )
    parser.add_argument(
        "output_file",
        type=Path,
        help="Output file path (CSV or JSON based on extension)"
    )
    parser.add_argument(
        "--start-day",
        type=int,
        default=1,
        help=f"First day to process (1-{extractor.max_days}, default: 1)"
    )
    parser.add_argument(
        "--end-day",
        type=int,
        default=extractor.max_days,
        help=f"Last day to process (1-{extractor.max_days}, default: full year)"
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

    metadata = extractor._extract_metadata(args.start_day, args.end_day)

    if str(args.output_file).lower().endswith('.json'):
        extractor.extract_to_json(args.output_file, metadata)
    else:
        extractor.extract_to_csv(args.output_file, metadata)

if __name__ == "__main__":
    main()
