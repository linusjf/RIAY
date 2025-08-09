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
from pathlib import Path
from configenv import ConfigEnv

def extract_image_metadata_from_markdown(md_path, csv_path):
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
    write_headers = not Path(csv_path).exists() or Path(csv_path).stat().st_size == 0

    with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if write_headers:
            writer.writerow(["caption", "image_filepath", "image_url"])
        for caption, img_path, img_url in image_data:
            writer.writerow([caption, img_path, img_url])

    config = ConfigEnv()
    if config.get("LOGGING", False):
        print(f"✅ Appended {len(image_data)} image entries to {csv_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_image_metadata.py <markdown_file_path> <output_csv_file_path>")
        sys.exit(1)

    md_file = Path(sys.argv[1])
    csv_file = Path(sys.argv[2])

    if not md_file.is_file():
        print(f"❌ Markdown file not found: {md_file}")
        sys.exit(1)

    extract_image_metadata_from_markdown(md_file, csv_file)
