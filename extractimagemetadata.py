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
import sys
import os
import argparse
import time
from pathlib import Path
from datetime import datetime
from itertools import cycle
from threading import Thread
from typing import Optional
from configenv import ConfigEnv
import openai
from loggerutil import LoggerFactory
from configconstants import ConfigConstants
from dateutils import MONTHS, is_leap_year, get_month_and_day, validate_day_range
from markdownhelper import strip_code_guards

class Spinner:
    """Simple terminal spinner for long-running operations."""
    def __init__(self):
        self._running = False
        self._thread: Optional[Thread] = None
        self._spinner = cycle(['-', '/', '|', '\\'])

    def _spin(self):
        while self._running:
            sys.stdout.write(next(self._spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')

    def start(self):
        """Start the spinner animation."""
        self._running = True
        self._thread = Thread(target=self._spin)
        self._thread.start()

    def stop(self):
        """Stop the spinner animation."""
        self._running = False
        if self._thread:
            self._thread.join()
        sys.stdout.write('\b \b')
        sys.stdout.flush()

class ImageMetadataExtractor:
    """Class for extracting image metadata from markdown files."""

    def __init__(self):
        self.config = ConfigEnv(include_os_env=True)
        self.logger = LoggerFactory.get_logger(
            name=os.path.basename(__file__),
            log_to_file=self.config.get(ConfigConstants.LOGGING, False)
        )
        self.year = int(self.config.get(ConfigConstants.YEAR, datetime.now().year))
        self.max_days = 366 if is_leap_year(self.year) else 365
        self.months = MONTHS
        self.augment_meta_data_prompt = self.config.get(ConfigConstants.AUGMENT_META_DATA_PROMPT, "")
        self.text_llm_api_key = self.config.get(ConfigConstants.TEXT_LLM_API_KEY, "")
        self.text_llm_base_url = self.config.get(ConfigConstants.TEXT_LLM_BASE_URL, "")
        self.text_llm_model = self.config.get(ConfigConstants.TEXT_LLM_MODEL, "")

        # Configure OpenAI client
        self.client = openai.OpenAI(
            api_key=self.text_llm_api_key,
            base_url=self.text_llm_base_url
        )
        self.batch_size = self.config.get(ConfigConstants.AUGMENT_META_DATA_BATCH_SIZE, 10)
        self.logger.info("ImageMetadataExtractor initialized")

    def _validate_day_range(self, start_day: int, end_day: int) -> None:
        """Validate the day range is within bounds for the year."""
        validate_day_range(self.year, start_day, end_day)

    def _get_month_and_day(self, day_num: int) -> tuple[str, int]:
        """Get month name and day of month from day of year."""
        return get_month_and_day(self.year, day_num)

    def _augment_metadata(self, metadata: list[dict]) -> list[dict]:
        """Augment metadata using LLM in batches."""
        if not self.augment_meta_data_prompt or not self.text_llm_api_key:
            self.logger.debug("LLM augmentation not configured, skipping")
            return metadata

        spinner = Spinner()
        try:
            total_batches = (len(metadata) // self.batch_size) + (1 if len(metadata) % self.batch_size else 0)
            self.logger.info(f"Starting metadata augmentation with LLM (processing {len(metadata)} records in {total_batches} batches)")
            spinner.start()
            start_time = time.time()

            augmented_data = []

            for i in range(0, len(metadata), self.batch_size):
                batch_start = i + 1
                batch_end = min(i + self.batch_size, len(metadata))
                batch_num = (i // self.batch_size) + 1
                batch = metadata[i:i + self.batch_size]
                batch_start_time = time.time()

                self.logger.info(f"Processing batch {batch_num}/{total_batches} (records {batch_start}-{batch_end})")
                self.logger.debug(f"Input batch {batch_num} data:\n{json.dumps(batch, indent=2)}")

                response = self.client.chat.completions.create(
                    model=self.text_llm_model,
                    messages=[
                        {"role": "system", "content": self.augment_meta_data_prompt},
                        {"role": "user", "content": json.dumps(batch)}
                    ],
                    response_format={"type": "json_object"}
                )

                batch_time = time.time() - batch_start_time
                self.logger.debug(f"Raw LLM response for batch {batch_num}:\n{response}")
                self.logger.info(f"Batch {batch_num} processed in {batch_time:.2f} seconds")

                content = str(response.choices[0].message.content)
                self.logger.debug(f"Content for batch {batch_num}:\n{content}")
                content = strip_code_guards(content)
                self.logger.debug(f"Stripped content for batch {batch_num}:\n{content}")
                batch_result = json.loads(content)
                batch_result = batch_result.get("artrecords", "[]")
                self.logger.debug(f"Parsed LLM response for batch {batch_num}:\n{json.dumps(batch_result, indent=2)}")

                if isinstance(batch_result, list):
                    augmented_data.extend(batch_result)
                    self.logger.info(f"Batch {batch_num} augmentation successful, added {len(batch_result)} records")
                else:
                    self.logger.warning(f"Unexpected response format from LLM for batch {batch_num}: {batch_result}")
                    augmented_data.extend(batch)
                    self.logger.debug(f"Using original data for batch {batch_num}")

            spinner.stop()
            elapsed_time = time.time() - start_time
            self.logger.info(f"Successfully augmented {len(augmented_data)} records in {elapsed_time:.2f} seconds")
            self.logger.debug(f"Final augmented data:\n{json.dumps(augmented_data, indent=2)}")

            return augmented_data
        except Exception as e:
            if 'spinner' in locals():
                spinner.stop()
            self.logger.error(f"Failed to augment metadata: {e}")
            return metadata

    def _extract_metadata(self, start_day: int, end_day: int, augment_data: bool = False) -> list[dict]:
        """Extract and augment metadata from markdown files."""
        output_data = []
        total_images = 0
        self.logger.info(f"Starting metadata extraction for days {start_day} to {end_day}")
        start_time = time.time()

        for day_num in range(start_day, end_day + 1):
            month_name, _ = self._get_month_and_day(day_num)
            md_path = Path(f"{month_name}/Day{day_num:03d}.md")

            if not md_path.is_file():
                self.logger.debug(f"Markdown file not found for day {day_num}, skipping")
                continue

            try:
                with open(md_path, encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                self.logger.error(f"Error reading {md_path}: {e}")
                continue

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
            self.logger.debug(f"Found {len(image_data)} images for day {day_num}")

        # Augment metadata with LLM if configured and requested
        if augment_data and self.augment_meta_data_prompt and self.text_llm_api_key:
            self.logger.info("Starting LLM metadata augmentation")
            output_data = self._augment_metadata(output_data)

        elapsed_time = time.time() - start_time
        self.logger.info(f"Completed processing days {start_day}-{end_day} in {elapsed_time:.2f} seconds, found {total_images} images total")
        return output_data

    def extract_to_csv(self, csv_path: Path, metadata: list[dict]) -> None:
        """Save metadata to CSV file."""
        self.logger.info(f"Saving metadata to CSV file: {csv_path}")

        try:
            with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                fieldnames = set()
                for record in metadata:
                    fieldnames.update(record.keys())
                writer.writerow(sorted(fieldnames))
                self.logger.debug(f"Wrote CSV headers: {sorted(fieldnames)}")

                for record in metadata:
                    writer.writerow([record.get(field, "") for field in sorted(fieldnames)])
            self.logger.info(f"Successfully wrote {len(metadata)} records to CSV")
        except Exception as e:
            self.logger.error(f"Error writing to CSV: {e}")
            raise

    def extract_to_json(self, json_path: Path, metadata: list[dict]) -> None:
        """Save metadata to JSON file."""
        self.logger.info(f"Saving metadata to JSON file: {json_path}")
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            self.logger.info(f"Successfully wrote {len(metadata)} records to JSON")
        except Exception as e:
            self.logger.error(f"Error writing to JSON: {e}")
            raise

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
  CSV - Overwrites existing file with complete dataset
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
    parser.add_argument(
        "--augment-data",
        action="store_true",
        help="Enable LLM augmentation of metadata (if configured)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    extractor = ImageMetadataExtractor()

    try:
        extractor._validate_day_range(args.start_day, args.end_day)
    except ValueError as e:
        extractor.logger.error(f"Invalid day range: {e}")
        sys.exit(1)

    metadata = extractor._extract_metadata(args.start_day, args.end_day, args.augment_data)

    try:
        if str(args.output_file).lower().endswith('.json'):
            extractor.extract_to_json(args.output_file, metadata)
        else:
            extractor.extract_to_csv(args.output_file, metadata)
    except Exception as e:
        extractor.logger.error(f"Failed to save output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
