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
import subprocess
from io import BytesIO

import requests
from dotenv import load_dotenv
from PIL import Image
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from serpapi import GoogleSearch

# Global list to track downloaded URLs
DOWNLOADED_URLS = []

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

SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.webp', '.avif', '.svg')

def convert_to_jpeg(input_path):
    """Convert image to JPEG using GraphicsMagick.
    
    Args:
        input_path: Path to input image file
        
    Returns:
        str: Path to converted JPEG file or None if conversion failed
    """
    try:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.jpg"
        
        # Check if GraphicsMagick is available
        if subprocess.run(["gm", "version"], capture_output=True).returncode != 0:
            print("⚠️ GraphicsMagick (gm) not found, skipping conversion")
            return None
            
        result = subprocess.run(
            ["gm", "convert", input_path, output_path],
            capture_output=True
        )
        
        if result.returncode == 0:
            print(f"✅ Converted to JPEG: {output_path}")
            # Remove original file if conversion succeeded
            os.remove(input_path)
            return output_path
        else:
            print(f"❌ Conversion failed: {result.stderr.decode().strip()}")
            return None
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return None

def create_session_with_retries(
    retries=5,
    backoff_factor=1,
    status_forcelist=(403,408, 429, 500, 502, 503, 504),
    session=None
):
    """Create a requests session with retry logic."""
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
    """Calculate exponential backoff with jitter."""
    backoff = min(cap, base * (2 ** attempt))
    jitter = random.uniform(0, backoff)
    return jitter

def save_image(url, filename):
    """Save an image from URL to local file."""
    if url in DOWNLOADED_URLS:
        print(f"⏩ Skipping already downloaded URL: {url}")
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
                url_filename = os.path.splitext(temp_filename)[0] + ".url"
                with open(url_filename, "w") as url_file:
                    url_file.write(url)
                DOWNLOADED_URLS.append(url)

                # Convert to JPEG if not already
                if ext.lower() not in ('.jpg', '.jpeg'):
                    jpeg_path = convert_to_jpeg(temp_filename)
                    if jpeg_path:
                        print(f"✅ Saved: {jpeg_path} (source URL saved to {url_filename})")
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

# [Rest of the file remains exactly the same from the original, starting from @retry decorator...]
