#!/usr/bin/env python
"""
Sphinxsitemapgenerator.

######################################################################
# @author      : Linus Fernandes (linusfernandes at gmail dot com)
# @file        : sphinxsitemapgenerator
# @created     : Monday Jul 21, 2025 11:24:48 IST
# @description :
# -*- coding: utf-8 -*-'
######################################################################
"""
from urllib.parse import urljoin
from datetime import datetime, timezone
from pathlib import Path

def generate_sitemap(app, exception):
    if exception is not None:
        return

    base_url = app.config.html_baseurl
    if not base_url:
        app.warn("html_baseurl is not set; skipping sitemap.xml generation.")
        return

    builder = app.builder
    outdir = Path(builder.outdir)  # Use pathlib.Path
    pages = builder.env.found_docs

    sitemap_path = outdir / "sitemap.xml"
    with sitemap_path.open("w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for page in sorted(pages):
            if page.endswith("genindex") or page.endswith("search"):
                continue
            loc = urljoin(base_url + "/", page + ".html")
            lastmod = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            f.write(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod></url>\n")
        f.write("</urlset>\n")

def setup(app):
    app.connect("build-finished", generate_sitemap)
