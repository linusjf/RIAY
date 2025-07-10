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
from dotenv import load_dotenv
from serpapi import GoogleSearch
from simtools import compare_terms, MatchMode
from htmlhelper import clean_filename_text
from bashhelper import parse_bash_array
from urllib.parse import urlparse
from pathlib import Path

STOCK_PHOTO_SITES = parse_bash_array('config.env', 'STOCK_PHOTO_SITES')
# Load environment variables from config.env
load_dotenv('config.env')
SERP_API_KEY = os.getenv("SERP_API_KEY")
if not SERP_API_KEY:
    raise ValueError("SERP_API_KEY environment variable not set")

# Get your API key from https://api.imgbb.com/
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
if not IMGBB_API_KEY:
    raise ValueError("IMGBB_API_KEY environment variable not set")

MIN_IMAGE_WIDTH = 350
MIN_IMAGE_HEIGHT = 480

def upload_to_imgbb(image_path):
    with open(image_path, "rb") as f:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY},
            files={"image": f}
        )
    if response.status_code == 200:
        json_data = response.json()["data"]
        return (json_data["url"], json_data["delete_url"])
    else:
        raise Exception(f"Upload failed: {response.status_code} {response.text}")


def reverse_image_search(image_url, metadata_text):
    params = {
        "engine": "google_lens",
        "api_key": SERP_API_KEY,
        "url": image_url,
        "type": "visual_matches"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    visual_matches = results["visual_matches"][0:5]
    qualifying_urls = []
    for image_info in visual_matches:
        title = image_info["title"]
        link = image_info["link"]
        source = image_info["source"]
        url = image_info["image"]
        image_width = image_info["image_width"]
        image_height = image_info["image_height"]

        # Skip PDF links
        if link.lower().endswith('.pdf'):
            continue

        # Skip stock photo sites
        parsed_url = urlparse(link)
        domain = parsed_url.netloc.lower()
        if any(stock_domain.lower() in domain for stock_domain in STOCK_PHOTO_SITES):
            continue
        if (int(image_width) < MIN_IMAGE_WIDTH or int(image_height) < MIN_IMAGE_HEIGHT):
            continue

        match_text = ", ".join(filter(None, [
            title, clean_filename_text(link), source, clean_filename_text(url)
        ]))
        score = compare_terms(metadata_text, match_text, MatchMode.COSINE)
        if score > 0.7:  # Only include URLs that meet the minimum score threshold
            qualifying_urls.append((url, score))

    # Sort by score in descending order
    qualifying_urls.sort(key=lambda x: x[1], reverse=True)
    return qualifying_urls


def validate_image_path(path):
    """Validate that the path exists and is a file."""
    path_obj = Path(path)
    if not path_obj.exists():
        raise argparse.ArgumentTypeError(f"File '{path}' does not exist")
    if not path_obj.is_file():
        raise argparse.ArgumentTypeError(f"'{path}' is not a file")
    return path


def reverse_image_lookup(image_path, title, artist, subject=None, location=None,
                        date=None, style=None, medium=None):
    """Perform reverse image lookup with provided parameters.

    Args:
        image_path: Path to the image file
        title: Title of the artwork
        artist: Artist of the artwork
        subject: Subject of the artwork (optional)
        location: Current location of artwork (optional)
        date: Date when artwork was created (optional)
        style: Style of the artwork (optional)
        medium: Medium of the artwork (optional)
        source_url: Source URL of the image (optional)

    Returns:
        tuple: (list of qualifying URLs, delete_url from imgbb)
    """

    image_url, delete_url = upload_to_imgbb(image_path)
    qualifying_urls = reverse_image_lookup_url(image_url,title, artist,subject, location, date,style, medium )
    return qualifying_urls, delete_url


def reverse_image_lookup_url(image_url, title, artist, subject=None, location=None,
                            date=None, style=None, medium=None):
    """Perform reverse image lookup with provided parameters using a direct image URL.

    Args:
        image_url: URL of the image file
        title: Title of the artwork
        artist: Artist of the artwork
        subject: Subject of the artwork (optional)
        location: Current location of artwork (optional)
        date: Date when artwork was created (optional)
        style: Style of the artwork (optional)
        medium: Medium of the artwork (optional)

    Returns:
        tuple: (list of qualifying URLs, None since no imgbb upload was done)
    """

    metadata_text = ", ".join(filter(None, [
        title, artist, subject, location, date, style, medium,
        clean_filename_text(image_url)
    ]))

    qualifying_urls = reverse_image_search(image_url, metadata_text)
    return qualifying_urls


def main():
    parser = argparse.ArgumentParser(description='Perform reverse image search using SerpAPI')
    parser.add_argument(
        "--image", required=True, type=validate_image_path, help="Path to the image file"
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

    source_url = None
    # Check for corresponding url.txt file if no source_url provided
    url_file = os.path.splitext(args.image)[0] + '.url.txt'
    if os.path.exists(url_file):
        with open(url_file, 'r') as f:
            source_url = f.read().strip()
            print(f"Found source URL: {source_url}", file=sys.stderr)

    qualifying_urls = []
    delete_url = None
    if source_url:
        qualifying_urls = reverse_image_lookup_url(
            image_url=source_url,
            title=args.title,
            artist=args.artist,
            subject=args.subject,
            location=args.location,
            date=args.date,
            style=args.style,
            medium=args.medium
        )
    else:
        qualifying_urls, delete_url = reverse_image_lookup(
            image_path=args.image_file,
            title=args.title,
            artist=args.artist,
            subject=args.subject,
            location=args.location,
            date=args.date,
            style=args.style,
            medium=args.medium
        )

    if qualifying_urls:
        print("\nQualifying URLs (sorted by score):")
        for url, score in qualifying_urls:
            print(f"{url} (score: {score:.3f})")
    else:
        print("No qualifying URLs found")

    if delete_url:
        print(f"\nTry deleting {delete_url} in a browser.", file=sys.stderr)

    sys.exit(0)


if __name__ == '__main__':
    main()
