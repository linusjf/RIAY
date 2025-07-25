# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import codecs
import logging
import sys
from typing import Dict, Any, List, Union, Optional
from pathlib import Path
from sphinx.application import Sphinx

# Set up logging to redirect stderr to logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stderr.log'),
        logging.StreamHandler(sys.stdout)  # Keep stdout as is
    ]
)
logger = logging.getLogger(__name__)

# Redirect stderr to logger
class StreamToLogger:
    def __init__(self, logger, log_level=logging.ERROR):
        self.logger = logger
        self.log_level = log_level

    def write(self, message):
        if message.rstrip():
            self.logger.log(self.log_level, message.rstrip())

    def flush(self):
        pass

sys.stderr = StreamToLogger(logger, logging.ERROR)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project: str = "RIAY"
copyright: str = "Compiled by Linus Fernandes"
author: str = "Linus Fernandes"
version: str = "1"
language: str = "English"

release: str = os.environ.get("READTHEDOCS_VERSION", "latest")
master_doc: str = "index"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions: List[str] = [
    "myst_parser",
    "sphinxcontrib.cairosvgconverter",
    "sphinx_rtd_dark_mode",
    "sphinx_rtd_theme",
]

# Absolute site URL
html_baseurl: str = "https://riay.readthedocs.io/en/latest"

# Load the extension
import os, sys
sys.path.append(os.path.abspath("."))  # or wherever the script is
extensions.append("sphinxsitemapgenerator")

templates_path: List[str] = ["_templates"]

include_patterns: List[str] = ["index.rst", "*.md", "*/*.jpg", "*/*.pdf"]

exclude_patterns: List[str] = [
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
    "TODO.md",
    "SCRIPTS.md",
    "scripts.md",
    "addimgtoday.md",
    "addsnippets.md"
]

suppress_warnings: List[str] = [
    "toc.not_included",
    "myst.xref_missing",
    "image/svg+xml",
    "epub.unknown_project_files",
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# Add paths for custom static files
html_static_path: List[str] = ["_static"]
html_extra_path: List[str] = ["robots.txt"]
html_show_copyright: bool = False
html_show_sphinx: bool = False
html_theme: str = "sphinx_rtd_theme"
html_split_index: bool = True
html_last_updated_use_utc: bool = True

# user starts in dark mode
default_dark_mode: bool = True

# -- Options for PDF output
latex_engine: str = "lualatex"

latex_show_urls: str = "inline"

latex_elements: Dict[str, str] = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    "fontpkg": r"""
        \usepackage{fontspec}
    """,
    "preamble": r"""
\pdfminorversion=7
\setmainfont{Symbola}
""",
}

# -- Options for EPUB output -------------------------------------------------
epub_show_urls: str = 'inline'  # or 'no', 'footnote'
epub_author: str = author
epub_publisher: str = 'Linus Fernandes'
epub_copyright: str = copyright
epub_title: str = project
epub_description: str = "Rosary in a Year"
epub_scheme: str = "URL"
epub_identifier: str = 'https://github.com/linusjf/RIAY'  # Should be a unique URI
epub_uid: str = 'riay'  # Unique ID for EPUB file
epub_cover: tuple[str, str] = ('_static/cover.jpg', '')
epub_exclude_files: List[str] = ["_static/*.pdf"]

# -- Options for linkcheck
# seconds
linkcheck_timeout: int = 20

linkcheck_anchors: bool = False

linkcheck_report_timeouts_as_broken: bool = False

linkcheck_ignore: List[str] = [
    r"http://localhost:\d+/",  # Ignore local dev servers
    r"https://example\.com/redirect",  # Ignore known redirect
    r"https://www.gnu.org/software/m4/m4.html",
    r"https://4.bp.blogspot.com/-ujfCtTV6yhs/VI1NW92kIBI/AAAAAAAAJBo/aFOIoUu7aqs/s1600/Annunciation_Prado_ca.+1426.jpg",
    r"https://www.museodelprado.es/en/the-collection/art-work/agony-in-the-garden/323edcfd-701e-403f-b27a-9c9d5c656e58",
    r"https://www.dreamstime.com/stock-photo-rome-italy-fresco-assumption-virgin-mary-main-cupola-chiesa-di-santa-maria-del-orto-march-giuseppe-image68702725",
    r"https://carlbloch.org/media//b/a/base_41135642.jpg?width=600"
]

linkcheck_ignore_redirects: bool = True

linkcheck_workers: int = 1

linkcheck_retries: int = 1


def replace_emojis_in_file(file_path: Union[str, Path]) -> None:
    """Replace unsupported emojis in a file with alternatives.

    Args:
        file_path: Path to file to process
    """
    replacements: Dict[str, str] = {
        "🥹": "😢",
        "🥰": "😍",
    }

    try:
        with codecs.open(str(file_path), "r", encoding="utf-8") as file:
            content: str = file.read()

        original_content: str = content
        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original_content:
            with codecs.open(str(file_path), "w", encoding="utf-8") as file:
                file.write(content)
            logger.info(f"Updated: {file_path}")
    except Exception as error:
        logger.error(f"Error processing {file_path}: {error}")


def replace_emojis_in_markdown() -> None:
    """Find and replace emojis in all markdown files."""
    filename: Optional[str] = None
    dirpath: Optional[str] = None
    _: List[str]
    filenames: List[str]
    for dirpath, _, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".md"):
                replace_emojis_in_file(os.path.join(dirpath, filename))


def run_only_for_pdf(app: Sphinx) -> None:
    """Run emoji replacement only for PDF builds.

    Args:
        app: Sphinx application object
    """
    if app.builder.name == "latex":
        logger.info("Running emoji replacement for PDF build...")
        replace_emojis_in_markdown()


def setup(app: Sphinx) -> Dict[str, Any]:
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
