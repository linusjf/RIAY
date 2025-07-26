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
Image classification script
Analyzes an image file and classifies it as monochrome, grayscale, sepia, or full color

Usage: classifyimage.py <image-file>
Output: Classification result with emoji indicator
Returns: 0 on success, 1 on error
"""

import argparse
import sys
import logging
from pathlib import Path
from PIL import Image
from typing import Optional, Dict, Any, Tuple, Union
import numpy as np
import json
from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory


VERSION = "1.0.0"

config = ConfigEnv()
logger = LoggerFactory.get_logger(
    __name__,
    logging.DEBUG,
    logfile="classifyimage.log",
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)


class ImageClassifier:
    """Class for classifying images by color type."""

    def __init__(self, image_path: Optional[str] = None) -> None:
        self.image_path = image_path
        self.result: Dict[str, Union[str, bool, Optional[Dict[str, int]]]] = {
            "image_color": "unknown",
            "is_monochrome": False,
            "is_grayscale": False,
            "average_rgb": None
        }

    def is_monochrome(self, image: Image.Image) -> bool:
        """Check if image has only two distinct grayscale values (likely monochrome)"""
        gray = image.convert("L")
        unique_values = np.unique(np.array(gray))
        return len(unique_values) <= 2

    def is_grayscale(self, image: Image.Image) -> bool:
        """Check if R == G == B for all pixels"""
        rgb = image.convert("RGB")
        data = np.array(rgb)
        r, g, b = data[..., 0], data[..., 1], data[..., 2]
        return bool(np.all(r == g) and np.all(g == b))

    def average_rgb(self, image: Image.Image) -> Tuple[int, int, int]:
        """Downsample image to 1x1 to get average color"""
        img = image.convert("RGB").resize((1, 1))
        pixel = img.getpixel((0, 0))
        if isinstance(pixel, tuple) and len(pixel) == 3:
            return pixel
        else:
            raise ValueError("Expected RGB pixel tuple (3 values), got: {}".format(pixel))

    def classify(self) -> Dict[str, Any]:
        """Classify image and return results as dictionary."""
        if not self.image_path:
            return {"error": "No image path provided"}

        try:
            img = Image.open(self.image_path)
        except Exception as e:
            return {"error": f"Unable to open image: {e}"}

        if self.is_grayscale(img):
            self.result["is_grayscale"] = True
            if self.is_monochrome(img):
                self.result["image_color"] = "Monochrome"
                self.result["is_monochrome"] = True
            else:
                self.result["image_color"] = "Grayscale"
        else:
            avg_color = self.average_rgb(img)
            if isinstance(avg_color, tuple) and len(avg_color) == 3:
                r, g, b = avg_color
                self.result["average_rgb"] = {"r": r, "g": g, "b": b}

                rg_diff = abs(r - g)
                gb_diff = abs(g - b)

                if rg_diff < 5 and gb_diff < 5:
                    self.result["image_color"] = "Grayscale"
                elif r > g > b and (r - b) > 30:
                    self.result["image_color"] = "Sepia"
                else:
                    self.result["image_color"] = "Color"

        return self.result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify image as monochrome, grayscale, sepia or full color"
    )
    parser.add_argument("image_file", help="Path to the image file")
    parser.add_argument("-v", "--version", action="version", version=VERSION)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_path = args.image_file

    if not Path(image_path).is_file():
        logger.error(f"File not found: {image_path}")
        sys.exit(1)

    classifier = ImageClassifier(image_path)
    result = classifier.classify()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
