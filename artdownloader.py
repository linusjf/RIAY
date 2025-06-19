#!/usr/bin/env python
"""
Download artwork images from various sources.

This script searches for artwork images from multiple sources including:
- DuckDuckGo
- Wikimedia Commons
- The Met Museum
- Harvard Art Museums

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : artdownloader
# @created     : Thursday Jun 19, 2025 14:03:26 IST
# @description : Artwork image downloader
# -*- coding: utf-8 -*-'
######################################################################
"""
import os
import sys

import requests
from duckduckgo_search import DDGS


# Constants
SAVE_DIR = "downloads"
WIKIMEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
METMUSEUM_SEARCH_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
METMUSEUM_OBJECT_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
HARVARD_API_URL = "https://api.harvardartmuseums.org/object"
HARVARD_API_KEY = os.getenv("HARVARD_ART_MUSEUMS_API_KEY", "")


def save_image(url: str, filename: str) -> bool:
    """Save an image from URL to local file.

    Args:
        url: Image URL to download
        filename: Local filename to save to

    Returns:
        bool: True if download succeeded, False otherwise
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"✅ Saved: {filename}")
            return True
        print(f"❌ Failed to download: {url}")
    except Exception as error:
        print(f"❌ Error: {error}")
    return False


def download_from_duckduckgo(query: str) -> bool:
    """Download image from DuckDuckGo search.

    Args:
        query: Search query string

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 DuckDuckGo search for: {query}")
    with DDGS() as ddgs:
        results = ddgs.images(query, max_results=1)
        results = iter(results)
        image = next(results, None)
        if image:
            url = image["image"]
            filename = os.path.join(
                SAVE_DIR,
                f"{query.replace(' ', '_')}_duckduckgo.jpg"
            )
            return save_image(url, filename)
    return False


def download_from_wikimedia(query: str) -> bool:
    """Download image from Wikimedia Commons.

    Args:
        query: Search query string

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 Wikimedia Commons search for: {query}")
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "titles": query
    }
    response = requests.get(WIKIMEDIA_API_URL, params=params).json()
    pages = response.get("query", {}).get("pages", {})
    for page in pages.values():
        image_url = page.get("original", {}).get("source")
        if image_url:
            filename = os.path.join(
                SAVE_DIR,
                f"{query.replace(' ', '_')}_wikimedia.jpg"
            )
            return save_image(image_url, filename)
    return False


def download_from_metmuseum(query: str) -> bool:
    """Download image from The Met Museum.

    Args:
        query: Search query string

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 The Met Museum search for: {query}")
    params = {"q": query, "hasImages": "true"}
    response = requests.get(METMUSEUM_SEARCH_URL, params=params).json()
    object_ids = response.get("objectIDs", [])
    if object_ids:
        object_url = f"{METMUSEUM_OBJECT_URL}/{object_ids[0]}"
        data = requests.get(object_url).json()
        img_url = data.get("primaryImage")
        if img_url:
            filename = os.path.join(
                SAVE_DIR,
                f"{query.replace(' ', '_')}_met.jpg"
            )
            return save_image(img_url, filename)
    return False


def download_from_harvard(query: str, api_key: str = HARVARD_API_KEY) -> bool:
    """Download image from Harvard Art Museums.

    Args:
        query: Search query string
        api_key: API key for Harvard Art Museums (default: DEMO_API_KEY)

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 Harvard Art Museums search for: {query}")
    params = {
        "apikey": api_key,
        "q": query,
        "hasimage": 1,
        "size": 1
    }
    response = requests.get(HARVARD_API_URL, params=params)
    response = response.json()
    records = response.get("records", [])
    if records and "primaryimageurl" in records[0]:
        img_url = records[0]["primaryimageurl"]
        filename = os.path.join(
            SAVE_DIR,
            f"{query.replace(' ', '_')}_harvard.jpg"
        )
        return save_image(img_url, filename)
    return False


def download_all(query: str) -> None:
    """Download images from all available sources.

    Args:
        query: Search query string
    """
    download_from_duckduckgo(query)
    download_from_wikimedia(query)
    download_from_metmuseum(query)
    download_from_harvard(query)


def main() -> None:
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python artdownloader.py <artwork_name>")
        sys.exit(1)

    os.makedirs(SAVE_DIR, exist_ok=True)
    art_title = " ".join(sys.argv[1:])
    download_all(art_title)


if __name__ == "__main__":
    main()
