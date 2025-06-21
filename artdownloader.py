#!/usr/bin/env python
"""Download artwork images from various sources.

This script searches for artwork images from multiple sources including:
- DuckDuckGo
- Wikimedia Commons
"""

import os
import sys
import time
from io import BytesIO

from PIL import Image
import requests
import random
from duckduckgo_search import DDGS

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries(
    retries=5,
    backoff_factor=1,
    status_forcelist=(408, 429, 500, 502, 503, 504),
    session=None
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        raise_on_status=False,  # Important if you want to handle it yourself
        respect_retry_after_header=True,
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def exponential_backoff_with_jitter(base=1.0, cap=60.0, attempt=1):
    backoff = min(cap, base * (2 ** attempt))
    jitter = random.uniform(0, backoff)
    return jitter

# Constants
SAVE_DIR = "downloads"
WIKIMEDIA_SEARCH_API_URL = (
    "https://api.wikimedia.org/core/v1/commons/search/page"
)
WIKIMEDIA_FILE_API_URL = "https://api.wikimedia.org/core/v1/commons/file"


def save_image(url, filename):
    """Save an image from URL to local file.

    Args:
        url: Image URL to download
        filename: Local filename to save to

    Returns:
        bool: True if download succeeded, False otherwise
    """
    try:
        session = create_session_with_retries()
        headers = {
    "User-Agent": "Mozilla/5.0 (compatible; ImageDownloaderBot/1.0; +https://github.com/linusjf/RIAY/bot-info)"
}
        attempt = 0
        while attempt < 5:
            response = session.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
                # Save URL to companion file
                url_filename = os.path.splitext(filename)[0] + ".url"
                with open(url_filename, "w") as url_file:
                    url_file.write(url)
                print(f"✅ Saved: {filename} (source URL saved to {url_filename})")
                return True
            elif response.status_code in {408, 429, 500, 502, 503, 504}:
                wait = exponential_backoff_with_jitter(base=2, cap=60, attempt=attempt)
                print(f"⚠️ Retry {attempt+1}: HTTP {response.status_code}, waiting {wait:.2f}s...")
                time.sleep(wait)
                attempt += 1
            else:
                print(f"❌ Failed with status: {response.status_code}")
                break
        print("❗ Download failed after retries.")
        print(f"❌ Failed to download: {url}")
    except Exception as error:
        print(f"❌ Error: {error}")
    return False


def download_from_duckduckgo(query):
    """Download image from DuckDuckGo search.

    Args:
        query: Search query string

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 DuckDuckGo search for: {query}")
    with DDGS() as ddgs:
        results = ddgs.images(keywords=query, max_results=10)
        if not results:
            return False
        for image in results:
            url = image["image"]
            filename = os.path.join(
                SAVE_DIR,
                f"{query.replace(' ', '_')}_duckduckgo.jpg"
            )
            if save_image(url, filename):
                return True
    return False


def download_from_wikimedia(query):
    """Download image from Wikimedia Commons.

    Args:
        query: Search query string

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 Wikimedia Commons search for: {query}")
    params = {"q": query}
    response = requests.get(
        WIKIMEDIA_SEARCH_API_URL,
        params=params
    ).json()
    pages = response.get("pages", [])
    for page in pages:
        file = page.get("key")
        if not file:
            continue
        file_response = requests.get(
            WIKIMEDIA_FILE_API_URL + "/" + file,
            headers={'User-Agent': 'Mozilla/5.0'}
        ).json()
        original = file_response.get("original")
        if original and "url" in original:
            image_url = original.get("url")
            if image_url.lower().endswith(('.jpg', '.jpeg')):
                safe_query = "".join(
                    c if c.isalnum() or c in "_-" else "_" for c in query
                )
                filename = os.path.join(
                    SAVE_DIR,
                    f"{safe_query}_wikimedia.jpg"
                )
                if save_image(image_url, filename):
                    return True
    return False


def download_all(query):
    """Download images from all available sources.

    Args:
        query: Search query string
    """
    download_from_duckduckgo(query)
    download_from_wikimedia(query)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python artdownloader.py <artwork_name>")
        sys.exit(1)

    os.makedirs(SAVE_DIR, exist_ok=True)
    art_title = " ".join(sys.argv[1:])
    download_all(art_title)


if __name__ == "__main__":
    main()
