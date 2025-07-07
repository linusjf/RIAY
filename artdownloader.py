#!/usr/bin/env python
"""Download artwork images from various sources.

This script searches for artwork images from multiple sources including:
- DuckDuckGo
- Wikimedia Commons
- Google
"""

import os
import sys
import time
import argparse
import shutil

import requests
import re
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from serpapi import GoogleSearch
from bashhelper import parse_bash_array
from htmlhelper import strip_span_tags_but_keep_contents, clean_filename_text
from converterhelper import convert_to_jpeg
from sessionhelper import create_session_with_retries, exponential_backoff_with_jitter
from simtools import compare_terms, MatchMode

# Global dictionary to track downloaded URLs and their saved filenames
DOWNLOADED_URLS = {}
# Global list to track found stock photo URLs
FOUND_STOCK_PHOTOS = []
# Global list to track Wikipedia images and their scores
WIKIPEDIA_IMAGES = []
# Global list to track Google search results (url, file, score)
GOOGLE_IMAGES = []
# Global list to track DuckDuckGo search results (url, file, score)
DUCKDUCKGO_IMAGES = []

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

SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.webp', '.avif', '.svg')

def save_image(url, filename):
    """Save an image from URL to local file."""
    if url in DOWNLOADED_URLS:
        print(f"⏩ URL already downloaded: {url}", file=sys.stderr)
        existing_file = DOWNLOADED_URLS[url]
        try:
            # Copy the existing file to new filename
            shutil.copy2(existing_file, filename)
            # Copy the URL file as well
            existing_url_file = os.path.splitext(existing_file)[0] + ".url.txt"
            new_url_file = os.path.splitext(filename)[0] + ".url.txt"
            if os.path.exists(existing_url_file):
                shutil.copy2(existing_url_file, new_url_file)
            print(f"✅ Copied existing file: {existing_file} -> {filename}", file=sys.stderr)
            DOWNLOADED_URLS[url] = filename
            return True
        except Exception as e:
            print(f"❌ Error copying existing file: {e}", file=sys.stderr)
            return False

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
                # Get file extension from URL or content type
                ext = os.path.splitext(url)[1].lower()
                if not ext or ext not in SUPPORTED_FORMATS:
                    content_type = response.headers.get('content-type', '')
                    if 'image/png' in content_type:
                        ext = '.png'
                    elif 'image/webp' in content_type:
                        ext = '.webp'
                    elif 'image/svg+xml' in content_type:
                        ext = '.svg'
                    elif 'image/avif' in content_type:
                        ext = '.avif'
                    else:
                        ext = '.jpg'

                # Save with original extension first
                temp_filename = os.path.splitext(filename)[0] + ext
                with open(temp_filename, "wb") as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)

                # Save URL to companion file
                url_filename = os.path.splitext(temp_filename)[0] + ".url.txt"
                with open(url_filename, "w") as url_file:
                    url_file.write(url)
                DOWNLOADED_URLS[url] = temp_filename

                # Convert to JPEG if not already
                if ext.lower() not in ('.jpg', '.jpeg'):
                    jpeg_path = convert_to_jpeg(temp_filename)
                    if jpeg_path:
                        print(f"✅ Saved: {jpeg_path} (source URL saved to {url_filename})", file=sys.stderr)
                        DOWNLOADED_URLS[url] = jpeg_path
                        return True
                    else:
                        print(f"⚠️ Saved original format: {temp_filename}", file=sys.stderr)
                        return True
                else:
                    print(f"✅ Saved: {temp_filename} (source URL saved to {url_filename})", file=sys.stderr)
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
                print(f"❌ Failed with status: {response.status_code}", file=sys.stderr)
                break
        print("❗ Download failed after retries.", file=sys.stderr)
        print(f"❌ Failed to download: {url}", file=sys.stderr)
    except Exception as error:
        print(f"❌ Error: {error}", file=sys.stderr)
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
            print("❌ No matching images found.",file=sys.stderr)
            return False
        qualifying_results = []
        for image in results[0:5]:
            url = image["image"]
            title = image["title"]
            image_meta_data = " ".join([title, clean_filename_text(url)])
            score = compare_terms(query.lower(), image_meta_data.lower(), MatchMode.COSINE)
            if score >= 0.7:
                qualifying_results.append((image, score))

        if not qualifying_results:
            print("❌ No qualifying results found (score >= 50.0)", file=sys.stderr)
            return False

        success = False
        for idx, (result, score) in enumerate(qualifying_results):
            url = result["image"]
            if any(val.lower() in url.lower() for val in STOCK_PHOTO_SITES):
                FOUND_STOCK_PHOTOS.append(url)
                DUCKDUCKGO_IMAGES.append((url, "", score))
                continue
            filename = os.path.join(
                  SAVE_DIR,
                f"{filename_base}_{idx+1}_duckduckgo.jpg"
            )
            if save_image(url, filename):
                DUCKDUCKGO_IMAGES.append((url, filename, score))
                success = True

        return success

    except Exception as error:
        print(f"❌ Error: {error}", file=sys.stderr)
    return False

def download_from_wikimedia_search(query,detailed_query, filename_base, source="wikimedia_search"):
    """
    Search Wikimedia Commons for an image by query and download the top result.

    Args:
        query (str): Search term (e.g., 'Mona Lisa')
        detailed_query (str): Detailed search terms
        filename_base (str): Base name for saving the file
        source (str): search source

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 Searching Wikimedia for: {query}", file=sys.stderr)
    search_endpoint = "https://commons.wikimedia.org/w/api.php"
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,  # File namespace only
        "srlimit": 5,
        "srprop": "size|wordcount|timestamp|snippet|titlesnippet"
    }

    try:
        resp = requests.get(search_endpoint, params=search_params, timeout=30)
        resp.raise_for_status()
        search_data = resp.json()
        search_results = search_data.get("query", {}).get("search", [])

        if not search_results:
            print("❌ No matching images found.", file=sys.stderr)
            return False

        qualifying_results = []
        for result in search_results:
            title = result["title"]
            titlesnippet = strip_span_tags_but_keep_contents(result["titlesnippet"])
            snippet = strip_span_tags_but_keep_contents(result["snippet"])
            result_meta_data = " ".join([title, titlesnippet, snippet])
            score = compare_terms(detailed_query.lower(), result_meta_data.lower(), MatchMode.HYBRID)
            if score >= 50.0:
                qualifying_results.append((result, score))

        if not qualifying_results:
            print("❌ No qualifying results found (score >= 50.0)", file=sys.stderr)
            return False

        success = False
        for idx, (result, score) in enumerate(qualifying_results):
            selected_title = result["title"]
            print(f"Selected title {selected_title} with score: {score}", file=sys.stderr)

            # Get image info
            info_params = {
                "action": "query",
                "titles": selected_title,
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
                        unique_filename = f"{filename_base}_{idx+1}_{source}"
                        filename = os.path.join(SAVE_DIR, f"{unique_filename}.jpg")
                        if save_image(image_url, filename):
                            WIKIPEDIA_IMAGES.append((filename, score))
                            success = True

        return success

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return False

def download_image_from_wikipedia_article(query, detailed_query, filename_base):
    """Download the first usable image from a Wikipedia article (full API pipeline).

    Args:
        query: Search query string (Wikipedia article title)
        detailed_query: longer detailed query
        filename_base: Base filename to use for saving

    Returns:
        bool: True if any download succeeded, False otherwise
    """
    print(f"\n🔍 Fetching all images from Wikipedia article: {query}", file=sys.stderr)
    try:
        # Step 1: Get the first n pages that fits the query
        params = {
            "limit": 5,
            "q": query
        }
        response = requests.get("https://api.wikimedia.org/core/v1/wikipedia/en/search/page", params=params)
        image_data = response.json()

        pages = image_data.get("pages", [])
        qualifying_pages = []

        for idx, page in enumerate(pages):
            key = page.get("key", "")
            title = page.get("title", "")
            excerpt = strip_span_tags_but_keep_contents(page.get("excerpt", ""))
            description = page.get("description", "")
            page_meta_data = " ".join([key, title, excerpt, description])
            score = compare_terms(detailed_query.lower(), page_meta_data.lower(), MatchMode.HYBRID)

            if score >= 50.0:
                print(f"✅ Qualified page {idx+1}: {title} (score: {score:.3f})", file=sys.stderr)
                qualifying_pages.append((title, score))
            else:
                print(f"❌ Excluded page {idx+1}: {title} (score: {score:.3f})")

        if not qualifying_pages:
            print("❌ No qualifying pages found (score >= 50.0)", file=sys.stderr)
            return False

        # Download images for all qualifying pages
        success = False
        for idx, (title, score) in enumerate(qualifying_pages):
            print(f"\n📥 Downloading image for qualified page {idx+1}: {title}", file=sys.stderr)
            unique_filename = f"{filename_base}_{idx+1}"
            if download_from_wikimedia_search(title, detailed_query, unique_filename, "wikipedia"):
                success = True

        return success

    except Exception as error:
        print(f"❌ Error: {error}", file=sys.stderr)
        return False

def download_from_wikimedia(query, enhanced_query, filename_base):
    """Download image from Wikimedia Commons.

    Args:
        query: Search query string
        filename_base: Base filename to use for saving

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 Wikimedia Commons search for: {query}", file=sys.stderr)
    params = {"q": query}
    try:
        response = requests.get(
            WIKIMEDIA_SEARCH_API_URL,
            params=params
        ).json()
        pages = response.get("pages", [])
        qualifying_pages = []
        if not pages:
            print("❌ No matching images found.", file=sys.stderr)
            return False
        for idx, page in enumerate(pages[0:5]):
            file = page.get("key")
            key = page.get("key", "")
            title = page.get("title", "")
            excerpt = strip_span_tags_but_keep_contents(page.get("excerpt", ""))
            description = page.get("description", "")
            page_meta_data = " ".join(str(p) for p in [key, title, excerpt, description] if p is not None)
            score = compare_terms(enhanced_query.lower(), page_meta_data.lower(), MatchMode.HYBRID)

            if score >= 50.0:
                print(f"✅ Qualified file {idx+1}: {file} (score: {score:.3f})", file=sys.stderr)
                qualifying_pages.append((file, score))
            else:
                print(f"❌ Excluded file {idx+1}: {file} (score: {score:.3f})", file=sys.stderr)

        if not qualifying_pages:
            print("❌ No qualifying files found (score >= 50.0)", file=sys.stderr)
            return False

        # Download images for all qualifying pages
        success = False
        for idx, (file, score) in enumerate(qualifying_pages):
            print(f"\n📥 Downloading image for qualified file {idx+1}: {file}", file=sys.stderr)
            unique_filename = f"{filename_base}_{idx+1}"
            file_response = requests.get(
                WIKIMEDIA_FILE_API_URL + "/" + file,
                headers={'User-Agent': 'Mozilla/5.0'}
            ).json()
            original = file_response.get("original")
            if original and "url" in original:
                image_url = original.get("url")
                filename = os.path.join(
                        SAVE_DIR,
                        f"{unique_filename}_wikimedia.jpg"
                )
                if save_image(image_url, filename):
                    WIKIPEDIA_IMAGES.append((filename, score))
                    success = True

        return success

    except Exception as error:
        print(f"❌ Error: {error}", file=sys.stderr)

    return False

def download_from_google(query, filename_base):
    """Download image from Google Images via SerpAPI.

    Args:
        query: Search query string
        filename_base: Base filename to use for saving

    Returns:
        bool: True if download succeeded, False otherwise
    """
    print(f"\n🔍 Google search for: {query}", file=sys.stderr)
    try:
        params = {
            "q": query,
            "tbm": "isch",
            "api_key": SERPAPI_API_KEY,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        if not results:
            print("❌ No matching images found.", file=sys.stderr)
            return False
        images = results.get("images_results", [])
        if not images:
            return False

        qualifying_pages = []
        for idx, image in enumerate(images[0:5]):
            title = image.get("title")
            url = image.get("original")
            if not url:
                continue
            image_meta_data = " ".join(str(p) for p in [title, clean_filename_text(url)] if p is not None)
            score = compare_terms(query.lower(), image_meta_data.lower(), MatchMode.COSINE)

            if score >= 0.7:
                print(f"✅ Qualified image {idx+1}: {url} (score: {score:.3f})", file=sys.stderr)
                qualifying_pages.append((url, score))
            else:
                print(f"❌ Excluded file {idx+1}: {url} (score: {score:.3f})", file=sys.stderr)

        if not qualifying_pages:
            print("❌ No qualifying images found (score >= 50.0)", file=sys.stderr)
            return False

        # Download images for all qualifying pages
        success = False
        for idx, (url, score) in enumerate(qualifying_pages):
            if any(val.lower() in url.lower() for val in STOCK_PHOTO_SITES):
                FOUND_STOCK_PHOTOS.append(url)
                GOOGLE_IMAGES.append((url, "", score))
                continue
            print(f"\n📥 Downloading image for qualified image {idx+1}: {url}", file=sys.stderr)
            unique_filename = f"{filename_base}_{idx+1}"
            filename = os.path.join(
                SAVE_DIR,
                f"{unique_filename}_google.jpg"
            )
            if save_image(url, filename):
                GOOGLE_IMAGES.append((url, filename, score))
                success = True

        return success

    except Exception as error:
        print(f"❌ Error: {error}", file=sys.stderr)
    return False

def download_all(query, filename_base=None, title=None, artist=None, location=None, date=None, style=None, medium=None, subject=None):
    """Download images from all available sources.

    Args:
        query: Search query string
        filename_base: Optional base filename to use for saving
        title: Artwork title
        artist: Artist name
        location: current location of artwork
        date: Year , decade or century of creation
        style: Artistic style
        medium: Art medium
        subject: Art subject

    Returns:
        bool: True if any download succeeded, False otherwise
    """
    if filename_base is None:
        filename_base = query.replace(' ', '_')

    # Build enhanced query with additional metadata
    enhanced_query = query
    if artist and artist not in query:
        enhanced_query += f" by {artist}"
    if title and title not in query:
        enhanced_query += f" {title}"
    if location:
        enhanced_query += f" {location}"
    if date:
        enhanced_query += f" {date}"
    if style:
        enhanced_query += f" {style}"
    if medium:
        enhanced_query += f" {medium}"
    if subject:
        enhanced_query += f" {subject}"

    # Wikimedia-specific query (only title, artist, date and location)
    wikimedia_query = query
    if artist and artist not in query:
        wikimedia_query += f" by {artist}"
    if title and title not in query:
        wikimedia_query += f" {title}"
    if date and date not in query:
        wikimedia_query += f" {date}"
    if location and location not in query:
        wikimedia_query += f" {location}"

    print(f"\n🔍 Searching wikis with simple query: {wikimedia_query}", file=sys.stderr)

    downloaded_wikipedia_search = download_image_from_wikipedia_article(wikimedia_query, enhanced_query, filename_base)
    downloaded_wikimedia_search = download_from_wikimedia_search(wikimedia_query, enhanced_query, filename_base)
    downloaded_wikimedia = download_from_wikimedia(wikimedia_query, enhanced_query, filename_base)

    print(f"\n🔍 Searching google and duckduckgo with enhanced query: {enhanced_query}", file=sys.stderr)

    downloaded_duckduckgo = download_from_duckduckgo(enhanced_query, filename_base)
    downloaded_google = download_from_google(enhanced_query, filename_base)
    return (downloaded_duckduckgo or downloaded_wikipedia_search or downloaded_wikimedia or downloaded_wikimedia_search or downloaded_google)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Download artwork images from various sources.')
    parser.add_argument('query', nargs='?', help='Name of artwork to search for')
    parser.add_argument('--title', help='Title of the artwork')
    parser.add_argument('--artist', help='Artist name')
    parser.add_argument('--location', help='current location of artwork')
    parser.add_argument('--date', help='the year and/or century of creation')
    parser.add_argument('--style', help='the artistic style')
    parser.add_argument('--medium', help='Art medium (e.g., oil painting, sculpture)')
    parser.add_argument('--subject', help='Art subject matter')
    parser.add_argument('--filename', help='Base filename for saved images (without extension)')

    args = parser.parse_args()

    if not args.query and not any([args.title, args.artist, args.location, args.style, args.medium, args.subject]):
        parser.print_help()
        sys.exit(1)

    os.makedirs(SAVE_DIR, exist_ok=True)

    query = args.query if args.query else ""
    if args.title and args.title not in query:
        query = f"{query} {args.title}".strip()
    if args.artist and args.artist not in query:
        query = f"{query} {args.artist}".strip()

    success = download_all(
        query=query,
        filename_base=args.filename,
        title=args.title,
        artist=args.artist,
        location=args.location,
        date=args.date,
        style=args.style,
        medium=args.medium,
        subject=args.subject
    )

    print("\nDownloaded images: ")
    for v in DOWNLOADED_URLS.values():
        print(v)

    if FOUND_STOCK_PHOTOS:
        print("\nFound stock photos (not downloaded):")
        for url in FOUND_STOCK_PHOTOS:
            print(url)

    if WIKIPEDIA_IMAGES:
        print("\nWikipedia images with scores:")
        for filepath, score in WIKIPEDIA_IMAGES:
            print(f"{filepath} (score: {score:.3f})")

        # Find and print the best Wikipedia image
        best_wikipedia = max(WIKIPEDIA_IMAGES, key=lambda x: x[1], default=None)
        if best_wikipedia:
            print(f"\n⭐ Best Wikipedia image: {best_wikipedia[0]} (score: {best_wikipedia[1]:.3f})")

    if not WIKIPEDIA_IMAGES:
        # Combine all search results
        all_results = DUCKDUCKGO_IMAGES + GOOGLE_IMAGES
        if all_results:
            print("\nAll search results (url, file, score):")
            for url, file, score in all_results:
                print(f"{url} -> {file} (score: {score:.3f})")

            # Find the best result (highest score)
            best_result = max(all_results, key=lambda x: x[2], default=None)
            if best_result:
                url, file, score = best_result
                # If we have a URL but no file, download it now
                if url and not file:
                    filename = os.path.join(SAVE_DIR, f"best_result_{query.replace(' ', '_')}.jpg")
                    if save_image(url, filename):
                        print(f"✅ Downloaded best result: {filename}")
                        file = filename
                print(f"\n⭐ Best available image (downloaded): {file} (score: {score:.3f})")


    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
