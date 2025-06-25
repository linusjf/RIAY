#!/usr/bin/env python
"""
Verifyartimagews.
Verifyartimagews using Hugging Face API and upgraded models.

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
import base64
import json
from io import BytesIO
from fuzzywuzzy import fuzz
import os

# Hugging Face API token from environment
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable not set")
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

# Hugging Face model endpoints
BLIP_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
CLIP_URL = "https://api-inference.huggingface.co/models/laion/CLIP-ViT-H-14-laion2B-s32B-b79K"

def image_to_bytes(image_path):
    with open(image_path, "rb") as f:
        return f.read()

def encode_image_to_base64(image_path):
    return base64.b64encode(image_to_bytes(image_path)).decode("utf-8")

def generate_caption(image_path):
    print("🖼️ Generating caption...", file=sys.stderr)
    image_bytes = image_to_bytes(image_path)

    payload = {
        "inputs": {
            "image": base64.b64encode(image_bytes).decode("utf-8"),
            "prompt": "Describe the artwork in detail."
        },
        "parameters": {"max_new_tokens": 50}
    }

    response = requests.post(BLIP_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(f"BLIP2 request failed: {response.text}")

    output = response.json()
    if isinstance(output, dict) and "error" in output:
        raise Exception(f"BLIP2 error: {output['error']}")

    caption = output[0].get("generated_text", "").strip()
    token_usage = response.headers.get("x-compute-time", "unknown")
    print(f"🔍 Caption: {caption}", file=sys.stderr)
    print(f"📊 Caption token usage: ~{token_usage} seconds compute time", file=sys.stderr)
    return caption

def clip_similarity(image_path, text):
    print(f"📐 Calculating similarity score for: {text}", file=sys.stderr)
    image_base64 = encode_image_to_base64(image_path)

    response = requests.post(
        CLIP_URL,
        headers=HEADERS,
        json={"inputs": {"image": image_base64, "text": [text]}}
    )
    if response.status_code != 200:
        raise Exception(f"CLIP request failed: {response.text}")

    result = response.json()
    if isinstance(result, dict) and "error" in result:
        raise Exception(f"CLIP error: {result['error']}")

    score = result["logits_per_image"][0][0]
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
    parser = argparse.ArgumentParser(description="Verify if an image matches artwork metadata using Hugging Face hosted models.")
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

    try:
        caption = generate_caption(args.image)
        clip_score = clip_similarity(args.image, metadata_text)
        match_terms = compute_match_terms(caption, metadata_terms)

        is_likely_match = clip_score > 0.7 and len(match_terms) >= 2
        print(f"🤔 Is likely match? {'Yes' if is_likely_match else 'No'}", file=sys.stderr)

        result = {
            "caption": caption,
            "clip_score": round(clip_score, 3),
            "match_terms": match_terms,
            "is_likely_match": is_likely_match
        }

        print(json.dumps(result, indent=2))
        sys.exit(0 if is_likely_match else 1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
