#!/usr/bin/env python
"""
Gensitemap.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : gensitemap
# @created     : Monday Jul 21, 2025 11:11:52 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

BASE_URL = "https://riay.readthedocs.io/"
visited = set()
sitemap_urls = []

def crawl(url):
    if url in visited or not url.startswith(BASE_URL):
        return
    print(f"Crawling: {url}")
    visited.add(url)
    sitemap_urls.append(url)

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            return
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            abs_url = urljoin(url, link["href"])
            abs_url = abs_url.split("#")[0]  # Remove anchor fragments
            if urlparse(abs_url).netloc == urlparse(BASE_URL).netloc:
                crawl(abs_url)
                time.sleep(0.5)  # Be polite
    except requests.RequestException:
        pass

crawl(BASE_URL)

# Write sitemap
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for url in sorted(sitemap_urls):
        f.write(f"  <url><loc>{url}</loc></url>\n")
    f.write('</urlset>')
