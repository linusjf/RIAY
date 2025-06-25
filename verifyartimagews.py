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
    print("🖼️ Generating caption...", file=sys.stderr)
    image_base64 = encode_image_to_base64(image_path)
    response = requests.post(
        BLIP_URL,
        headers=HEADERS,
        json={"inputs": {"image": image_base64}}
    )
    if response.status_code != 200:
        raise Exception(f"BLIP request failed: {response.text}")
    caption = response.json().get("generated_text", "")
    print(f"🔍 Generated caption: {caption}", file=sys.stderr)
    return caption

def clip_similarity(image_path, text):
    print(f"📐 Calculating similarity score for text: {text}", file=sys.stderr)
    image_base64 = encode_image_to_base64(image_path)
    response = requests.post(
        CLIP_URL,
        headers=HEADERS,
        json={"inputs": {"image": image_base64, "text": [text]}}
    )
    if response.status_code != 200:
        raise Exception(f"CLIP request failed: {response.text}")
    probs = response.json().get("logits_per_image", [[0]])[0]
    score = probs[0]
    print(f"📊 CLIP similarity score: {score:.3f}", file=sys.stderr)
    return score

def compute_match_terms(caption, metadata_terms):
    print("🧠 Checking for matching terms...", file=sys.stderr)
    matched = []
    for term in metadata_terms:
        score = fuzz.partial_ratio(term.lower(), caption.lower())
        print(f"  🔎 Comparing '{term}' (score: {score})", file=sys.stderr)
        if score > 70:
            matched.append(term)
    print(f"✅ Matched terms: {matched}", file=sys.stderr)
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
    print(f"📋 Metadata text: {metadata_text}", file=sys.stderr)
    print(f"📋 Metadata terms: {metadata_terms}", file=sys.stderr)

    caption = generate_caption(args.image)
    clip_score = clip_similarity(args.image, metadata_text)
    match_terms = compute_match_terms(caption, metadata_terms)

    is_likely_match = clip_score > 0.7 and len(match_terms) >= 2
    print(f"🤔 Is likely match? {'Yes' if is_likely_match else 'No'} (CLIP score: {clip_score:.3f}, matched terms: {len(match_terms)})", file=sys.stderr)

    result = {
        "caption": caption,
        "clip_score": round(clip_score, 3),
        "match_terms": match_terms,
        "is_likely_match": is_likely_match
    }

    print(json.dumps(result, indent=2))

    # Return appropriate exit code
    sys.exit(0 if is_likely_match else 1)

if __name__ == "__main__":
    main()
