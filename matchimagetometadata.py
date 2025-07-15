#!/usr/bin/env python3
"""
Match image to metadata by combining classification, watermark detection and reverse image lookup.
"""

import argparse
import json
import sys
from pathlib import Path

from classifyimage import ImageClassifier
from detectwatermark import WatermarkDetector
from reverseimagelookup import ReverseImageLookup
from simtools import THRESHOLDS

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
        # 1. Classify the image using ImageClassifier
        classifier = ImageClassifier(image_path)
        classification = classifier.classify()

        # 2. Detect watermarks using WatermarkDetector
        detector = WatermarkDetector()
        watermark = detector.detect(image_path)

        # 3. Perform reverse image lookup
        lookup = ReverseImageLookup(ReverseImageLookup.SEARCH_API.ZENSERP_API)
        score = lookup.match_reverse_lookup(
            image_path,
            args.title,
            args.artist,
            args.subject,
            args.location,
            args.date,
            args.style,
            args.medium
        )

        # Combine all results
        result = classification | watermark
        result["cosine_score"] = score

        print(json.dumps(result, indent=2))
        if score >= THRESHOLDS["cosine"]:
            sys.exit(0)
        sys.exit(1)

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
