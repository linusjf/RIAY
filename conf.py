# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import codecs
from typing import Dict, Any

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "RIAY"
copyright = "Compiled by Linus Fernandes"
author = "Linus Fernandes"
version = "1"
language = "English"

release = os.environ.get("READTHEDOCS_VERSION", "latest")
master_doc = "index"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "myst_parser",
    "sphinxcontrib.cairosvgconverter",
    "sphinx_rtd_dark_mode",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]

include_patterns = ["index.rst", "*.md", "*/*.jpg", "*/*.pdf"]

exclude_patterns = [
    "stitch.md",
    "January/*.md",
    "February/*.md",
    "March/*.md",
    "April/*.md",
    "May/*.md",
    "June/*.md",
    "July/*.md",
    "August/*.md",
    "September/*.md",
    "October/*.md",
    "November/*.md",
    "December/*.md",
    "README.md",
    "Conventions/*.md",
    ".aider.chat*",
]

suppress_warnings = [
    "toc.not_included",
    "myst.xref_missing",
    "image/svg+xml",
    "epub.unknown_project_files",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# Add paths for custom static files
html_static_path = ["_static"]
html_show_copyright = False
html_theme = "sphinx_rtd_theme"
html_split_index = True
html_last_updated_use_utc = True

# user starts in dark mode
default_dark_mode = True

# -- Options for PDF output
latex_engine = "lualatex"

latex_show_urls = "inline"

latex_elements = {
    "fontpkg": r"""
        \usepackage{fontspec}
    """,
    "preamble": r"""
\pdfminorversion=7
\setmainfont{Symbola}
""",
}

# -- Options for EPUB output -------------------------------------------------
epub_show_urls = 'inline'  # or 'no', 'footnote'
epub_author = author
epub_publisher = 'Linus Fernandes'
epub_copyright = copyright
epub_title = project
epub_identifier = 'https://github.com/linusjf/RIAY'  # Should be a unique URI
epub_uid = 'riay'  # Unique ID for EPUB file
epub_cover = ('_static/cover.jpg', '')
epub_exclude_files = ["_static/*.pdf"]

# -- Options for linkcheck
# seconds
linkcheck_timeout = 30

linkcheck_anchors = False

linkcheck_report_timeouts_as_broken = True

linkcheck_ignore = [
    r"http://localhost:\d+/",  # Ignore local dev servers
    r"https://example\.com/redirect",  # Ignore known redirect
    r"https://www.gnu.org/software/m4/m4.html",
]

linkcheck_ignore_redirects = True

linkcheck_workers = 1

linkcheck_retries = 1


def replace_emojis_in_file(file_path: str) -> None:
    """Replace unsupported emojis in a file with alternatives.

    Args:
        file_path: Path to file to process
    """
    replacements = {
        "🥹": "😢",
        "🥰": "😍",
    }

    try:
        with codecs.open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        original_content = content
        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original_content:
            with codecs.open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"Updated: {file_path}")
    except Exception as error:
        print(f"Error processing {file_path}: {error}")


def replace_emojis_in_markdown() -> None:
    """Find and replace emojis in all markdown files."""
    for dirpath, _, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".md"):
                replace_emojis_in_file(os.path.join(dirpath, filename))


def run_only_for_pdf(app) -> None:
    """Run emoji replacement only for PDF builds.

    Args:
        app: Sphinx application object
    """
    if app.builder.name == "latex":
        print("Running emoji replacement for PDF build...")
        replace_emojis_in_markdown()


def setup(app) -> Dict[str, Any]:
    """Set up Sphinx extensions and callbacks.

    Args:
        app: Sphinx application object

    Returns:
        Dictionary of metadata for Sphinx
    """
    app.add_css_file("custom.css")
    app.connect("builder-inited", run_only_for_pdf)
    return {
        "version": version,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
