#!/usr/bin/env python
"""
Reverseimagelookup.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : reverseimagelookup
# @created     : Saturday Jul 05, 2025 17:07:38 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import sys
import os
import requests
import argparse
from serpapi import GoogleSearch
from simtools import compare_terms, MatchMode

SERP_API_KEY = os.getenv("SERP_API_KEY")
if not SERP_API_KEY:
    raise ValueError("SERP_API_KEY environment variable not set")

# Get your API key from https://api.imgbb.com/
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
if not IMGBB_API_KEY:
    raise ValueError("IMGBB_API_KEY environment variable not set")

IMAGE_SOURCE_URL = None

def upload_to_imgbb(image_path):
    with open(image_path, "rb") as f:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY},
            files={"image": f}
        )
    if response.status_code == 200:
        json_data = response.json()["data"]
        print(json_data,file=sys.stderr)
        return (json_data["url"], json_data["delete_url"], json_data["id"])
    else:
        raise Exception(f"Upload failed: {response.status_code} {response.text}")


def reverse_image_search(image_url, metadata_text):
    params = {
        "engine": "google_lens",
        "api_key": SERP_API_KEY,
        "url": image_url
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    visual_matches = results["visual_matches"][0:5]
    best_score = 0.0
    best_match = {}
    for image_info in visual_matches:
        title = image_info["title"]
        link = image_info["link"]
        source = image_info["source"]
        url = image_info["image"]
        match_text = ", ".join(filter(None, [
        title, link, source, url
        ]))
        score = compare_terms(metadata_text, match_text, MatchMode.COSINE)
        if score > best_score:
            best_score = score
            best_match = image_info

    print(best_match)


def main():
    global IMAGE_SOURCE_URL
    parser = argparse.ArgumentParser(description='Perform reverse image search using SerpAPI')
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

    # Check for corresponding url.txt file
    url_file = os.path.splitext(args.image)[0] + '.url.txt'
    if os.path.exists(url_file):
        with open(url_file, 'r') as f:
            IMAGE_SOURCE_URL = f.read().strip()
            print(f"Found source URL: {IMAGE_SOURCE_URL}", file=sys.stderr)

    image_url, delete_url, image_id = upload_to_imgbb(args.image)
    print(f"image url: {image_url}", file=sys.stderr)
    print(f"delete url: {delete_url}",file=sys.stderr)
    print(f"image id: {image_id}",file=sys.stderr)

    metadata_text = ", ".join(filter(None, [
        args.title, args.artist, args.subject, args.location, args.date, args.style, args.medium, IMAGE_SOURCE_URL
    ]))

    reverse_image_search(image_url, metadata_text)
    print(f"Try deleting {image_url} in a browser using {delete_url}.", file=sys.stderr)
    sys.exit(0)


if __name__ == '__main__':
    main()
