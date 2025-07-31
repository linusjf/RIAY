#!/usr/bin/env python
"""Download artwork images from various sources.

This script searches for artwork images from multiple sources including:
- DuckDuckGo
- Wikimedia Commons
- Google
"""

import asyncio
import os
import sys
import time
import argparse
import shutil
from typing import Optional, Dict, List, Tuple, Any, Set

import requests
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from serpapi import GoogleSearch
from htmlhelper import strip_span_tags_but_keep_contents, clean_filename_text, extract_domain_from_url, clean_filename
from converterhelper import convert_to_jpeg
from sessionhelper import create_session_with_retries, exponential_backoff_with_jitter
from simtools import THRESHOLDS, compare_terms, MatchMode
from reverseimagelookup import ReverseImageLookup
from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory
from PIL import Image

class ArtDownloader:
    """Download artwork images from various sources."""

    SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.webp', '.avif', '.svg')
    MAX_ALLOWED_RESULTS = 5
    MAX_WIKI_ALLOWED_RESULTS = 3
    """Initialize the downloader with configuration."""
    config: ConfigEnv = ConfigEnv(include_os_env=True)
    STOCK_PHOTO_SITES: List[str] = config.get(ConfigConstants.STOCK_PHOTO_SITES, [])
    SOCIAL_MEDIA_SITES: List[str] = config.get(ConfigConstants.SOCIAL_MEDIA_SITES, [])
    FIND_ALTERNATE_IMAGES: bool = config.get(ConfigConstants.FIND_ALTERNATE_IMAGES, False)
    SERPAPI_API_KEY: str = config.get(ConfigConstants.SERP_API_KEY, "")
    SAVE_DIR: str = config.get(ConfigConstants.ART_DOWNLOADER_DIR, 'artdownloads')
    MIN_IMAGE_WIDTH: int = config.get(ConfigConstants.MIN_IMAGE_WIDTH, 0)
    MIN_IMAGE_HEIGHT: int = config.get(ConfigConstants.MIN_IMAGE_HEIGHT, 0)
    SEARCH_WIKIPEDIA: bool = config.get(ConfigConstants.SEARCH_WIKIPEDIA, True)
    MAX_RETRIES: int = config.get(ConfigConstants.CURL_MAX_RETRIES, 5)

    def __init__(self, params: Optional[Dict[str, str]] = None) -> None:
        # Initialize artwork metadata fields
        self.title: Optional[str] = None
        self.artist: Optional[str] = None
        self.location: Optional[str] = None
        self.date: Optional[str] = None
        self.style: Optional[str] = None
        self.medium: Optional[str] = None
        self.subject: Optional[str] = None
        self.filename_base: Optional[str] = None

        # Populate from params dictionary if provided
        if params:
            self.title = params.get('title')
            self.artist = params.get('artist')
            self.location = params.get('location')
            self.date = params.get('date')
            self.style = params.get('style')
            self.medium = params.get('medium')
            self.subject = params.get('subject')
            self.filename_base = params.get('filename')

        self.WIKIMEDIA_SEARCH_API_URL: str = "https://api.wikimedia.org/core/v1/commons/search/page"
        self.WIKIMEDIA_FILE_API_URL: str = "https://api.wikimedia.org/core/v1/commons/file"

        # Track downloaded URLs and results
        self.DOWNLOADED_URLS: Dict[str, str] = {}
        self.FOUND_STOCK_PHOTOS: Set[str] = set()
        self.WIKIPEDIA_IMAGES: List[Tuple[str, str, float]] = []
        self.GOOGLE_IMAGES: List[Tuple[str, str, float]] = []
        self.DUCKDUCKGO_IMAGES: List[Tuple[str, str, float]] = []

        # Configure logger
        logging_enabled = self.config.get(ConfigConstants.LOGGING, False)
        self.logger = LoggerFactory.get_logger(
            name=os.path.basename(__file__),
            log_to_file=logging_enabled
        )

        os.makedirs(self.SAVE_DIR, exist_ok=True)

    def _check_image_size(self, url: str) -> bool:
        """Check if image size exceeds PIL.Image.MAX_IMAGE_PIXELS before downloading."""
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (compatible; ImageDownloaderBot/1.0; "
                    "+https://github.com/linusjf/RIAY/bot-info)"
                )
            }
            response = requests.head(url, headers=headers, timeout=10)
            if response.status_code == 200:
                content_length = response.headers.get('content-length')
                if content_length:
                    file_size = int(content_length)
                    # Estimate pixels assuming 3 bytes per pixel for RGB
                    estimated_pixels = file_size // 3
                    if estimated_pixels > Image.MAX_IMAGE_PIXELS:
                        self.logger.warning(f"Image too large (estimated {estimated_pixels} pixels exceeds MAX_IMAGE_PIXELS)")
                        return False
            return True
        except Exception as e:
            self.logger.error(f"Error checking image size: {e}")
            return True  # Continue with download if we can't check size

    def _check_image_dimensions(self, image_path: str) -> bool:
        """Check if image meets minimum dimension requirements."""
        if self.MIN_IMAGE_WIDTH <= 0 and self.MIN_IMAGE_HEIGHT <= 0:
            return True

        try:
            with Image.open(image_path) as img:
                width, height = img.size
                if width >= self.MIN_IMAGE_WIDTH and height >= self.MIN_IMAGE_HEIGHT:
                    return True
                self.logger.warning(f"Image dimensions too small: {width}x{height} (min {self.MIN_IMAGE_WIDTH}x{self.MIN_IMAGE_HEIGHT})")
                return False
        except Exception as e:
            self.logger.error(f"Error checking image dimensions: {e}")
            return False

    def get_extension_from_mime(self, mime_type):
        mapping = {
        'image/png': '.png',
        'image/webp': '.webp',
        'image/svg+xml': '.svg',
        'image/avif': '.avif',
        'image/jpeg': '.jpg'
        }
        return mapping.get(mime_type.split(";")[0].strip(), '.jpg')

    def _copy_existing_download(self, url: str, filename: str) -> bool:
        """Copy an already downloaded file from cache."""
        existing_file = self.DOWNLOADED_URLS[url]
        try:
            shutil.copy2(existing_file, filename)
            existing_url_file = os.path.splitext(existing_file)[0] + ".url.txt"
            new_url_file = os.path.splitext(filename)[0] + ".url.txt"
            if os.path.exists(existing_url_file):
                shutil.copy2(existing_url_file, new_url_file)
            self.logger.info(f"Copied existing file: {existing_file} -> {filename}")
            self.DOWNLOADED_URLS[url] = filename
            return True
        except Exception as e:
            self.logger.error(f"Error copying existing file: {e}")
            return False

    def _validate_url(self, url: str) -> bool:
        """Check if URL is valid for downloading."""
        # Check for PDF extension and reject
        ext = os.path.splitext(url)[1].lower()
        if ext == '.pdf':
            self.logger.error(f"PDF files not supported: {url}")
            return False

        # Reject URLs with query parameters
        if '?' in url:
            self.logger.error(f"URLs with query parameters not supported: {url}")
            return False

        return True

    def _download_image_data(self, url: str) -> Optional[Tuple[bytes, str]]:
        """Download image data from URL with retries."""
        if not self._check_image_size(url):
            return None

        session = create_session_with_retries()
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; ImageDownloaderBot/1.0; "
                "+https://github.com/linusjf/RIAY/bot-info)"
            )
        }

        for attempt in range(self.MAX_RETRIES):
            try:
                response = session.get(url, headers=headers, stream=True)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    ext = self.get_extension_from_mime(content_type)
                    return (response.content, ext)
                elif response.status_code in {408, 429, 500, 502, 503, 504}:
                    wait = exponential_backoff_with_jitter(base=2, cap=60, attempt=attempt)
                    self.logger.warning(f"Retry {attempt + 1}: HTTP {response.status_code}, waiting {wait:.2f}s...")
                    time.sleep(wait)
                else:
                    self.logger.error(f"Failed with status: {response.status_code}")
                    break
            except Exception as e:
                self.logger.error(f"Download attempt {attempt + 1} failed: {e}")
                if attempt == self.MAX_RETRIES - 1:
                    raise

        self.logger.error("Download failed after retries.")
        return None

    def _save_image_file(self, image_data: bytes, filename: str, url: str) -> bool:
        """Save image data to file and handle post-processing."""
        try:
            with open(filename, "wb") as f:
                f.write(image_data)

            if not self._check_image_dimensions(filename):
                os.remove(filename)
                return False

            url_filename = os.path.splitext(filename)[0] + ".url.txt"
            with open(url_filename, "w") as url_file:
                url_file.write(url)
            self.DOWNLOADED_URLS[url] = filename

            ext = os.path.splitext(filename)[1].lower()
            if ext not in ('.jpg', '.jpeg'):
                jpeg_path = convert_to_jpeg(filename)
                if jpeg_path:
                    if not self._check_image_dimensions(jpeg_path):
                        os.remove(jpeg_path)
                        return False
                    self.logger.info(f"Saved: {jpeg_path} (source URL saved to {url_filename})")
                    self.DOWNLOADED_URLS[url] = jpeg_path
                    return True
                else:
                    self.logger.warning(f"Saved original format: {filename}")
                    return True
            else:
                self.logger.info(f"Saved: {filename} (source URL saved to {url_filename})")
                return True
        except Exception as e:
            self.logger.error(f"Error saving image file: {e}")
            return False

    def save_image(self, url: str, filename: str) -> bool:
        """Save an image from URL to local file."""
        if url in self.DOWNLOADED_URLS:
            self.logger.info(f"URL already downloaded: {url}")
            return self._copy_existing_download(url, filename)

        if not self._validate_url(url):
            return False

        try:
            if not self._check_image_size(url):
                return False

            result = self._download_image_data(url)
            if not result:
                return False

            image_data, ext = result
            temp_filename = os.path.splitext(filename)[0] + ext
            return self._save_image_file(image_data, temp_filename, url)
        except Exception as error:
            self.logger.error(f"Error downloading image: {error}")
            return False

    # ... rest of the file remains exactly the same ...
