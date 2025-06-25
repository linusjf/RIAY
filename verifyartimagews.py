#!/usr/bin/env python
"""
Verifyartimagews.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : verifyartimagews
# @created     : Wednesday Jun 25, 2025 12:45:50 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import sys
import argparse
import requests
from PIL import Image
from io import BytesIO
import base64
import json
from fuzzywuzzy import fuzz
import os

# Read API key from environment variable
DEEPINFRA_TOKEN = os.getenv("DEEPINFRA_TOKEN")
if not DEEPINFRA_TOKEN:
    raise ValueError("DEEPINFRA_TOKEN environment variable not set")
HEADERS = {"Authorization": f"Bearer {DEEPINFRA_TOKEN}"}

# DeepInfra model endpoints
BLIP_URL = "https://api.deepinfra.com/v1/inference/Salesforce/blip-image-captioning-base"
CLIP_URL = "https://api.deepinfra.com/v1/inference/openai/clip-vit-base-patch32"

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def generate_caption(image_path):
    image_base64 = encode_image_to_base64(image_path)
    response = requests.post(
        BLIP_URL,
        headers=HEADERS,
        json={"inputs": {"image": image_base64}}
    )
    if response.status_code != 200:
        raise Exception(f"BLIP request failed: {response.text}")
    return response.json().get("generated_text", "")

def clip_similarity(image_path, text):
    image_base64 = encode_image_to_base64(image_path)
    response = requests.post(
        CLIP_URL,
        headers=HEADERS,
        json={"inputs": {"image": image_base64, "text": [text]}}
    )
    if response.status_code != 200:
        raise Exception(f"CLIP request failed: {response.text}")
    probs = response.json().get("logits_per_image", [[0]])[0]
    return probs[0]

def compute_match_terms(caption, metadata_terms):
    matched = []
    for term in metadata_terms:
        score = fuzz.partial_ratio(term.lower(), caption.lower())
        if score > 70:
            matched.append(term)
    return matched

def main():
    parser = argparse.ArgumentParser(description="Verify if an image matches artwork metadata using DeepInfra-hosted models.")
    parser.add_argument("--image", required=True, help="Path to the image file")
    parser.add_argument("--title", required=True, help="Title of the artwork")
    parser.add_argument("--artist", required=True, help="Artist of the artwork")
    parser.add_argument("--subject", help="Subject of the artwork")
    parser.add_argument("--year", help="Year of the artwork")
    parser.add_argument("--medium", help="Medium of the artwork")
    args = parser.parse_args()

    metadata_text = ", ".join(filter(None, [args.title, args.artist, args.subject, args.year, args.medium]))
    metadata_terms = list(filter(None, [args.title, args.artist, args.subject]))

    caption = generate_caption(args.image)
    clip_score = clip_similarity(args.image, metadata_text)
    match_terms = compute_match_terms(caption, metadata_terms)

    is_likely_match = clip_score > 0.7 and len(match_terms) >= 2

    result = {
        "caption": caption,
        "clip_score": round(clip_score, 3),
        "match_terms": match_terms,
        "is_likely_match": clip_score > 0.7 and len(match_terms) >= 2
    }

    print(json.dumps(result, indent=2))

    # Return appropriate exit code
    sys.exit(0 if is_likely_match else 1)

if __name__ == "__main__":
    main()
