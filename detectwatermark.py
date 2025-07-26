#!/usr/bin/env python3
"""Detect watermarks in images using text, edge and frequency analysis."""

import argparse
import json
import os
import re
import sys
from typing import Dict, Union, Optional, Tuple

import cv2
import numpy as np
import pytesseract

from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory


class WatermarkDetector:
    """Detect watermarks in images using multiple techniques."""

    DEFAULT_TEXT_THRESHOLD: int = 20
    DEFAULT_EDGE_THRESHOLD: float = 0.01
    DEFAULT_FREQ_THRESHOLD: float = 500
    FFT_RADIUS: int = 30
    CANNY_THRESHOLDS: Tuple[int, int] = (100, 200)

    def __init__(
        self,
        text_threshold: int = DEFAULT_TEXT_THRESHOLD,
        edge_threshold: float = DEFAULT_EDGE_THRESHOLD,
        freq_threshold: float = DEFAULT_FREQ_THRESHOLD
    ) -> None:
        """Initialize detector with threshold values.

        Args:
            text_threshold: Minimum text length to consider watermarked
            edge_threshold: Edge density threshold
            freq_threshold: Frequency energy threshold
        """
        self.text_threshold: int = text_threshold
        self.edge_threshold: float = edge_threshold
        self.freq_threshold: float = freq_threshold
        self.config = ConfigEnv("config.env")
        self.logger = LoggerFactory.get_logger(
        name=os.path.basename(__file__),
        log_to_file=self.config.get(ConfigConstants.LOGGING, False)
        )

    def detect_text_regions(self, image: np.ndarray) -> str:
        """Detect and extract text from image using OCR.

        Args:
            image: Input image in BGR format

        Returns:
            Extracted text with collapsed whitespace
        """
        gray: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text: str = pytesseract.image_to_string(gray)
        return re.sub(r'\s+', ' ', text).strip()

    def calculate_edge_density(self, image: np.ndarray) -> float:
        """Calculate edge density using Canny edge detection.

        Args:
            image: Input image in BGR format

        Returns:
            Ratio of edge pixels to total pixels
        """
        edges: np.ndarray = cv2.Canny(image, *self.CANNY_THRESHOLDS)
        edge_pixels: int = int(np.sum(edges > 0))
        total_pixels: int = image.shape[0] * image.shape[1]
        return float(edge_pixels / total_pixels)

    def calculate_frequency_energy(self, image: np.ndarray) -> float:
        """Calculate high frequency energy using FFT.

        Args:
            image: Input image in BGR format

        Returns:
            Normalized high frequency energy
        """
        gray: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fft: np.ndarray = np.fft.fft2(gray)
        fft_shift: np.ndarray = np.fft.fftshift(fft)

        rows: int
        cols: int
        rows, cols = gray.shape
        center_row: int = rows // 2
        center_col: int = cols // 2

        mask: np.ndarray = np.ones((rows, cols), np.uint8)
        mask[center_row - self.FFT_RADIUS:center_row + self.FFT_RADIUS,
             center_col - self.FFT_RADIUS:center_col + self.FFT_RADIUS] = 0

        high_freq: np.ndarray = fft_shift * mask
        magnitude: np.ndarray = np.abs(high_freq)

        return float(np.sum(magnitude) / (rows * cols))

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
            self.logger.error(f"File not found: {image_path}")
            raise FileNotFoundError(f"File not found: {image_path}")

        image: Optional[np.ndarray] = cv2.imread(image_path)
        if image is None:
            self.logger.error(f"Invalid image file: {image_path}")
            raise ValueError(f"Invalid image file: {image_path}")

        text: str = self.detect_text_regions(image)
        has_text: bool = len(text) > self.text_threshold

        edge_density: float = self.calculate_edge_density(image)
        high_edges: bool = edge_density > self.edge_threshold

        freq_energy: float = self.calculate_frequency_energy(image)
        high_freq: bool = freq_energy > self.freq_threshold

        return {
            "watermarked": "Yes" if (has_text or high_edges or high_freq) else "No",
            "watermarks": text,
            "edge_density": edge_density,
            "frequency_energy": freq_energy
        }


def main() -> None:
    """Command line interface for watermark detection."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Detect watermarks in images using multiple techniques"
    )
    parser.add_argument("image", help="Path to JPEG image")
    args: argparse.Namespace = parser.parse_args()

    detector: Optional[WatermarkDetector] = None
    try:
        detector = WatermarkDetector()
        result: Dict[str, Union[bool, str, float]] = detector.detect(args.image)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as error:
        if detector:
            detector.logger.error(str(error))
        print(json.dumps({"error": str(error)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
