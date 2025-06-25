#!/usr/bin/env python
"""
Veryifyartimage.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : veryifyartimage
# @created     : Wednesday Jun 25, 2025 12:18:00 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import argparse
import json
import sys
from PIL import Image
from fuzzywuzzy import fuzz

import torch
from transformers import (
    AutoConfig,
    BlipProcessor, BlipForConditionalGeneration,
    CLIPProcessor, CLIPModel
)


# Force CPU
device = torch.device("cpu")

# Model identifiers
BLIP_ID = "Salesforce/blip-image-captioning-base"
CLIP_ID = "openai/clip-vit-base-patch32"

print("🔁 Loading BLIP (captioning) processor and model...")
blip_config = AutoConfig.from_pretrained(BLIP_ID, local_files_only=False)
blip_processor = BlipProcessor.from_pretrained(BLIP_ID, local_files_only=False)
blip_model = BlipForConditionalGeneration.from_pretrained(BLIP_ID, config=blip_config, local_files_only=False).to(device)

print("🔁 Loading CLIP (image-text similarity) processor and model...")
clip_processor = CLIPProcessor.from_pretrained(CLIP_ID, local_files_only=False)
clip_model = CLIPModel.from_pretrained(CLIP_ID, local_files_only=False).to(device)

def generate_caption(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = blip_processor(image, "Describe the painting.", return_tensors="pt").to(device)
    out = blip_model.generate(**inputs)
    caption = blip_processor.decode(out[0], skip_special_tokens=True)
    return caption

def clip_similarity(image_path, text):
    image = Image.open(image_path).convert("RGB")
    inputs = clip_processor(text=[text], images=image, return_tensors="pt", padding=True).to(device)
    outputs = clip_model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)
    return probs[0][0].item()

def compute_match_terms(caption, metadata_terms):
    matched = []
    for term in metadata_terms:
        score = fuzz.partial_ratio(term.lower(), caption.lower())
        if score > 70:
            matched.append(term)
    return matched

def main():
    parser = argparse.ArgumentParser(description="Verify if an image matches artwork metadata using local BLIP and CLIP models.")
    parser.add_argument("--image", required=True, help="Path to the image file")
    parser.add_argument("--title", help="Title of the artwork")
    parser.add_argument("--artist", help="Artist of the artwork")
    parser.add_argument("--subject", help="Subject of the artwork")
    parser.add_argument("--year", help="Year of the artwork")
    parser.add_argument("--medium", help="Medium of the artwork")
    args = parser.parse_args()

    metadata_text = ", ".join(filter(None, [args.title, args.artist, args.subject, args.year, args.medium]))
    metadata_terms = list(filter(None, [args.title, args.artist, args.subject]))

    print("🖼️ Generating caption...")
    caption = generate_caption(args.image)

    print("📐 Calculating similarity score...")
    clip_score = clip_similarity(args.image, metadata_text)

    print("🧠 Checking for matching terms...")
    match_terms = compute_match_terms(caption, metadata_terms)

    is_likely_match = clip_score > 0.7 and len(match_terms) >= 2

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
