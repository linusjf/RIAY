#!/usr/bin/env python3
import cv2
import pytesseract
import numpy as np
from PIL import Image
import argparse
import os
import re

def detect_text_regions(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
    return text.strip()

def edge_density(image):
    edges = cv2.Canny(image, 100, 200)
    edge_pixels = np.sum(edges > 0)
    total_pixels = image.shape[0] * image.shape[1]
    return edge_pixels / total_pixels

def frequency_energy(image, radius=30):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)

    rows, cols = gray.shape
    crow, ccol = rows // 2, cols // 2

    # Create high-pass mask
    mask = np.ones((rows, cols), np.uint8)
    mask[crow - radius:crow + radius, ccol - radius:ccol + radius] = 0

    high_freq = fshift * mask
    magnitude = np.abs(high_freq)

    # Return average energy in high frequencies
    return np.sum(magnitude) / (rows * cols)

def detect_watermark(image_path, text_threshold=20, edge_threshold=0.01, freq_threshold=500):
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Invalid image file")

    text = detect_text_regions(image)
    has_text = len(text) > text_threshold

    edensity = edge_density(image)
    high_edges = edensity > edge_threshold

    fenergy = frequency_energy(image)
    high_freq = fenergy > freq_threshold

    watermarked = has_text or high_edges or high_freq
    return {
        "watermarked": watermarked,
        "text": text,
        "edge_density": edensity,
        "frequency_energy": fenergy
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to JPEG image")
    args = parser.parse_args()

    try:
        result = detect_watermark(args.image)
        print(f"Watermarked: {'Yes' if result['watermarked'] else 'No'}")
        print(f"Detected Text: {result['text'][:100]}{'...' if len(result['text']) > 100 else ''}")
        print(f"Edge Density: {result['edge_density']:.4f}")
        print(f"Frequency Energy: {result['frequency_energy']:.2f}")
    except Exception as e:
        print(f"Error: {e}")
