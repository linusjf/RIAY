#!/usr/bin/env python
"""Perform reverse image lookup using SerpAPI and imgbb APIs.

This script allows users to perform reverse image searches and verify images
against metadata using Google Lens via SerpAPI and imgbb for image hosting.
"""

import argparse
from enum import Enum, auto
import os
import sys
import time
import json
from pathlib import Path
import requests

from configenv import ConfigEnv
from configconstants import ConfigConstants
from serpapi import GoogleSearch

from htmlhelper import clean_filename_text, extract_domain_from_url
from simtools import compare_terms, MatchMode, THRESHOLDS
from imgbb import upload_to_imgbb

class ReverseImageLookup:
    """Class for performing reverse image lookups using SerpAPI and imgbb."""

    class SEARCH_API(Enum):
        SERP_API = auto(),
        ZENSERP_API = auto()

    # Constants
    CONFIG_FILE = 'config.env'
    ZENSERP_API_ENDPOINT = "https://app.zenserp.com/api/v2/search"
    IMAGE_URL_FILE_EXTENSION = '.url.txt'
    REQUIRED_MATCH_COUNT = 5

    def __init__(self, search_api=SEARCH_API.SERP_API):
        """Initialize the reverse image lookup service."""
        # Load environment variables using ConfigEnv
        self.config = ConfigEnv(self.CONFIG_FILE, include_os_env=True)
        self.SERP_API_KEY = self.config[ConfigConstants.SERP_API_KEY]
        if not self.SERP_API_KEY:
            raise ValueError(f"{ConfigConstants.SERP_API_KEY} environment variable not set")
        self.ZENSERP_API_KEY = self.config[ConfigConstants.ZENSERP_API_KEY]
        if not self.ZENSERP_API_KEY:
            raise ValueError(f"{ConfigConstants.ZENSERP_API_KEY} environment variable not set")
        self.search_api = search_api
        self.STOCK_PHOTO_SITES = self.config[ConfigConstants.STOCK_PHOTO_SITES]
        self.match_text = None
        self.MIN_IMAGE_WIDTH = self.config[ConfigConstants.MIN_IMAGE_WIDTH]
        self.MIN_IMAGE_HEIGHT = self.config[ConfigConstants.MIN_IMAGE_HEIGHT]

    def verify_image_against_metadata(self, image_url, metadata_text):
        if self.search_api == self.SEARCH_API.SERP_API:
            """Verify if image matches metadata using Google Lens."""
            params = {
                "engine": "google_lens",
                "api_key": self.SERP_API_KEY,
                "url": image_url,
                "type": "visual_matches"
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            visual_matches = results["visual_matches"][0:self.REQUIRED_MATCH_COUNT]

            if not visual_matches:
                return 0.0

            first_match = visual_matches[0]
            title = first_match["title"]
            link = first_match["link"]
            source = first_match["source"]
            url = first_match["image"]

            self.match_text = ", ".join(filter(None, [
                title,
                clean_filename_text(link),
                source,
                clean_filename_text(url)
            ]))
            score = compare_terms(metadata_text, self.match_text, MatchMode.COSINE)
            print(f"Matched: {image_url} —> {url}", file=sys.stderr)
            return score
        elif self.search_api == self.SEARCH_API.ZENSERP_API:
            headers = {
                "apikey": self.ZENSERP_API_KEY}

            params = (
                ("image_url",image_url),
                ("hl", "en")
            );

            response = requests.get(self.ZENSERP_API_ENDPOINT, headers=headers, params=params);
            json_response = response.text
            data = json.loads(json_response)
            reverse_image_results = data["reverse_image_results"]
            if not reverse_image_results:
                return 0.0
            organic_results = reverse_image_results.get("organic")
            if not organic_results:
                return 0.0
            best_score = 0.0
            best_match = {}
            for organic_result in organic_results[0:5]:
                match = organic_result
                title = match["title"]
                url = match["url"]
                destination = match["destination"]
                description = match["description"]
                match_text = ", ".join(filter(None, [
                    title,
                    clean_filename_text(url),
                    destination,
                    description
                    ]))
                score = compare_terms(metadata_text, match_text, MatchMode.COSINE)
                if score > best_score:
                    best_score = score
                    best_match = match
                    self.match_text = match_text

            print(f"Matched: {image_url} —> {best_match["url"]}", file=sys.stderr)
            return best_score

    def reverse_image_search(self, image_url, metadata_text):
        """Perform reverse image search and return qualifying URLs."""
        params = {
            "engine": "google_lens",
            "api_key": self.SERP_API_KEY,
            "url": image_url,
            "type": "visual_matches"
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        visual_matches = results["visual_matches"][0:5]
        qualifying_urls = []

        for image_info in visual_matches:
            title = image_info["title"]
            link = image_info["link"]
            source = image_info["source"]
            url = image_info["image"]
            image_width = image_info["image_width"]
            image_height = image_info["image_height"]

            # Skip PDF links
            if link.lower().endswith('.pdf'):
                continue

            # Skip stock photo sites
            domain = extract_domain_from_url(link)
            if domain and any(stock_domain.lower() in domain for stock_domain in self.STOCK_PHOTO_SITES):
                continue
            if (int(image_width) < self.MIN_IMAGE_WIDTH or int(image_height) < self.MIN_IMAGE_HEIGHT):
                continue

            match_text = ", ".join(filter(None, [
                title,
                clean_filename_text(link),
                source,
                clean_filename_text(url)
            ]))
            score = compare_terms(metadata_text, match_text, MatchMode.COSINE)
            if score > THRESHOLDS["cosine"]:
                qualifying_urls.append((url, score))

        # Sort by score in descending order
        qualifying_urls.sort(key=lambda x: x[1], reverse=True)
        return qualifying_urls

    @staticmethod
    def validate_image_path(path):
        """Validate that the path exists and is a file."""
        path_obj = Path(path)
        if not path_obj.exists():
            raise argparse.ArgumentTypeError(f"File '{path}' does not exist")
        if not path_obj.is_file():
            raise argparse.ArgumentTypeError(f"'{path}' is not a file")
        return path

    def reverse_image_lookup(self, image_path, title, artist, subject=None, location=None,
                            date=None, style=None, medium=None):
        """Perform reverse image lookup with provided parameters.

        Args:
            image_path: Path to the image file
            title: Title of the artwork
            artist: Artist of the artwork
            subject: Subject of the artwork (optional)
            location: Current location of artwork (optional)
            date: Date when artwork was created (optional)
            style: Style of the artwork (optional)
            medium: Medium of the artwork (optional)

        Returns:
            tuple: (list of qualifying URLs, delete_url from imgbb)
        """
        image_url, delete_url = upload_to_imgbb(image_path)
        qualifying_urls = self.reverse_image_lookup_url(
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

    def reverse_image_lookup_url(self, image_url, title, artist, subject=None,
                                location=None, date=None, style=None, medium=None):
        """Perform reverse image lookup using a direct image URL.

        Args:
            image_url: URL of the image file
            title: Title of the artwork
            artist: Artist of the artwork
            subject: Subject of the artwork (optional)
            location: Current location of artwork (optional)
            date: Date when artwork was created (optional)
            style: Style of the artwork (optional)
            medium: Medium of the artwork (optional)

        Returns:
            tuple: (list of qualifying URLs, None since no imgbb upload was done)
        """
        metadata_text = ", ".join(filter(None, [
            title,
            artist,
            subject,
            location,
            date,
            style,
            medium,
            clean_filename_text(image_url)
        ]))

        qualifying_urls = self.reverse_image_search(image_url, metadata_text)
        return qualifying_urls

    @staticmethod
    def get_metadata_text(title, artist, subject=None, location=None, date=None, style=None, medium=None):
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

    def match_reverse_lookup(self, image, title, artist, subject=None, location=None, date=None, style=None, medium=None):
        """Core reverse lookup functionality.

        Args:
            args: Namespace object containing command line arguments

        Returns:
            score
        """
        source_url = None
        # Check for corresponding url.txt file if no source_url provided
        url_file = os.path.splitext(image)[0] + self.IMAGE_URL_FILE_EXTENSION
        if os.path.exists(url_file):
            with open(url_file, 'r', encoding='utf-8') as file:
                source_url = file.read().strip()
                print(f"Found source URL: {source_url}", file=sys.stderr)

        if not source_url:
            source_url, _ = upload_to_imgbb(image)

        metadata_text = self.get_metadata_text(
            title,
            artist,
            subject,
            location,
            date,
            style,
            medium
        )

        score = self.verify_image_against_metadata(source_url, metadata_text)
        return score

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
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

    start_time = time.time()
    script_name = os.path.basename(__file__)
    args = parser.parse_args()

    lookup = ReverseImageLookup()
    score = lookup.match_reverse_lookup(
        args.image,
        args.title,
        args.artist,
        args.subject,
        args.location,
        args.date,
        args.style,
        args.medium
    )

    elapsed_time = time.time() - start_time
    print(
        f"Verified image {args.image} in {elapsed_time:.2f} seconds using {script_name}",
        file=sys.stderr
    )
    print(f"{score:.4f}")
    sys.exit(0 if score >= THRESHOLDS["cosine"] else 1)

if __name__ == '__main__':
    main()
