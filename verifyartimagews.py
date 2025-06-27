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
import numpy as np
import sys
import argparse
import requests
from PIL import Image
import base64
from openai import OpenAI

import json
from io import BytesIO
from fuzzywuzzy import fuzz
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("DEEPINFRA_TOKEN environment variable not set")
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_TOKEN")
if not DEEPINFRA_API_KEY:
    raise ValueError("DEEPINFRA_TOKEN environment variable not set")
headers = {"Authorization": f"Bearer {DEEPINFRA_API_KEY}"}

client = OpenAI(
    api_key=OPENAI_API_KEY,
)

CLIP_URL = "https://api.deepinfra.com/v1/inference/thenlper/gte-large"

def get_embedding(text):
    response = requests.post(CLIP_URL, headers=headers, json={"inputs": text})
    response.raise_for_status()
    return np.array(response.json()[0])

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def image_to_bytes(image_path):
    with open(image_path, "rb") as f:
        return f.read()

def encode_image_to_base64(image_path):
    return base64.b64encode(image_to_bytes(image_path)).decode("utf-8")

def generate_caption(image_path):
    print("🖼️ Generating caption...", file=sys.stderr)
    base64_image = encode_image_to_base64(image_path)
    prompt = "Describe and interpret this image in detail."
    response = client.responses.create(
    model="gpt-4o-mini",
    input=[ {"role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image}"},
            ],
        }
           ]
    )
    caption = response.output_text

    print(f"🔍 Caption: {caption}", file=sys.stderr)
    print(f"🔍 Token usage: {response.usage}", file=sys.stderr)
    print(caption)
    return caption

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
    parser = argparse.ArgumentParser(description="Verify if an image matches artwork metadata using hosted models.")
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

        # Get embeddings from DeepInfra
        vec1 = get_embedding(metadata_text)
        vec2 = get_embedding(caption)

        # Compute cosine similarity
        similarity = cosine_similarity(vec1, vec2)
        print(f"Cosine similarity: {similarity:.4f}", file=sys.stderr)
        # Compute matched terms
        match_terms = compute_match_terms(caption, metadata_terms)
        is_likely_match = similarity > 0.7 and len(match_terms) > 2
        print(f"🤔 Is likely match? {'Yes' if is_likely_match else 'No'}", file=sys.stderr)
        result = {
            "caption": caption,
            "cosine_score": round(similarity, 3),
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
