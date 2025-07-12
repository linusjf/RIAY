#!/usr/bin/env python3
"""
Match image to metadata by combining classification, watermark detection and reverse image lookup.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from classifyimage import classify_image
from detectwatermark import detect_watermark
from reverseimagelookup import (
    reverse_image_lookup,
    get_metadata_text,
    verify_image_against_metadata
)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Match image to metadata using multiple techniques"
    )
    parser.add_argument(
        "--image", required=True, help="Path to the image file"
    )
    parser.add_argument(
        "--title", required=True, help="Title of the artwork"
    )
    parser.add_argument(
        "--artist", required=True, help="Artist of the artwork"
    )
    parser.add_argument("--subject", help="Subject of the artwork")
    parser.add_argument("--location", help="Current location of artwork")
    parser.add_argument("--date", help="Date when artwork was created")
    parser.add_argument("--style", help="Style of the artwork")
    parser.add_argument("--medium", help="Medium of the artwork")
    return parser.parse_args()


def main():
    """Main function to match image to metadata."""
    args = parse_arguments()
    image_path = args.image

    if not Path(image_path).is_file():
        print(json.dumps({"error": f"File not found: {image_path}"}))
        sys.exit(1)

    try:
        # 1. Classify the image
        classification = classify_image(image_path)
        
        # 2. Detect watermarks
        watermark = detect_watermark(image_path)
        
        # 3. Perform reverse image lookup
        metadata_text = get_metadata_text(
            args.title,
            args.artist,
            args.subject,
            args.location,
            args.date,
            args.style,
            args.medium
        )
        
        reverse_lookup_urls, _ = reverse_image_lookup(
            image_path,
            args.title,
            args.artist,
            args.subject,
            args.location,
            args.date,
            args.style,
            args.medium
        )
        
        verification_score = verify_image_against_metadata(
            reverse_lookup_urls[0][0] if reverse_lookup_urls else "",
            metadata_text
        )

        # Combine all results
        result = {
            "classification": classification,
            "watermark_detection": watermark,
            "reverse_image_lookup": {
                "matches": reverse_lookup_urls,
                "verification_score": verification_score
            },
            "metadata": {
                "title": args.title,
                "artist": args.artist,
                "subject": args.subject,
                "location": args.location,
                "date": args.date,
                "style": args.style,
                "medium": args.medium
            }
        }

        print(json.dumps(result, indent=2))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
