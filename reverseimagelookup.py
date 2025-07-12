#!/usr/bin/env python
"""Perform reverse image lookup using SerpAPI and imgbb APIs.

This script allows users to perform reverse image searches and verify images
against metadata using Google Lens via SerpAPI and imgbb for image hosting.
"""

import argparse
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from serpapi import GoogleSearch

from bashhelper import parse_bash_array
from htmlhelper import clean_filename_text, extract_domain_from_url
from simtools import compare_terms, MatchMode, THRESHOLDS
from imgbb import upload_to_imgbb

# Constants
CONFIG_FILE = 'config.env'
STOCK_PHOTO_SITES_VAR = 'STOCK_PHOTO_SITES'
SERP_API_KEY_VAR = "SERP_API_KEY"

# Load environment variables from config.env
load_dotenv(CONFIG_FILE)
SERP_API_KEY = os.getenv(SERP_API_KEY_VAR)
if not SERP_API_KEY:
    raise ValueError(f"{SERP_API_KEY_VAR} environment variable not set")

STOCK_PHOTO_SITES = parse_bash_array(CONFIG_FILE, STOCK_PHOTO_SITES_VAR)

MIN_IMAGE_WIDTH = 350
MIN_IMAGE_HEIGHT = 480
REQUIRED_MATCH_COUNT = 5
IMAGE_URL_FILE_EXTENSION = '.url.txt'

# ... rest of reverseimagelookup.py remains exactly the same ...
