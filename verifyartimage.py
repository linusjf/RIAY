#!/usr/bin/env python
"""
Verifyartimage.
Verifyartimage using chatgpt gpt-4o-mini and semantic vector embedding models.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : verifyartimage
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
import re
from io import BytesIO
from dotenv import load_dotenv

import numpy as np
import requests
from openai import OpenAI
from PIL import Image
from simtools import compare_terms, compute_match_dicts, get_embedding, cosine_similarity, MatchMode


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

def image_to_bytes(image_path):
    """Read image file as bytes."""
    with open(image_path, "rb") as file:
        return file.read()


def encode_image_to_base64(image_path):
    """Encode image to base64 string."""
    return base64.b64encode(image_to_bytes(image_path)).decode("utf-8")

def strip_code_guards(text):
    # Remove code block guards like ```json ... ```
    text = re.sub(r'```(?:\w+\n)?(.*?)```', r'\1', text, flags=re.DOTALL)
    # Remove inline backticks
    text = re.sub(r'`([^`]*)`', r'\1', text)
    return text.strip()


def generate_image_description(image_path):
    """Generate image description for given image using OpenAI's gpt-4o-mini."""
    print("🖼️ Generating image description...", file=sys.stderr)
    base64_image = encode_image_to_base64(image_path)
    prompt = os.getenv("ART_METADATA_PROMPT", "Describe and interpret this image in detail.")
    response = client.responses.create(
        model="gpt-4o",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                },
            ],
        }]
    )
    image_description = response.output_text

    print(f"🔍 Image Description: {image_description}", file=sys.stderr)
    print(f"🔍 Token usage: {response.usage}", file=sys.stderr)
    return image_description

def is_json_string(s):
    try:
        json.loads(s)
        return True
    except (ValueError, TypeError):
        return False

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
    parser.add_argument("--location", help="Current location of artwork")
    parser.add_argument("--date", help="Date when artwork was created")
    parser.add_argument("--style", help="Style of the artwork")
    parser.add_argument("--medium", help="Medium of the artwork")

    args = parser.parse_args()

    metadata_text = ", ".join(filter(None, [
        args.title, args.artist, args.subject, args.location, args.date, args.style, args.medium
    ]))
    metadata_dict = vars(args)
    print(f"📋 Metadata text: {metadata_text}", file=sys.stderr)
    print(f"📋 Metadata dict: {metadata_dict}", file=sys.stderr)

    try:
        image_description = strip_code_guards(generate_image_description(args.image))
        if not is_json_string(image_description):
            print(
            f"Error in generating image description from image : {image_description}",
            file=sys.stderr
            )
            sys.exit(1)

        data = json.loads(image_description)
        data['subject'] = data['description']
        image_description_dict = data
        image_description_text = ", ".join(filter(None, [
        data['title'], data['artist'], data['location'], data['date'] , data['style'], data['medium'], data['description']
    ]))
        print(
            f"Image description : {image_description_text}",
            file=sys.stderr
        )

        similarity = compare_terms(metadata_text, image_description_text,MatchMode.COSINE)
        print(f"Cosine similarity: {similarity:.4f}", file=sys.stderr)
        data["cosine_score"] = round(similarity, 3)

        print("🧠 Checking for matching terms...", file=sys.stderr)
        match_terms = compute_match_dicts(metadata_dict, image_description_dict,MatchMode.COSINE)
        is_likely_match = similarity > 0.7 and len(match_terms) >= (len(metadata_dict))//2
        print(
            f"🤔 Is likely match? {'Yes' if is_likely_match else 'No'}",
            file=sys.stderr
        )
        data["is_likely_match"] = True if is_likely_match else False
        data["matched_terms"] = match_terms
        result = json.dumps(data, indent=2)
        print(result)

        sys.exit(0 if is_likely_match else 1)

    except Exception as error:
        print(f"❌ Error: {error}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
