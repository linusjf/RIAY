#!/usr/bin/env python
"""
Classifyimage.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : classifyimage
# @created     : Wednesday Jul 02, 2025 16:35:52 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
#!/usr/bin/env python3
"""
Image classification script
Analyzes an image file and classifies it as monochrome, grayscale, sepia, or full color

Usage: classifyimage.py <image-file>
Output: Classification result with emoji indicator
Returns: 0 on success, 1 on error
"""

import argparse
import sys
from pathlib import Path
from PIL import Image
import numpy as np


VERSION = "1.0.0"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Classify image as monochrome, grayscale, sepia or full color"
    )
    parser.add_argument("image_file", help="Path to the image file")
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    return parser.parse_args()


def is_monochrome(image: Image.Image) -> bool:
    """Check if image has only two distinct grayscale values (likely monochrome)"""
    gray = image.convert("L")
    unique_values = np.unique(np.array(gray))
    return len(unique_values) <= 2


def is_grayscale(image: Image.Image) -> bool:
    """Check if R == G == B for all pixels"""
    rgb = image.convert("RGB")
    data = np.array(rgb)
    r, g, b = data[..., 0], data[..., 1], data[..., 2]
    return np.all(r == g) and np.all(g == b)


def average_rgb(image: Image.Image):
    """Downsample image to 1x1 to get average color"""
    img = image.convert("RGB").resize((1, 1))
    return img.getpixel((0, 0))


def classify_image(image_path: str) -> dict:
    """Classify image and return results as dictionary."""
    try:
        img = Image.open(image_path)
    except Exception as e:
        return {"error": f"Unable to open image: {e}"}

    result = {
        "classification": "unknown",
        "is_monochrome": False,
        "is_grayscale": False,
        "average_rgb": None
    }

    if is_grayscale(img):
        result["is_grayscale"] = True
        if is_monochrome(img):
            result["classification"] = "monochrome"
            result["is_monochrome"] = True
        else:
            result["classification"] = "grayscale"
    else:
        r, g, b = average_rgb(img)
        result["average_rgb"] = {"r": r, "g": g, "b": b}
        
        rg_diff = abs(r - g)
        gb_diff = abs(g - b)

        if rg_diff < 5 and gb_diff < 5:
            result["classification"] = "grayscale"
        elif r > g > b and (r - b) > 30:
            result["classification"] = "sepia"
        else:
            result["classification"] = "color"

    return result


def main():
    args = parse_args()
    image_path = args.image_file

    if not Path(image_path).is_file():
        print(f"❌ File not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    result = classify_image(image_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
