"""Helper functions for creating and managing HTTP sessions."""

import random
import requests
from requests.adapters import HTTPAdapter
from requests import Session
from urllib3.util.retry import Retry
from typing import Optional, Sequence

def create_session_with_retries(
    retries: int = 5,
    backoff_factor: float = 1,
    status_forcelist: Sequence[int] = (403, 408, 429, 500, 502, 503, 504),
    session: Optional[Session] = None
) -> Session:
    """Create a requests session with retry logic.

    Args:
        retries: Maximum number of retries
        backoff_factor: Base multiplier for exponential backoff
        status_forcelist: HTTP status codes to force retry on
        session: Existing session to configure (creates new if None)

    Returns:
        Configured Session object with retry logic
    """
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

def exponential_backoff_with_jitter(
    base: float = 1.0,
    cap: float = 60.0,
    attempt: int = 1
) -> float:
    """Calculate exponential backoff with jitter.

    Args:
        base: Base backoff time in seconds
        cap: Maximum backoff time in seconds
        attempt: Current attempt number (1-based)

    Returns:
        Calculated backoff time with jitter in seconds
    """
    backoff = min(cap, base * (2 ** attempt))
    jitter = random.uniform(0, backoff)
    return jitter
