#!/usr/bin/env python
"""Download artwork images from various sources.

This script searches for artwork images from multiple sources including:
- DuckDuckGo
- Wikimedia Commons
"""

import os
import random
import sys
import time
from io import BytesIO

import requests
from dotenv import load_dotenv
from PIL import Image
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from serpapi import BingSearch, GoogleSearch

# Replace with your own API key


# Load environment variables from config.env
load_dotenv('config.env')

# Constants
SAVE_DIR = os.getenv('ART_DOWNLOADER_DIR', 'artdownloads')
SERPAPI_API_KEY = os.getenv("SERP_API_KEY", "")

WIKIMEDIA_SEARCH_API_URL = (
    "https://api.wikimedia.org/core/v1/commons/search/page"
)
WIKIMEDIA_FILE_API_URL = "https://api.wikimedia.org/core/v1/commons/file"


def create_session_with_retries(
    retries=5,
    backoff_factor=1,
    status_forcelist=(403,408, 429, 500, 502, 503, 504),
    session=None
):
    """Create a requests session with retry logic.

    Args:
        retries: Maximum number of retries
        backoff_factor: Backoff factor for retries
        status_forcelist: HTTP status codes to force retry on
        session: Existing session to modify (optional)

    Returns:
        requests.Session: Configured session with retry logic
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        raise_on_status=False,
        respect_retry_after_header=True,
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def exponential_backoff_with_jitter(base=1.0, cap=60.0, attempt=1):
    """Calculate exponential backoff with jitter.

    Args:
        base: Base backoff time in seconds
        cap: Maximum backoff time in seconds
        attempt: Current attempt number

    Returns:
        float: Time to wait in seconds
    """
    backoff = min(cap, base * (2 ** attempt))
    jitter = random.uniform(0, backoff)
    return jitter


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
            "User-Agent": (
                "Mozilla/5.0 (compatible; ImageDownloaderBot/1.0; "
                "+https://github.com/linusjf/RIAY/bot-info)"
            )
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
                print(
                    f"⚠️ Retry {attempt + 1}: HTTP {response.status_code}, "
                    f"waiting {wait:.2f}s..."
                )
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

# Retry on rate limit with exponential backoff
@retry(
    retry=retry_if_exception_type(RatelimitException),
    wait=wait_exponential(min=1, max=10),
    stop=stop_after_attempt(5),
)
def search_duckduckgo_images(query, max_results=10):
    with DDGS() as ddgs:
        return ddgs.images(query, max_results=max_results)

def download_from_duckduckgo(query, filename_base):
    """Download image from DuckDuckGo search.

    Args:
        query: Search query string
        filename_base: Base filename to use for saving

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 DuckDuckGo search for: {query}")
    try:
        results = search_duckduckgo_images(query, max_results=10)
        if not results:
            print("❌ No matching images found.")
            return False
        for image in results:
            url = image["image"]
            filename = os.path.join(
                SAVE_DIR,
                f"{filename_base}_duckduckgo.jpg"
            )
            if save_image(url, filename):
                return True
    except Exception as error:
        print(f"❌ Error: {error}")
    return False

def download_from_wikimedia_search(query, filename_base):
    """
    Search Wikimedia Commons for an image by query and download the top result.

    Args:
        query (str): Search term (e.g., 'Mona Lisa')
        filename_base (str): Base name for saving the file

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 Searching Wikimedia for: {query}")
    search_endpoint = "https://commons.wikimedia.org/w/api.php"
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,  # File namespace only
        "srlimit": 10
    }

    try:
        # Step 1: Search
        resp = requests.get(search_endpoint, params=search_params, timeout=30)
        resp.raise_for_status()
        search_data = resp.json()
        search_results = search_data.get("query", {}).get("search", [])

        if not search_results:
            print("❌ No matching images found.")
            return False

        for result in search_results:
            title = result["title"]
            if title.lower().endswith(('.jpg', '.jpeg')):
                # Step 2: Get image info
                info_params = {
                    "action": "query",
                    "titles": title,
                    "prop": "imageinfo",
                    "iiprop": "url",
                    "format": "json"
                }

                info_resp = requests.get(search_endpoint, params=info_params, timeout=10)
                info_resp.raise_for_status()
                info_data = info_resp.json()
                pages = info_data.get("query", {}).get("pages", {})

                for page in pages.values():
                    imageinfo = page.get("imageinfo")
                    if imageinfo:
                        image_url = imageinfo[0].get("url")
                        if image_url:
                            filename = os.path.join(SAVE_DIR, f"{filename_base}_wikimedia_search.jpg")
                            return save_image(image_url, filename)

    except Exception as e:
        print(f"❌ Error: {e}")

    return False

def download_from_wikimedia(query, filename_base):
    """Download image from Wikimedia Commons.

    Args:
        query: Search query string
        filename_base: Base filename to use for saving

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 Wikimedia Commons search for: {query}")
    params = {"q": query}
    try:
        response = requests.get(
            WIKIMEDIA_SEARCH_API_URL,
            params=params
        ).json()
        pages = response.get("pages", [])
        if not pages:
            print("❌ No matching images found.")
            return False
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
                    filename = os.path.join(
                        SAVE_DIR,
                        f"{filename_base}_wikimedia.jpg"
                    )
                    if save_image(image_url, filename):
                        return True
    except Exception as error:
        print(f"❌ Error: {error}")

    return False

def download_from_google(query, filename_base):
    """Download image from Google Images via SerpAPI.

    Args:
        query: Search query string
        filename_base: Base filename to use for saving

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 Google search for: {query}")
    try:
        params = {
            "q": query,
            "tbm": "isch",
            "api_key": SERPAPI_API_KEY,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        if not results:
            print("❌ No matching images found.")
            return False
        images = results.get("images_results", [])
        if not images:
            return False

        for image in images:
            url = image.get("original")
            if not url:
                continue
            if url.lower().endswith(('.jpg', '.jpeg')):
                filename = os.path.join(
                    SAVE_DIR,
                    f"{filename_base}_google.jpg"
                )
                if save_image(url, filename):
                    return True

    except Exception as error:
        print(f"❌ Error: {error}")
    return False

def download_all(query, filename_base=None):
    """Download images from all available sources.

    Args:
        query: Search query string
        filename_base: Optional base filename to use for saving

    Returns:
        bool: True if any download succeeded, False otherwise
    """
    if filename_base is None:
        filename_base = query.replace(' ', '_')
    downloaded_duckduckgo = download_from_duckduckgo(query, filename_base)
    downloaded_wikimedia = download_from_wikimedia(query, filename_base)
    downloaded_wikimedia_search = download_from_wikimedia_search(query, filename_base)
    downloaded_google = download_from_google(query, filename_base)
    return (downloaded_duckduckgo or downloaded_wikimedia or downloaded_wikimedia_search or downloaded_google)



def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python artdownloader.py <artwork_name> [filename_base]")
        print("  artwork_name: Name of artwork to search for")
        print("  filename_base: Optional base filename for saved images (without extension)")
        sys.exit(1)

    os.makedirs(SAVE_DIR, exist_ok=True)
    if len(sys.argv) > 2:
        art_title = " ".join(sys.argv[1:-1])
        filename_base = sys.argv[-1]
    else:
        art_title = " ".join(sys.argv[1:])
        filename_base = None

    if download_all(art_title, filename_base):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
