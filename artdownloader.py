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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from serpapi import GoogleSearch
from fuzzywuzzy import fuzz
from bashhelper import parse_bash_array
from htmlhelper import strip_span_tags_but_keep_contents

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

[... rest of artdownloader.py remains exactly the same ...]
