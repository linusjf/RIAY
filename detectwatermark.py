#!/usr/bin/env python3
import cv2
import pytesseract
import numpy as np
from PIL import Image
import argparse
import os

def detect_text_regions(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Use Tesseract OCR to extract text
    text = pytesseract.image_to_string(gray)
    return text.strip()

def edge_density(image):
    edges = cv2.Canny(image, 100, 200)
    edge_pixels = np.sum(edges > 0)
    total_pixels = image.shape[0] * image.shape[1]
    return edge_pixels / total_pixels

def detect_watermark(image_path, text_threshold=20, edge_threshold=0.1):
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Invalid image file")

    # Step 1: OCR Text Detection
    detected_text = detect_text_regions(image)
    has_text = len(detected_text) > text_threshold

    # Step 2: Edge Density Heuristic
    edensity = edge_density(image)
    high_edges = edensity > edge_threshold

    # Combine heuristics
    watermarked = has_text or high_edges
    return watermarked, detected_text, edensity

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to JPEG image")
    args = parser.parse_args()

    try:
        watermarked, text, edensity = detect_watermark(args.image)
        print(f"Watermarked: {'Yes' if watermarked else 'No'}")
        print(f"Detected Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        print(f"Edge Density: {edensity:.4f}")
    except Exception as e:
        print(f"Error: {e}")
