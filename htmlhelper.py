import re
from urllib.parse import urlparse
import os
from typing import Optional

from configenv import ConfigEnv
from configconstants import ConfigConstants
from loggerutil import LoggerFactory

config = ConfigEnv("config.env")
logger = LoggerFactory.get_logger(
    name=os.path.basename(__file__),
    log_to_file=config.get(ConfigConstants.LOGGING, False)
)

def clean_filename(filename: str) -> str:
    # Remove "File:" prefix and file extension
    base = os.path.splitext(filename.replace("File:", "", 1))[0]
    # Remove commas, semicolons, and parentheses
    base = re.sub(r"[(),;]", "", base)
    # Replace multiple spaces or underscores with a single space
    base = re.sub(r"[_\s]+", " ", base).strip()
    return base


def strip_span_tags_but_keep_contents(text: str) -> str:
    """Remove HTML span tags while preserving their contents.

    Args:
        text: String containing HTML with span tags

    Returns:
        String with span tags removed but contents preserved
    """
    # Remove opening <span ...> tag
    text = re.sub(r'<span[^>]*?>', '', text)
    # Remove closing </span> tag
    text = re.sub(r'</span>', '', text)
    return text

def clean_filename_text(url: str) -> str:
    """Clean text from URLs to create safe filenames.

    Args:
        url: URL string to extract filename from

    Returns:
        Cleaned string with only alphabetic characters and spaces
    """
    # Extract the filename part from the URL
    filename = url.rsplit('/', 1)[-1]
    # Remove extension
    filename = filename.rsplit('.', 1)[0]
    # Remove non-alphabet characters, replace with space
    cleaned = re.sub(r'[^A-Za-z]+', ' ', filename)
    # Strip leading/trailing whitespace and normalize spaces
    return cleaned.strip()

def extract_domain_from_url(url: Optional[str]) -> Optional[str]:
    """Extract domain from url.

    Args:
        url: URL string to extract domain from

    Returns:
        Domain
    """
    if not url:
        return None

    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    return domain
