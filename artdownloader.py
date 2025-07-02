#!/usr/bin/env python
"""Download artwork images from various sources.

This script searches for artwork images from multiple sources including:
- DuckDuckGo
- Wikimedia Commons
- Google
"""

import os
import random
import sys
import time
import re
import argparse
import subprocess
from io import BytesIO
import shutil

import requests
from dotenv import load_dotenv
from PIL import Image
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from serpapi import GoogleSearch
from fuzzywuzzy import fuzz
from bashhelper import parse_bash_array
from htmlhelper import strip_span_tags_but_keep_contents
from converterhelper import convert_to_jpeg
from sessionhelper import create_session_with_retries, exponential_backoff_with_jitter

# Global dictionary to track downloaded URLs and their saved filenames
DOWNLOADED_URLS = {}

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
        print(f"⏩ URL already downloaded: {url}")
        existing_file = DOWNLOADED_URLS[url]
        try:
            # Copy the existing file to new filename
            shutil.copy2(existing_file, filename)
            # Copy the URL file as well
            existing_url_file = os.path.splitext(existing_file)[0] + ".url.txt"
            new_url_file = os.path.splitext(filename)[0] + ".url.txt"
            if os.path.exists(existing_url_file):
                shutil.copy2(existing_url_file, new_url_file)
            print(f"✅ Copied existing file: {existing_file} -> {filename}")
            DOWNLOADED_URLS[url] = filename
            return True
        except Exception as e:
            print(f"❌ Error copying existing file: {e}")
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
                        print(f"✅ Saved: {jpeg_path} (source URL saved to {url_filename})")
                        DOWNLOADED_URLS[url] = jpeg_path
                        return True
                    else:
                        print(f"⚠️ Saved original format: {temp_filename}")
                        return True
                else:
                    print(f"✅ Saved: {temp_filename} (source URL saved to {url_filename})")
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

[... rest of artdownloader.py remains exactly the same ...]
