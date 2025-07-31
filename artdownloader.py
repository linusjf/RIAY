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

[... previous ArtDownloader class code remains exactly the same until the main() function ...]

def parse_arguments() -> argparse.Namespace:
    """Parse and return command line arguments."""
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
    return parser.parse_args()

def validate_arguments(args: argparse.Namespace) -> bool:
    """Validate that we have sufficient arguments to proceed."""
    if not args.query and not any([args.title, args.artist, args.location, 
                                 args.style, args.medium, args.subject]):
        return False
    return True

def build_search_query(args: argparse.Namespace) -> str:
    """Construct the initial search query from arguments."""
    query = args.query if args.query else ""
    if args.title and args.title not in query:
        query = f"{query} {args.title}".strip()
    if args.artist and args.artist not in query:
        query = f"{query} {args.artist}".strip()
    return query

async def run_downloader(args: argparse.Namespace, query: str) -> Tuple[bool, float]:
    """Run the main downloader workflow and return success status and elapsed time."""
    start_time = time.time()
    downloader = ArtDownloader(vars(args))
    success = await downloader.download_all(query=query)
    await downloader.print_results()
    elapsed_time = time.time() - start_time
    return success, elapsed_time

def log_results(success: bool, elapsed_time: float, logger) -> None:
    """Log the final results of the operation."""
    if success:
        logger.info(f"Downloaded art images in {elapsed_time:.2f} seconds")
    else:
        logger.error(f"Error occurred in downloading art images: Time taken: {elapsed_time:.2f} seconds")

async def main() -> None:
    """Main entry point for the script."""
    args = parse_arguments()
    
    if not validate_arguments(args):
        parse_arguments().print_help()
        sys.exit(1)

    query = build_search_query(args)
    success, elapsed_time = await run_downloader(args, query)
    
    # Create temporary logger for final output
    temp_logger = LoggerFactory.get_logger(
        name=os.path.basename(__file__),
        log_to_file=False
    )
    log_results(success, elapsed_time, temp_logger)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
