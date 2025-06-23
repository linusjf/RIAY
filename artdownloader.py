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
import re
import argparse
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

def parse_bash_array(file_path, var_name):
    with open(file_path, 'r') as f:
        content = f.read()

    # Match array definition like: VAR=( "a" "b" "c" )
    pattern = re.compile(rf'{var_name}\s*=\s*\((.*?)\)', re.DOTALL)
    match = pattern.search(content)
    if not match:
        return []

    array_body = match.group(1)
    # Extract all quoted strings
    values = re.findall(r'"(.*?)"', array_body)
    return values

STOCK_PHOTO_SITES = parse_bash_array('config.env', 'STOCK_PHOTO_SITES')
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
            if not any(val.lower() in url.lower() for val in STOCK_PHOTO_SITES):
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
            if url.lower().endswith(('.jpg', '.jpeg')) and not any(val.lower() in url.lower() for val in STOCK_PHOTO_SITES):
                filename = os.path.join(
                    SAVE_DIR,
                    f"{filename_base}_google.jpg"
                )
                if save_image(url, filename):
                    return True

    except Exception as error:
        print(f"❌ Error: {error}")
    return False

def download_all(query, filename_base=None, title=None, artist=None, year=None, medium=None, subject=None):
    """Download images from all available sources.

    Args:
        query: Search query string
        filename_base: Optional base filename to use for saving
        title: Artwork title
        artist: Artist name
        year: Creation year
        medium: Art medium
        subject: Art subject

    Returns:
        bool: True if any download succeeded, False otherwise
    """
    if filename_base is None:
        filename_base = query.replace(' ', '_')

    # Build enhanced query with additional metadata
    enhanced_query = query
    if artist:
        enhanced_query += f" by {artist}"
    if title and title not in query:
        enhanced_query += f" {title}"
    if year:
        enhanced_query += f" {year}"
    if medium:
        enhanced_query += f" {medium}"
    if subject:
        enhanced_query += f" {subject}"

    # Wikimedia-specific query (only title and artist)
    wikimedia_query = query
    if artist:
        wikimedia_query += f" by {artist}"
    if title and title not in query:
        wikimedia_query += f" {title}"

    print(f"\n🔍 Searching with enhanced query: {enhanced_query}")

    downloaded_duckduckgo = download_from_duckduckgo(enhanced_query, filename_base)
    downloaded_wikimedia = download_from_wikimedia(wikimedia_query, filename_base)
    downloaded_wikimedia_search = download_from_wikimedia_search(wikimedia_query, filename_base)
    downloaded_google = download_from_google(enhanced_query, filename_base)
    return (downloaded_duckduckgo or downloaded_wikimedia or downloaded_wikimedia_search or downloaded_google)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Download artwork images from various sources.')
    parser.add_argument('query', nargs='?', help='Name of artwork to search for')
    parser.add_argument('--title', help='Title of the artwork')
    parser.add_argument('--artist', help='Artist name')
    parser.add_argument('--year', help='Year of creation')
    parser.add_argument('--medium', help='Art medium (e.g., oil painting, sculpture)')
    parser.add_argument('--subject', help='Art subject matter')
    parser.add_argument('--filename', help='Base filename for saved images (without extension)')

    args = parser.parse_args()

    if not args.query and not any([args.title, args.artist, args.year, args.medium, args.subject]):
        parser.print_help()
        sys.exit(1)

    os.makedirs(SAVE_DIR, exist_ok=True)

    query = args.query if args.query else ""
    if args.title and args.title not in query:
        query = f"{query} {args.title}".strip()

    success = download_all(
        query=query,
        filename_base=args.filename,
        title=args.title,
        artist=args.artist,
        year=args.year,
        medium=args.medium,
        subject=args.subject
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
