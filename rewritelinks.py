#!/usr/bin/env python3
import sys
import re
from pathlib import Path
import shutil
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="config.env")
# Base GitHub raw URL to be replaced
URL_BASE = "https://raw.githubusercontent.com/{user}/{repo}/refs/heads/main/"
user = str(os.getenv("REPO_OWNER"))
repo = str(os.getenv("REPO_NAME"))

URL_BASE = URL_BASE.replace("{user}", user).replace("{repo}",repo)
# Output prefix for relative links
RELATIVE_PREFIX = "_static/images/"

# Regex pattern to match and capture everything after the base URL
pattern = re.compile(re.escape(URL_BASE) + r"([^)]+)")

def rewrite(md_file: Path):
    if not md_file.is_file():
        print(f"❌ Not found or not a file: {md_file}")
        return

    # Replace URLs with prefixed relative links
    original = md_file.read_text()
    modified = pattern.sub(RELATIVE_PREFIX + r"\1", original)

    if original != modified:
        md_file.write_text(modified)
        print(f"✅ Updated: {md_file}")
    else:
        print(f"➖ No changes: {md_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python rewrite_links.py file1.md file2.md ...")
        return

    for arg in sys.argv[1:]:
        rewrite(Path(arg))

if __name__ == "__main__":
    main()
