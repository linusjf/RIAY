# docs/strip_toc.py
import re
from pathlib import Path

toc_pattern = re.compile(r"<!-- toc -->.*?<!-- tocstop -->", flags=re.DOTALL)

def strip_toc_blocks(directory="."):
    for md_file in Path(directory).rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        new_text = toc_pattern.sub("", text)
        if new_text != text:
            print(f"Stripped ToC from: {md_file}")
            md_file.write_text(new_text, encoding="utf-8")

if __name__ == "__main__":
    strip_toc_blocks()
