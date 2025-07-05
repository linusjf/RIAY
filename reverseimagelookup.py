#!/usr/bin/env python
"""
Reverseimagelookup.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : reverseimagelookup
# @created     : Saturday Jul 05, 2025 17:07:38 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import os
import requests
import json

def reverse_image_search(image_path):
    url = "https://serpapi.com/search"
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY environment variable not set")

    with open(image_path, "rb") as image_file:
        files = {
            'image': (image_path, image_file, 'image/jpeg')
        }

        params = {
            "engine": "google_lens",
            "api_key": api_key
        }

        print("Uploading image to SerpApi...")
        response = requests.post(url, params=params, files=files)

    if response.status_code == 200:
        data = response.json()
        if 'visual_matches' in data:
            print("\n🔍 Visual Matches:")
            for match in data['visual_matches'][:5]:  # Top 5 matches
                print(f"- Title: {match.get('title')}")
                print(f"  Link: {match.get('link')}")
        else:
            print("No visual matches found.")
    else:
        print("Request failed:", response.status_code, response.text)

# Example usage
reverse_image_search("path/to/image.jpg")
