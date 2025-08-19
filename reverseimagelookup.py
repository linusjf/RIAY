#!/usr/bin/env python
"""Perform reverse image lookup using SerpAPI and imgbb APIs.

This script allows users to perform reverse image searches and verify images
against metadata using Google Lens via SerpAPI and imgbb for image hosting.
"""

import argparse
from enum import Enum, auto
import urllib.parse
import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import requests

from serpapi import GoogleSearch

from htmlhelper import clean_filename_text, extract_domain_from_url
from simtools import compare_terms, MatchMode, THRESHOLDS
from imgbb import upload_to_imgbb

from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory

config = ConfigEnv("config.env")
logger = LoggerFactory.get_logger(
    name=os.path.basename(__file__),
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)

class ReverseImageLookup:
    """Class for performing reverse image lookups using SerpAPI and imgbb."""

    class SEARCH_API(Enum):
        SERP_API = auto(),
        ZENSERP_API = auto()

    # Constants
    CONFIG_FILE: str = 'config.env'
    ZENSERP_API_ENDPOINT: str = "https://app.zenserp.com/api/v2/search"
    IMAGE_URL_FILE_EXTENSION: str = '.url.txt'
    REQUIRED_MATCH_COUNT: int = 5

    def __init__(self, search_api: SEARCH_API = SEARCH_API.SERP_API) -> None:
        """Initialize the reverse image lookup service."""
        # Load environment variables using ConfigEnv
        self.config: ConfigEnv = ConfigEnv(self.CONFIG_FILE, include_os_env=True)
        self.SERP_API_KEY: str = self.config[ConfigConstants.SERP_API_KEY]
        if not self.SERP_API_KEY:
            logger.error(f"{ConfigConstants.SERP_API_KEY} environment variable not set")
            raise ValueError(f"{ConfigConstants.SERP_API_KEY} environment variable not set")
        self.ZENSERP_API_KEY: str = self.config[ConfigConstants.ZENSERP_API_KEY]
        if not self.ZENSERP_API_KEY:
            logger.error(f"{ConfigConstants.ZENSERP_API_KEY} environment variable not set")
            raise ValueError(f"{ConfigConstants.ZENSERP_API_KEY} environment variable not set")
        self.search_api: ReverseImageLookup.SEARCH_API = search_api
        self.STOCK_PHOTO_SITES: List[str] = self.config[ConfigConstants.STOCK_PHOTO_SITES]
        self.match_text: Optional[str] = None
        self.MIN_IMAGE_WIDTH: int = self.config[ConfigConstants.MIN_IMAGE_WIDTH]
        self.MIN_IMAGE_HEIGHT: int = self.config[ConfigConstants.MIN_IMAGE_HEIGHT]

    def verify_image_against_metadata(self, image_url: str, metadata_text: str) -> float:
        """Verify if image matches metadata using Google Lens."""
        encoded_url = urllib.parse.quote(image_url, safe=":/")
        if self.search_api == self.SEARCH_API.SERP_API:
            parameters: Dict[str, Union[str, int]] = {
                "engine": "google_lens",
                "api_key": self.SERP_API_KEY,
                "url": encoded_url,
                "type": "visual_matches"
            }
            search: GoogleSearch = GoogleSearch(parameters)
            results: Dict[str, Any] = search.get_dict()
            visual_matches: List[Dict[str, Any]] = results["visual_matches"][0:self.REQUIRED_MATCH_COUNT]

            if not visual_matches:
                logger.info("No visual matches found")
                return 0.0

            first_match: Dict[str, Any] = visual_matches[0]
            title: str = first_match["title"]
            link: str = first_match["link"]
            source: str = first_match["source"]
            url: str = first_match["image"]

            self.match_text = ", ".join(filter(None, [
                title,
                clean_filename_text(link),
                source,
                clean_filename_text(url)
            ]))
            score: float = compare_terms(metadata_text, self.match_text, MatchMode.COSINE)
            logger.info(f"Matched: {image_url} —> {url}")
            return score
        else:
            headers: Dict[str, str] = {
                "apikey": self.ZENSERP_API_KEY}

            params: Tuple[Tuple[str, str], ...] = (
                ("image_url",encoded_url),
                ("hl", "en")
            )

            logger.debug(f"Invoking {self.ZENSERP_API_ENDPOINT} with image_url {encoded_url}")
            response: requests.Response = requests.get(self.ZENSERP_API_ENDPOINT, headers=headers, params=params)
            json_response: str = response.text
            logger.debug(f"{self.ZENSERP_API_ENDPOINT} response: {json_response}")
            data: Dict[str, Any] = json.loads(json_response)
            reverse_image_results: Dict[str, Any] = data["reverse_image_results"]
            logger.debug(f"reverse image results: {reverse_image_results}")
            if not reverse_image_results:
                logger.info("No reverse image results found")
                return 0.0
            organic_results: Optional[List[Dict[str, Any]]] = reverse_image_results.get("organic")
            logger.debug(f"organic results: {organic_results}")
            if not organic_results:
                logger.info("No organic results found")
                return 0.0
            best_score: float = 0.0
            best_match: Dict[str, Any] = {}
            for organic_result in organic_results[0:5]:
                match: Dict[str, Any] = organic_result
                title: str = match["title"]
                url: str = match["url"]
                destination: str = match["destination"]
                description: str = match["description"]
                match_text: str = ", ".join(filter(None, [
                    title,
                    clean_filename_text(url),
                    destination,
                    description
                    ]))
                score: float = compare_terms(metadata_text, match_text, MatchMode.COSINE)
                if score > best_score:
                    best_score = score
                    best_match = match
                    self.match_text = match_text

            logger.info(f"Matched: {encoded_url} —> {best_match['url']}")
            return best_score

    def reverse_image_search(self, image_url: str, metadata_text: str) -> List[Tuple[str, float]]:
        """Perform reverse image search and return qualifying URLs."""
        params: Dict[str, Union[str, int]] = {
            "engine": "google_lens",
            "api_key": self.SERP_API_KEY,
            "url": image_url,
            "type": "visual_matches"
        }
        search: GoogleSearch = GoogleSearch(params)
        results: Dict[str, Any] = search.get_dict()
        visual_matches: List[Dict[str, Any]] = results["visual_matches"][0:5]
        qualifying_urls: List[Tuple[str, float]] = []

        for image_info in visual_matches:
            title: str = image_info["title"]
            link: str = image_info["link"]
            source: str = image_info["source"]
            url: str = image_info["image"]
            image_width: int = image_info["image_width"]
            image_height: int = image_info["image_height"]

            # Skip PDF links
            if link.lower().endswith('.pdf'):
                logger.debug(f"Skipping PDF link: {link}")
                continue

            # Skip stock photo sites
            domain: Optional[str] = extract_domain_from_url(link)
            if domain and any(stock_domain.lower() in domain for stock_domain in self.STOCK_PHOTO_SITES):
                logger.debug(f"Skipping stock photo site: {domain}")
                continue
            if (int(image_width) < self.MIN_IMAGE_WIDTH or int(image_height) < self.MIN_IMAGE_HEIGHT):
                logger.debug(f"Skipping small image: {image_width}x{image_height}")
                continue

            match_text: str = ", ".join(filter(None, [
                title,
                clean_filename_text(link),
                source,
                clean_filename_text(url)
            ]))
            score: float = compare_terms(metadata_text, match_text, MatchMode.COSINE)
            if score > THRESHOLDS["cosine"]:
                qualifying_urls.append((url, score))

        # Sort by score in descending order
        qualifying_urls.sort(key=lambda x: x[1], reverse=True)
        return qualifying_urls

    @staticmethod
    def validate_image_path(path: str) -> Path:
        """Validate that the path exists and is a file."""
        path_obj: Path = Path(path)
        if not path_obj.exists():
            logger.error(f"File '{path}' does not exist")
            raise argparse.ArgumentTypeError(f"File '{path}' does not exist")
        if not path_obj.is_file():
            logger.error(f"'{path}' is not a file")
            raise argparse.ArgumentTypeError(f"'{path}' is not a file")
        return path_obj

    def reverse_image_lookup(self, image_path: str, title: str, artist: str, subject: Optional[str] = None,
                           location: Optional[str] = None, date: Optional[str] = None,
                           style: Optional[str] = None, medium: Optional[str] = None) -> Tuple[List[Tuple[str, float]], str]:
        """Perform reverse image lookup with provided parameters."""
        image_url: str
        delete_url: str
        image_url, delete_url = upload_to_imgbb(image_path)
        qualifying_urls: List[Tuple[str, float]] = self.reverse_image_lookup_url(
            image_url,
            title,
            artist,
            subject,
            location,
            date,
            style,
            medium
        )
        return qualifying_urls, delete_url

    def reverse_image_lookup_url(self, image_url: str, title: str, artist: str, subject: Optional[str] = None,
                               location: Optional[str] = None, date: Optional[str] = None,
                               style: Optional[str] = None, medium: Optional[str] = None) -> List[Tuple[str, float]]:
        """Perform reverse image lookup using a direct image URL."""
        encoded_url = urllib.parse.quote(image_url, safe=":/")
        metadata_text: str = ", ".join(filter(None, [
            title,
            artist,
            subject,
            location,
            date,
            style,
            medium,
            clean_filename_text(image_url)
        ]))

        qualifying_urls: List[Tuple[str, float]] = self.reverse_image_search(encoded_url, metadata_text)
        return qualifying_urls

    @staticmethod
    def get_metadata_text(title: str, artist: str, subject: Optional[str] = None,
                         location: Optional[str] = None, date: Optional[str] = None,
                         style: Optional[str] = None, medium: Optional[str] = None) -> str:
        """Create metadata text string from parameters."""
        return ", ".join(filter(None, [
            title,
            artist,
            subject,
            location,
            date,
            style,
            medium
        ]))

    def match_reverse_lookup(self, image: str, title: str, artist: str, subject: Optional[str] = None,
                            location: Optional[str] = None, date: Optional[str] = None,
                            style: Optional[str] = None, medium: Optional[str] = None) -> float:
        """Core reverse lookup functionality."""
        source_url: Optional[str] = None
        # Check for corresponding url.txt file if no source_url provided
        url_file: str = os.path.splitext(image)[0] + self.IMAGE_URL_FILE_EXTENSION
        if os.path.exists(url_file):
            with open(url_file, 'r', encoding='utf-8') as file:
                source_url = file.read().strip()
                source_url = urllib.parse.quote(source_url, safe=":/")
                logger.info(f"Found source URL: {source_url}")

        if not source_url:
            source_url, _ = upload_to_imgbb(image)

        metadata_text: str = self.get_metadata_text(
            title,
            artist,
            subject,
            location,
            date,
            style,
            medium
        )

        score: float = self.verify_image_against_metadata(source_url, metadata_text)
        return score

def main() -> None:
    """Main entry point for the script."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='Perform reverse image search using SerpAPI'
    )
    parser.add_argument(
        "--image",
        required=True,
        type=ReverseImageLookup.validate_image_path,
        help="Path to the image file"
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Title of the artwork"
    )
    parser.add_argument(
        "--artist",
        required=True,
        help="Artist of the artwork"
    )
    parser.add_argument(
        "--subject",
        help="Subject of the artwork"
    )
    parser.add_argument(
        "--location",
        help="Current location of artwork"
    )
    parser.add_argument(
        "--date",
        help="Date when artwork was created"
    )
    parser.add_argument(
        "--style",
        help="Style of the artwork"
    )
    parser.add_argument(
        "--medium",
        help="Medium of the artwork"
    )

    start_time: float = time.time()
    script_name: str = os.path.basename(__file__)
    args: argparse.Namespace = parser.parse_args()

    lookup: ReverseImageLookup = ReverseImageLookup()
    score: float = lookup.match_reverse_lookup(
        args.image,
        args.title,
        args.artist,
        args.subject,
        args.location,
        args.date,
        args.style,
        args.medium
    )

    elapsed_time: float = time.time() - start_time
    logger.info(f"Verified image {args.image} in {elapsed_time:.2f} seconds using {script_name}")
    print(f"{score:.4f}")
    sys.exit(0 if score >= THRESHOLDS["cosine"] else 1)

if __name__ == '__main__':
    main()
