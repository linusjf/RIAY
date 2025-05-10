#!/usr/bin/env python3
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="config.env")

# Base GitHub raw URL to be replaced
URL_BASE = "https://raw.githubusercontent.com/{user}/{repo}/refs/heads/main/"
user = str(os.getenv("REPO_OWNER"))
repo = str(os.getenv("REPO_NAME"))

URL_BASE = URL_BASE.replace("{user}", user).replace("{repo}", repo)

# Regex pattern to match and capture everything after the base URL
pattern = re.compile(re.escape(URL_BASE) + r"([^)]+)")

def get_relative_prefix(file_path: str) -> str:
    if file_path.endswith(".jpg"):
        return "_static/images/"
    elif file_path.endswith(".pdf"):
        return "_static/pdfs/"
    else:
        return "_static/others/"

def rewrite(md_file: Path):
    if not md_file.is_file():
        print(f"❌ Not found or not a file: {md_file}")
        return

    original = md_file.read_text()
    count = 0  # Counter for replacements

    def replacement(match: re.Match) -> str:
        nonlocal count
        count += 1
        file_path = match.group(1)
        return get_relative_prefix(file_path) + file_path

    modified = pattern.sub(replacement, original)

    if count > 0:
        md_file.write_text(modified)
        print(f"✅ Updated: {md_file} ({count} link{'s' if count != 1 else ''} modified)")
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
