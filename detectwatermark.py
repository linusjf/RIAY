#!/usr/bin/env python3
"""Detect watermarks in images using text, edge and frequency analysis."""

import argparse
import json
import os
import re
from typing import Dict, Union

import cv2
import numpy as np
import pytesseract
from PIL import Image


DEFAULT_TEXT_THRESHOLD = 20
DEFAULT_EDGE_THRESHOLD = 0.01
DEFAULT_FREQ_THRESHOLD = 500
FFT_RADIUS = 30
CANNY_THRESHOLDS = (100, 200)


def detect_text_regions(image: np.ndarray) -> str:
    """Detect and extract text from image using OCR.

    Args:
        image: Input image in BGR format

    Returns:
        Extracted text with collapsed whitespace
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return re.sub(r'\s+', ' ', text).strip()


def calculate_edge_density(image: np.ndarray) -> float:
    """Calculate edge density using Canny edge detection.

    Args:
        image: Input image in BGR format

    Returns:
        Ratio of edge pixels to total pixels
    """
    edges = cv2.Canny(image, *CANNY_THRESHOLDS)
    edge_pixels = np.sum(edges > 0)
    total_pixels = image.shape[0] * image.shape[1]
    return edge_pixels / total_pixels


def calculate_frequency_energy(image: np.ndarray, radius: int = FFT_RADIUS) -> float:
    """Calculate high frequency energy using FFT.

    Args:
        image: Input image in BGR format
        radius: Radius for high-pass filter

    Returns:
        Normalized high frequency energy
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fft = np.fft.fft2(gray)
    fft_shift = np.fft.fftshift(fft)

    rows, cols = gray.shape
    center_row, center_col = rows // 2, cols // 2

    mask = np.ones((rows, cols), np.uint8)
    mask[center_row - radius:center_row + radius,
         center_col - radius:center_col + radius] = 0

    high_freq = fft_shift * mask
    magnitude = np.abs(high_freq)

    return np.sum(magnitude) / (rows * cols)


def detect_watermark(
    image_path: str,
    text_threshold: int = DEFAULT_TEXT_THRESHOLD,
    edge_threshold: float = DEFAULT_EDGE_THRESHOLD,
    freq_threshold: float = DEFAULT_FREQ_THRESHOLD
) -> Dict[str, Union[bool, str, float]]:
    """Detect watermark in image using multiple techniques.

    Args:
        image_path: Path to image file
        text_threshold: Minimum text length to consider watermarked
        edge_threshold: Edge density threshold
        freq_threshold: Frequency energy threshold

    Returns:
        Dictionary containing detection results and metrics

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image cannot be read
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Invalid image file")

    text = detect_text_regions(image)
    has_text = len(text) > text_threshold

    edge_density = calculate_edge_density(image)
    high_edges = edge_density > edge_threshold

    freq_energy = calculate_frequency_energy(image)
    high_freq = freq_energy > freq_threshold

    return {
        "watermarked": "Yes" if (has_text or high_edges or high_freq) else "No",
        "watermarks": text,
        "edge_density": edge_density,
        "frequency_energy": freq_energy
    }


def main() -> None:
    """Command line interface for watermark detection."""
    parser = argparse.ArgumentParser(
        description="Detect watermarks in images using multiple techniques"
    )
    parser.add_argument("image", help="Path to JPEG image")
    args = parser.parse_args()

    try:
        result = detect_watermark(args.image)
        print(json.dumps(result, indent=2))
    except Exception as error:
        print(json.dumps({"error": str(error)}, indent=2))


if __name__ == "__main__":
    main()
