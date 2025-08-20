#!/usr/bin/env python
"""Helper functions for art-related operations.

This module contains utility functions for working with artwork images,
including URL validation, domain checking, and image processing.
"""

import os
from typing import Optional, Callable, List, Set, Tuple
from requests import Session
import requests
from PIL import Image
import logging

from htmlhelper import extract_domain_from_url, clean_filename_text
from sessionhelper import create_session_with_retries, exponential_backoff_with_jitter
from simtools import compare_terms, MatchMode, THRESHOLDS
from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory

config = ConfigEnv(include_os_env=True)
logger = LoggerFactory.get_logger(
    name="arthelper",
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)

def is_stock_image_url(url: str, stock_photo_sites: List[str]) -> bool:
    """Check if a URL is from a known stock photo site.

    Args:
        url: The URL to check
        stock_photo_sites: List of stock photo site domains

    Returns:
        bool: True if URL is from a stock photo site, False otherwise
    """
    domain = extract_domain_from_url(url)
    if not domain:
        return False
    return any(site in domain for site in stock_photo_sites)

def get_extension_from_mime(mime_type: str) -> str:
    """Get file extension from MIME type.
    
    Args:
        mime_type: The MIME type string
        
    Returns:
        str: File extension with leading dot
    """
    mapping = {
        'image/png': '.png',
        'image/webp': '.webp',
        'image/svg+xml': '.svg',
        'image/avif': '.avif',
        'image/jpeg': '.jpg'
    }
    return mapping.get(mime_type.split(";")[0].strip(), '.jpg')

def url_has_query_parameters(url: str) -> bool:
    """Check if URL contains query parameters.
    
    Args:
        url: The URL to check
        
    Returns:
        bool: True if URL has query parameters, False otherwise
    """
    return '?' in url

def validate_url(url: str) -> bool:
    """Check if URL is valid for downloading.
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    # Check for PDF extension and reject
    ext = os.path.splitext(url)[1].lower()
    if ext == '.pdf':
        logger.error(f"PDF files not supported: {url}")
        return False

    # Reject URLs with query parameters
    if url_has_query_parameters(url):
        logger.error(f"URLs with query parameters not supported: {url}")
        return False

    return True

def check_image_size(url: str, max_image_bytes: int) -> bool:
    """Check if image size exceeds maximum allowed size before downloading.
    
    Args:
        url: The image URL
        max_image_bytes: Maximum allowed file size in bytes
        
    Returns:
        bool: True if image size is acceptable, False otherwise
    """
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
                if file_size > max_image_bytes:
                    logger.warning(f"Image too large (estimated {file_size} bytes exceeds {max_image_bytes})")
                    return False
        return True
    except Exception as e:
        logger.error(f"Error checking image size: {e}")
        return False

def check_image_dimensions(image_path: str, min_image_width: int, min_image_height: int) -> bool:
    """Check if image meets minimum dimension requirements.
    
    Args:
        image_path: Path to the image file
        min_image_width: Minimum required width
        min_image_height: Minimum required height
        
    Returns:
        bool: True if image meets dimension requirements, False otherwise
    """
    if min_image_width <= 0 and min_image_height <= 0:
        return True

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            if width >= min_image_width and height >= min_image_height:
                return True
            logger.warning(f"Image dimensions too small: {width}x{height} (min {min_image_width}x{min_image_height})")
            return False
    except Exception as e:
        logger.error(f"Error checking image dimensions: {e}")
        return False

def download_image_data(url: str, max_retries: int, max_image_bytes: int) -> Optional[Tuple[bytes, str]]:
    """Download image data from URL with retries.
    
    Args:
        url: The image URL
        max_retries: Maximum number of retry attempts
        max_image_bytes: Maximum allowed file size
        
    Returns:
        Optional[Tuple[bytes, str]]: Tuple of (image_data, file_extension) or None if failed
    """
    if not check_image_size(url, max_image_bytes):
        return None

    session = create_session_with_retries()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; ImageDownloaderBot/1.0; "
            "+https://github.com/linusjf/RIAY/bot-info)"
        )
    }

    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                ext = get_extension_from_mime(content_type)
                return (response.content, ext)
            elif response.status_code in {408, 429, 500, 502, 503, 504}:
                wait = exponential_backoff_with_jitter(base=2, cap=60, attempt=attempt)
                logger.warning(f"Retry {attempt + 1}: HTTP {response.status_code}, waiting {wait:.2f}s...")
                import time
                time.sleep(wait)
            else:
                logger.error(f"Failed with status: {response.status_code}")
                break
        except Exception as e:
            logger.error(f"Download attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise

    logger.error("Download failed after retries.")
    return None

def is_social_media_domain(domain: str, social_media_sites: List[str]) -> bool:
    """Check if domain is a social media site.
    
    Args:
        domain: The domain to check
        social_media_sites: List of social media site domains
        
    Returns:
        bool: True if domain is a social media site, False otherwise
    """
    return any(site in domain for site in social_media_sites)

def is_stock_images_domain(domain: str, stock_photo_sites: List[str]) -> bool:
    """Check if domain is a stock image site.
    
    Args:
        domain: The domain to check
        stock_photo_sites: List of stock photo site domains
        
    Returns:
        bool: True if domain is a stock image site, False otherwise
    """
    return any(site in domain for site in stock_photo_sites)

def process_url(url: str, score: float,
                social_media_sites: List[str],
                stock_photo_sites: List[str],
                is_social_media_domain_fn: Callable[[str, List[str]], bool],
                is_stock_images_domain_fn: Callable[[str, List[str]], bool],
                add_stock_photo_callback: Callable[[str, float], None]) -> bool:
    """
    Process a URL to determine if it's a social media or stock image domain.

    Args:
        url: The URL to process.
        score: Associated score for the image.
        social_media_sites: List of social media site domains
        stock_photo_sites: List of stock photo site domains
        is_social_media_domain_fn: Function to check social media domains.
        is_stock_images_domain_fn: Function to check stock image domains.
        add_stock_photo_callback: Callback to handle valid stock photo URLs.

    Returns:
        bool: True if processing should continue, False if skipped.
    """
    domain = extract_domain_from_url(url)
    if not domain:
        return True  # Continue processing

    if is_social_media_domain_fn(domain, social_media_sites):
        return False  # Skip this URL

    if is_stock_images_domain_fn(domain, stock_photo_sites):
        add_stock_photo_callback(url, score)
        return False  # Skip after handling

    return True  # Continue processing

def filter_and_score_results(results: List[Any], extract_metadata_fn: Callable[[Any], str], query: str, threshold: float = THRESHOLDS["cosine"]) -> List[Tuple[Any, float]]:
    """Filter and score search results based on cosine similarity.
    
    Args:
        results: List of search results
        extract_metadata_fn: Function to extract metadata from a result
        query: The search query
        threshold: Minimum similarity threshold
        
    Returns:
        List[Tuple[Any, float]]: List of qualifying results with their scores
    """
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

def build_enhanced_query(base_query: str, title: Optional[str], artist: Optional[str], 
                        location: Optional[str], date: Optional[str], style: Optional[str], 
                        medium: Optional[str], subject: Optional[str]) -> str:
    """Build an enhanced search query by combining base query with metadata.
    
    Args:
        base_query: The base search query
        title: Artwork title
        artist: Artist name
        location: Artwork location
        date: Creation date
        style: Artistic style
        medium: Art medium
        subject: Subject matter
        
    Returns:
        str: Enhanced search query
    """
    enhanced_query = base_query
    if artist and artist not in base_query:
        enhanced_query += f" by {artist}"
    if title and title not in base_query:
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
    return enhanced_query

def build_wikimedia_query(base_query: str, title: Optional[str], artist: Optional[str], 
                         date: Optional[str], location: Optional[str]) -> str:
    """Build a specialized query for Wikimedia searches.
    
    Args:
        base_query: The base search query
        title: Artwork title
        artist: Artist name
        date: Creation date
        location: Artwork location
        
    Returns:
        str: Wikimedia-optimized search query
    """
    wikimedia_query = base_query
    if artist and artist not in base_query:
        wikimedia_query += f" by {artist}"
    if title and title not in base_query:
        wikimedia_query += f" {title}"
    if date and date not in base_query:
        wikimedia_query += f" {date}"
    if location and location not in base_query:
        wikimedia_query += f" {location}"
    return wikimedia_query
