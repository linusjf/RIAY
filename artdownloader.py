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
            result = self._download_image_data(url)
            if not result:
                return False

            image_data, ext = result
            temp_filename = os.path.splitext(filename)[0] + ext
            return self._save_image_file(image_data, temp_filename, url)
        except Exception as error:
            self.logger.error(f"Error downloading image: {error}")
            return False

    def is_social_media_domain(self, domain: str):
        if any(site in domain for site in self.SOCIAL_MEDIA_SITES):
            return True
        return False

    def is_stock_images_domain(self, domain: str):
        if any(site in domain for site in self.STOCK_PHOTO_SITES):
            return True
        return False

    @retry(
        retry=retry_if_exception_type(RatelimitException),
        wait=wait_exponential(min=1, max=10),
        stop=stop_after_attempt(MAX_RETRIES),
    )
    def search_duckduckgo_images(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        with DDGS() as ddgs:
            return ddgs.images(query, max_results=max_results)

    def filter_and_score_results(self, results, extract_metadata_fn, query, threshold=THRESHOLDS["cosine"]):
        qualifying = []
        for idx, result in enumerate(results):
            metadata = extract_metadata_fn(result)
            score = compare_terms(query.lower(), metadata.lower(), MatchMode.COSINE)
            if score >= threshold:
                print(f"✅ Qualified result {idx+1} (score: {score:.3f})", file=sys.stderr)
                qualifying.append((result, score))
            else:
                print(f"❌ Excluded result {idx+1} (score: {score:.3f})", file=sys.stderr)
        return qualifying


    def download_from_duckduckgo(self, query: str, filename_base: str) -> bool:
        """Download image from DuckDuckGo search."""
        self.logger.info(f"DuckDuckGo search for: {query}")
        try:
            results = self.search_duckduckgo_images(query, max_results=10)
            if not results:
                self.logger.error("No matching images found.")
                return False

            def extract_metadata(item):
                return " ".join(str(p) for p in [item["title"], clean_filename_text(item["image"])] if p)

            qualifying_results = self.filter_and_score_results(results[:self.MAX_ALLOWED_RESULTS], extract_metadata, query)

            if not qualifying_results:
                self.logger.error(f"No qualifying results found (score >= {THRESHOLDS['cosine']} )")
                return False

            success = False
            for idx, (result, score) in enumerate(qualifying_results):
                url = result["image"]
                if '?' in url:
                    self.logger.warning(f"Url has query parameters: rejecting {url}")
                    continue
                domain = extract_domain_from_url(url)
                if domain:
                    if self.is_social_media_domain(domain):
                        continue
                    if self.is_stock_images_domain(domain):
                        self.FOUND_STOCK_PHOTOS.add(url)
                        self.DUCKDUCKGO_IMAGES.append((url, "", score))
                        continue
                filename = os.path.join(
                    self.SAVE_DIR,
                    f"{filename_base}_{idx+1}_duckduckgo.jpg"
                )
                if self.save_image(url, filename):
                    self.DUCKDUCKGO_IMAGES.append((url, filename, score))
                    success = True

            success = success or len(self.DUCKDUCKGO_IMAGES) > 0
            return success

        except Exception as error:
            self.logger.error(f"Error: {error}")
        return False

    def download_from_wikimedia_search(self, query: str, detailed_query: str, filename_base: str, source: str = "wikimedia_search") -> bool:
        """Search Wikimedia Commons for an image by query and download the top result."""
        self.logger.info(f"Searching Wikimedia for: {query}")
        search_endpoint = "https://commons.wikimedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srnamespace": 6,
            "srlimit": self.MAX_ALLOWED_RESULTS,
            "srprop": "size|wordcount|timestamp|snippet|titlesnippet"
        }

        try:
            resp = requests.get(search_endpoint, params=search_params, timeout=30)
            resp.raise_for_status()
            search_data = resp.json()
            search_results = search_data.get("query", {}).get("search", [])

            if not search_results:
                self.logger.error("No matching images found.")
                return False

            def extract_metadata(result):
                result_meta_data = " ".join(str(p) for p in [clean_filename(result["title"]),
                                                             strip_span_tags_but_keep_contents(result["titlesnippet"]),
                                                             strip_span_tags_but_keep_contents(result["snippet"])
                                                             ] if p)
                return result_meta_data

            qualifying_results = self.filter_and_score_results(search_results, extract_metadata, detailed_query)

            if not qualifying_results:
                self.logger.error(f"No qualifying results found (score >= {THRESHOLDS['cosine']})")
                return False

            success = False
            for idx, (result, score) in enumerate(qualifying_results):
                selected_title = result["title"]
                self.logger.info(f"Selected title {selected_title} with score: {score}")

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
                            filename = os.path.join(self.SAVE_DIR, f"{unique_filename}.jpg")
                            if self.save_image(image_url, filename):
                                self.WIKIPEDIA_IMAGES.append((image_url, filename, score))
                                success = True

            return success

        except Exception as e:
            self.logger.error(f"Error: {e}")
            return False

    def download_image_from_wikipedia_article(self, query: str, detailed_query: str, filename_base: str) -> bool:
        """Download the first usable image from a Wikipedia article."""
        self.logger.info(f"Fetching all images from Wikipedia article: {query}")
        try:
            params = {
                "limit": self.MAX_ALLOWED_RESULTS,
                "q": query
            }
            response = requests.get("https://api.wikimedia.org/core/v1/wikipedia/en/search/page", params=params)
            image_data = response.json()

            pages = image_data.get("pages", [])

            def extract_metadata(result):
                result_meta_data = " ".join(str(p) for p in [result["key"],result["title"],strip_span_tags_but_keep_contents(result["excerpt"]),result["description"]] if p)
                return result_meta_data

            qualifying_pages = self.filter_and_score_results(pages, extract_metadata, detailed_query)

            if not qualifying_pages:
                self.logger.error(f"No qualifying pages found (score >= {THRESHOLDS['cosine']})")
                return False

            success = False
            for idx, (result, score) in enumerate(qualifying_pages):
                title = result["title"]
                self.logger.info(f"Downloading image for qualified page {idx+1}: {title} {score}")
                unique_filename = f"{filename_base}_{idx+1}"
                if self.download_from_wikimedia_search(title, detailed_query, unique_filename, "wikipedia"):
                    success = True

            return success

        except Exception as error:
            self.logger.error(f"Error: {error}")
            return False

    def download_from_wikimedia(self, query: str, enhanced_query: str, filename_base: str) -> bool:
        """Download image from Wikimedia Commons."""
        self.logger.info(f"Wikimedia Commons search for: {query}")
        params = {"q": query}
        try:
            response = requests.get(
                self.WIKIMEDIA_SEARCH_API_URL,
                params=params
            ).json()
            pages = response.get("pages", [])
            if not pages:
                self.logger.error("No matching images found.")
                return False

            def extract_metadata(page):
                page_meta_data = " ".join(str(p) for p in
                                          [
                                              clean_filename_text(clean_filename(page.get("key"))),
                                              clean_filename_text(clean_filename(page.get("title"))),
                                              strip_span_tags_but_keep_contents(page.get("excerpt")),
                                              page.get("description")
                                          ] if p)
                return page_meta_data

            qualifying_pages = self.filter_and_score_results(pages[:self.MAX_ALLOWED_RESULTS], extract_metadata, enhanced_query)

            if not qualifying_pages:
                self.logger.error(f"No qualifying files found (score >= {THRESHOLDS['cosine']})")
                return False

            success = False
            for idx, (page, score) in enumerate(qualifying_pages):
                file = page.get("key")
                self.logger.info(f"Downloading image for qualified file {idx+1}: {file}")
                unique_filename = f"{filename_base}_{idx+1}"
                file_response = requests.get(
                    self.WIKIMEDIA_FILE_API_URL + "/" + file,
                    headers={'User-Agent': 'Mozilla/5.0'}
                ).json()
                original = file_response.get("original")
                if original and "url" in original:
                    image_url = original.get("url")
                    filename = os.path.join(
                        self.SAVE_DIR,
                        f"{unique_filename}_wikimedia.jpg"
                    )
                    if self.save_image(image_url, filename):
                        self.WIKIPEDIA_IMAGES.append((image_url,filename, score))
                        success = True

            return success

        except Exception as error:
            self.logger.error(f"Error: {error}")
            return False

    def download_from_google(self, query: str, filename_base: str) -> bool:
        """Download image from Google Images via SerpAPI."""
        self.logger.info(f"Google search for: {query}")
        try:
            params = {
                "q": query,
                "tbm": "isch",
                "api_key": self.SERPAPI_API_KEY,
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            if not results:
                self.logger.error("No matching images found.")
                return False
            images = results.get("images_results", [])
            if not images:
                return False

            def extract_metadata(image):
                image_meta_data = " ".join(str(p) for p in
                                          [
                                              image.get("title"),
                                              clean_filename_text(image.get("original"))
                                          ] if p)
                return image_meta_data

            qualifying_pages = self.filter_and_score_results(images[:self.MAX_ALLOWED_RESULTS], extract_metadata, query)

            if not qualifying_pages:
                self.logger.error(f"No qualifying images found (score >= {THRESHOLDS['cosine']})")
                return False

            success = False
            for idx, (image, score) in enumerate(qualifying_pages):
                url = image.get("original")
                if '?' in url:
                    self.logger.warning(f"Url has query parameters: rejecting {url}")
                    continue
                domain = extract_domain_from_url(url)
                if domain:
                    if self.is_social_media_domain(domain):
                        continue
                    if self.is_stock_images_domain(domain):
                        self.FOUND_STOCK_PHOTOS.add(url)
                        self.GOOGLE_IMAGES.append((url, "", score))
                        continue
                self.logger.info(f"Downloading image for qualified image {idx+1}: {url}")
                unique_filename = f"{filename_base}_{idx+1}"
                filename = os.path.join(
                    self.SAVE_DIR,
                    f"{unique_filename}_google.jpg"
                )
                if self.save_image(url, filename):
                    self.GOOGLE_IMAGES.append((url, filename, score))
                    success = True

            success = success or len(self.GOOGLE_IMAGES) > 0
            return success

        except Exception as error:
            self.logger.error(f"Error: {error}")
            return False

    def download_from_googlelens(self, qualified_urls: List[Tuple[str, float]], filename_base: Optional[str]) -> Tuple[Optional[str], Optional[float]]:
        """Download images from Google Lens reverse image search results."""
        if not qualified_urls:
            return (None, None)

        for idx, (url, score) in enumerate(qualified_urls):
            filename = os.path.join(
                self.SAVE_DIR,
                f"{filename_base}_{idx+1}_googlelens.jpg"
            )
            if self.save_image(url, filename):
                return (filename, score)
        return (None, None)

    def _build_enhanced_query(self, base_query: str) -> str:
        """Build an enhanced search query by combining base query with metadata."""
        enhanced_query = base_query
        if self.artist and self.artist not in base_query:
            enhanced_query += f" by {self.artist}"
        if self.title and self.title not in base_query:
            enhanced_query += f" {self.title}"
        if self.location:
            enhanced_query += f" {self.location}"
        if self.date:
            enhanced_query += f" {self.date}"
        if self.style:
            enhanced_query += f" {self.style}"
        if self.medium:
            enhanced_query += f" {self.medium}"
        if self.subject:
            enhanced_query += f" {self.subject}"
        return enhanced_query

    def _build_wikimedia_query(self, base_query: str) -> str:
        """Build a specialized query for Wikimedia searches."""
        wikimedia_query = base_query
        if self.artist and self.artist not in base_query:
            wikimedia_query += f" by {self.artist}"
        if self.title and self.title not in base_query:
            wikimedia_query += f" {self.title}"
        if self.date and self.date not in base_query:
            wikimedia_query += f" {self.date}"
        if self.location and self.location not in base_query:
            wikimedia_query += f" {self.location}"
        return wikimedia_query

    def _search_wikipedia_sources(self, wikimedia_query: str, enhanced_query: str) -> bool:
        """Search Wikipedia-related sources for images."""
        downloaded_wikipedia_search = self.download_image_from_wikipedia_article(
            wikimedia_query, enhanced_query, str(self.filename_base)
        )
        downloaded_wikimedia_search = self.download_from_wikimedia_search(
            wikimedia_query, enhanced_query, str(self.filename_base)
        )
        downloaded_wikimedia = self.download_from_wikimedia(
            wikimedia_query, enhanced_query, str(self.filename_base)
        )
        return any([downloaded_wikipedia_search, downloaded_wikimedia_search, downloaded_wikimedia])

    def _search_other_sources(self, enhanced_query: str) -> bool:
        """Search non-Wikipedia sources for images."""
        downloaded_duckduckgo = self.download_from_duckduckgo(
            enhanced_query, str(self.filename_base)
        )
        downloaded_google = self.download_from_google(
            enhanced_query, str(self.filename_base)
        )
        return any([downloaded_duckduckgo, downloaded_google])

    def download_all(self, query: str) -> bool:
        """Download images from all available sources."""
        if self.filename_base is None:
            self.filename_base = query.replace(' ', '_')

        enhanced_query = self._build_enhanced_query(query)
        wikipedia_success = False

        if self.SEARCH_WIKIPEDIA:
            wikimedia_query = self._build_wikimedia_query(query)
            self.logger.info(f"Searching wikis with simple query: {wikimedia_query}")
            wikipedia_success = self._search_wikipedia_sources(wikimedia_query, enhanced_query)

        self.logger.info(f"Searching google and duckduckgo with enhanced query: {enhanced_query}")
        other_sources_success = self._search_other_sources(enhanced_query)

        return wikipedia_success or other_sources_success

    def _print_downloaded_images(self) -> None:
        """Print list of downloaded images."""
        print("\nDownloaded images: ")
        for v in self.DOWNLOADED_URLS.values():
            print(v)

    def _print_stock_photos(self) -> None:
        """Print list of found stock photos."""
        if self.FOUND_STOCK_PHOTOS:
            print("\nFound stock photos (not downloaded):")
            for url in self.FOUND_STOCK_PHOTOS:
                print(url)

    def _print_all_search_results(self) -> None:
        """Print all search results with scores."""
        all_results = self.WIKIPEDIA_IMAGES + self.DUCKDUCKGO_IMAGES + self.GOOGLE_IMAGES
        if all_results:
            print("\nAll search results (url, file, score):")
            for url, file, score in all_results:
                print(f"{url} -> {file} (score: {score:.3f})")

    def _get_best_result(self) -> Optional[Tuple[str, str, float]]:
        """Find and return the best available result."""
        all_results = self.WIKIPEDIA_IMAGES + self.DUCKDUCKGO_IMAGES + self.GOOGLE_IMAGES
        sorted_results = sorted(all_results, key=lambda x: x[2], reverse=True)

        for url, file, score in sorted_results:
            if file and os.path.exists(file):
                return (url, file, score)

            filename = os.path.join(self.SAVE_DIR, f"best_result_{self.filename_base}.jpg")
            if self.save_image(url, filename):
                return (url, filename, score)

        return None

    def _handle_alternate_images(self, best_result: Tuple[str, str, float]) -> None:
        """Handle alternate image search if enabled."""
        url, file, score = best_result
        if "best_result_" in file and self.FIND_ALTERNATE_IMAGES:
            lookup = ReverseImageLookup()
            qualified_urls = lookup.reverse_image_lookup_url(
                url, str(self.title), str(self.artist), 
                self.subject, self.location, self.date, 
                self.style, self.medium
            )
            if qualified_urls:
                best_qualified_result = self.download_from_googlelens(
                    qualified_urls=qualified_urls, 
                    filename_base=self.filename_base
                )
                if best_qualified_result:
                    filepath, url_score = best_qualified_result
                    print(f"\n⭐ Best available image (downloaded): {filepath} (score: {url_score:.3f})")
                else:
                    print(f"\n⭐ Best available image (downloaded): {file} (score: {score:.3f})")
            else:
                print(f"\n⭐ Best available image (downloaded): {file} (score: {score:.3f})")
        else:
            print(f"\n⭐ Best available image (downloaded): {file} (score: {score:.3f})")

    def print_results(self) -> None:
        """Print summary of downloaded images and results."""
        self._print_downloaded_images()
        self._print_stock_photos()
        self._print_all_search_results()

        best_result = self._get_best_result()
        if best_result:
            self._handle_alternate_images(best_result)


def main() -> None:
    """Main entry point for the script."""
    start_time = time.time()
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

    downloader = ArtDownloader(vars(args))

    query = args.query if args.query else ""
    if args.title and args.title not in query:
        query = f"{query} {args.title}".strip()
    if args.artist and args.artist not in query:
        query = f"{query} {args.artist}".strip()

    success = downloader.download_all(
        query=query,
    )

    downloader.print_results()

    end_time = time.time()
    elapsed_time = end_time - start_time
    if success:
        downloader.logger.info(f"Downloaded art images in {elapsed_time:.2f} seconds")
    else:
        downloader.logger.error(f"Error occurred in downloading art images: Time taken: {elapsed_time:.2f} seconds")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
