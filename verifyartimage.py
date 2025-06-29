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
import argparse
import base64
import json
import os
import sys
from io import BytesIO
from dotenv import load_dotenv

import numpy as np
import requests
from openai import OpenAI
from PIL import Image


# Load environment variables from config.env
load_dotenv('config.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("DEEPINFRA_TOKEN environment variable not set")
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_TOKEN")
if not DEEPINFRA_API_KEY:
    raise ValueError("DEEPINFRA_TOKEN environment variable not set")

client = OpenAI(api_key=OPENAI_API_KEY)

deepinfra_client = OpenAI(
    api_key=DEEPINFRA_API_KEY,
    base_url="https://api.deepinfra.com/v1/openai",
)


def get_embedding(text):
    """Get text embedding using deepinfra client."""
    embeddings = deepinfra_client.embeddings.create(
        model="thenlper/gte-large",
        input=text,
        encoding_format="float"
    )
    return np.array(embeddings.data[0].embedding)


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def image_to_bytes(image_path):
    """Read image file as bytes."""
    with open(image_path, "rb") as file:
        return file.read()


def encode_image_to_base64(image_path):
    """Encode image to base64 string."""
    return base64.b64encode(image_to_bytes(image_path)).decode("utf-8")


def generate_caption(image_path, artdescription):
    """Generate caption for given image using OpenAI."""
    print("🖼️ Generating caption...", file=sys.stderr)
    base64_image = encode_image_to_base64(image_path)
    prompt = os.getenv("ART_METADATA_PROMPT", "Describe and interpret this image in detail.")
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt + "\n\n" + artdescription},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                },
            ],
        }]
    )
    caption = response.output_text

    print(f"🔍 Caption: {caption}", file=sys.stderr)
    print(f"🔍 Token usage: {response.usage}", file=sys.stderr)
    return caption




def main():
    """Main function to verify image matches artwork metadata."""
    parser = argparse.ArgumentParser(
        description="Verify if an image matches artwork metadata using hosted models."
    )
    parser.add_argument(
        "--image", required=True, help="Path to the image file"
    )
    parser.add_argument(
        "--title", required=True, help="Title of the artwork"
    )
    parser.add_argument(
        "--artist", required=True, help="Artist of the artwork"
    )
    parser.add_argument("--subject", help="Subject of the artwork")
    parser.add_argument("--year", help="Year of the artwork")
    parser.add_argument("--medium", help="Medium of the artwork")

    args = parser.parse_args()

    metadata_text = ", ".join(filter(None, [
        args.title, args.artist, args.subject, args.year, args.medium
    ]))
    metadata_terms = list(filter(None, [
        args.title, args.artist, args.year, args.medium, args.subject
    ]))
    print(f"📋 Metadata text: {metadata_text}", file=sys.stderr)
    print(f"📋 Metadata terms: {metadata_terms}", file=sys.stderr)

    try:
        caption = generate_caption(args.image, metadata_text)

        # Get embeddings from DeepInfra
        vec1 = get_embedding(metadata_text)
        vec2 = get_embedding(caption)

        # Compute cosine similarity
        similarity = cosine_similarity(vec1, vec2)
        print(f"Cosine similarity: {similarity:.4f}", file=sys.stderr)
        is_likely_match = similarity > 0.7
        print(
            f"🤔 Is likely match? {'Yes' if is_likely_match else 'No'}",
            file=sys.stderr
        )
        data = json.loads(caption)
        data["cosine_score"] = round(similarity, 3)
        data["is_likely_match"] = True if is_likely_match else False
        result = json.dumps(data, indent=2)
        print(result)

        sys.exit(0 if is_likely_match else 1)

    except Exception as error:
        print(f"❌ Error: {error}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
