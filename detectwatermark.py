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


class WatermarkDetector:
    """Detect watermarks in images using multiple techniques."""

    DEFAULT_TEXT_THRESHOLD = 20
    DEFAULT_EDGE_THRESHOLD = 0.01
    DEFAULT_FREQ_THRESHOLD = 500
    FFT_RADIUS = 30
    CANNY_THRESHOLDS = (100, 200)

    def __init__(
        self,
        text_threshold: int = DEFAULT_TEXT_THRESHOLD,
        edge_threshold: float = DEFAULT_EDGE_THRESHOLD,
        freq_threshold: float = DEFAULT_FREQ_THRESHOLD
    ):
        """Initialize detector with threshold values.
        
        Args:
            text_threshold: Minimum text length to consider watermarked
            edge_threshold: Edge density threshold
            freq_threshold: Frequency energy threshold
        """
        self.text_threshold = text_threshold
        self.edge_threshold = edge_threshold
        self.freq_threshold = freq_threshold

    def detect_text_regions(self, image: np.ndarray) -> str:
        """Detect and extract text from image using OCR.

        Args:
            image: Input image in BGR format

        Returns:
            Extracted text with collapsed whitespace
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        return re.sub(r'\s+', ' ', text).strip()

    def calculate_edge_density(self, image: np.ndarray) -> float:
        """Calculate edge density using Canny edge detection.

        Args:
            image: Input image in BGR format

        Returns:
            Ratio of edge pixels to total pixels
        """
        edges = cv2.Canny(image, *self.CANNY_THRESHOLDS)
        edge_pixels = np.sum(edges > 0)
        total_pixels = image.shape[0] * image.shape[1]
        return edge_pixels / total_pixels

    def calculate_frequency_energy(self, image: np.ndarray) -> float:
        """Calculate high frequency energy using FFT.

        Args:
            image: Input image in BGR format

        Returns:
            Normalized high frequency energy
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)

        rows, cols = gray.shape
        center_row, center_col = rows // 2, cols // 2

        mask = np.ones((rows, cols), np.uint8)
        mask[center_row - self.FFT_RADIUS:center_row + self.FFT_RADIUS,
             center_col - self.FFT_RADIUS:center_col + self.FFT_RADIUS] = 0

        high_freq = fft_shift * mask
        magnitude = np.abs(high_freq)

        return np.sum(magnitude) / (rows * cols)

    def detect(self, image_path: str) -> Dict[str, Union[bool, str, float]]:
        """Detect watermark in image using multiple techniques.

        Args:
            image_path: Path to image file

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

        text = self.detect_text_regions(image)
        has_text = len(text) > self.text_threshold

        edge_density = self.calculate_edge_density(image)
        high_edges = edge_density > self.edge_threshold

        freq_energy = self.calculate_frequency_energy(image)
        high_freq = freq_energy > self.freq_threshold

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
        detector = WatermarkDetector()
        result = detector.detect(args.image)
        print(json.dumps(result, indent=2))
    except Exception as error:
        print(json.dumps({"error": str(error)}, indent=2))


if __name__ == "__main__":
    main()
