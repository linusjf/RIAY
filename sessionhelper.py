"""Helper functions for creating and managing HTTP sessions."""

import random
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries(
    retries=5,
    backoff_factor=1,
    status_forcelist=(403, 408, 429, 500, 502, 503, 504),
    session=None
):
    """Create a requests session with retry logic."""
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        raise_on_status=False,
        respect_retry_after_header=True,
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def exponential_backoff_with_jitter(base=1.0, cap=60.0, attempt=1):
    """Calculate exponential backoff with jitter."""
    backoff = min(cap, base * (2 ** attempt))
    jitter = random.uniform(0, backoff)
    return jitter
